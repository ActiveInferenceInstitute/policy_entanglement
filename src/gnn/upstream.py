"""Upstream-conformance support for the project-owned GNN parser.

The project-owned parser (:mod:`gnn.parser`) is cited-not-vendored: it
implements the GNN v1.1 grammar independently and never imports upstream
code.  This module makes that claim checkable.  It normalizes the project
parser's output into a comparable digest and compares that digest against the
digest emitted by the real upstream parser
(``gnn.parsers.markdown_parser.MarkdownGNNParser``) when it is executed
against the pinned upstream tree.

Reading and validating the pin is not this module's job.  The
[GNN–FEP contract](https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation/blob/main/docs/workflows/gnn-fep.md)
gives pin reading, pin/pointer validation and specification validation one
home: ``python -m gnn.importers``, which the ``gnn`` arm runs from the pinned
release's own environment.  The arm reads ``gnn/upstream.json`` once and hands
the selected release to the conformance test through
:data:`ENV_PINNED_RELEASE`; :func:`pinned_release` reads that hand-off.

Nothing here imports upstream GNN code (and nothing under ``src/`` ever
should).  :data:`DIGEST_DRIVER_SOURCE` is a stdlib-only program that
``tests/test_gnn_upstream_conformance.py`` runs with the GNN checkout's own
interpreter, with the pinned commit's ``src/gnn`` extracted onto
``PYTHONPATH`` — so the bytes under test are the pinned release's bytes, not
the live working tree's.  The comparison functions
(:func:`spec_digest`, :func:`normalize_upstream_digest`,
:func:`digest_divergences`) are pure and exercised in-process.
"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from pathlib import Path

import numpy as np

from gnn.model import GnnModel

#: Conventional directory name of the sibling upstream checkout.
DEFAULT_UPSTREAM_DIRNAME = "Generalized_Notation_Notation"
#: Explicit checkout selection; when set it is final (empty values are refused).
ENV_UPSTREAM_ROOT = "POLICY_ENTANGLEMENT_GNN_ROOT"
#: Checkout-relative path of the upstream markdown parser module.
PARSER_RELATIVE_PATH = "src/gnn/parsers/markdown_parser.py"
#: Environment variable carrying the release the ``gnn`` arm selected.
ENV_PINNED_RELEASE = "POLICY_ENTANGLEMENT_GNN_RELEASE"

_DTYPE_ALIASES = {"integer": "int", "boolean": "bool", "string": "str"}


class UpstreamConformanceError(ValueError):
    """Raised when upstream conformance cannot be decided from the inputs at hand."""


@dataclass(frozen=True)
class PinnedRelease:
    """The upstream release the ``gnn`` arm selected, as the test must exercise it.

    The arm reads ``gnn/upstream.json`` once and publishes this record through
    :data:`ENV_PINNED_RELEASE`; ``python -m gnn.importers`` validates the pin,
    the pointer and the specifications in the pinned release's own
    environment.  The record therefore carries only what selecting the
    revision and running its parser needs — it is the arm's hand-off, not a
    second pin reader.

    Attributes:
        repository: Upstream repository URL, as the pin records it.
        tag: Release tag the pin records.
        commit: Full commit identity the tag resolves to.
        parser_module: Dotted import path of the upstream parser module.
        parser_class: Parser class name inside ``parser_module``.
    """

    repository: str
    tag: str
    commit: str
    parser_module: str
    parser_class: str


def pinned_release(env: Mapping[str, str] | None = None) -> PinnedRelease:
    """Read the pinned-release record the ``gnn`` arm exports.

    Raises:
        UpstreamConformanceError: when the record is absent or incomplete,
            which means the caller is not running inside the ``gnn`` arm.
    """
    payload = (os.environ if env is None else env).get(ENV_PINNED_RELEASE, "")
    if not payload.strip():
        raise UpstreamConformanceError(
            f"{ENV_PINNED_RELEASE} is unset; run the conformance check through the gate arm "
            "(`python scripts/gate.py gnn`) so the shared GNN-FEP reader has read the pin"
        )
    try:
        data = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise UpstreamConformanceError(f"{ENV_PINNED_RELEASE} is not JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise UpstreamConformanceError(f"{ENV_PINNED_RELEASE} must be a JSON object")
    missing = [
        field.name
        for field in fields(PinnedRelease)
        if not isinstance(data.get(field.name), str) or not data[field.name].strip()
    ]
    if missing:
        raise UpstreamConformanceError(f"{ENV_PINNED_RELEASE} records no {', '.join(missing)}")
    return PinnedRelease(
        repository=data["repository"].strip(),
        tag=data["tag"].strip(),
        commit=data["commit"].strip(),
        parser_module=data["parser_module"].strip(),
        parser_class=data["parser_class"].strip(),
    )


def default_gnn_root(project_root: Path) -> Path:
    """The conventional sibling checkout of the upstream GNN repository."""
    return (Path(project_root).parent / DEFAULT_UPSTREAM_DIRNAME).resolve()


def resolve_gnn_root(project_root: Path, env: Mapping[str, str] | None = None) -> Path:
    """Resolve the upstream checkout root.

    An explicit :data:`ENV_UPSTREAM_ROOT` selection is final, including refusal
    of an empty value; otherwise the conventional sibling checkout is used.

    Raises:
        UpstreamConformanceError: if the environment selection is set but empty.
    """
    environ = os.environ if env is None else env
    if ENV_UPSTREAM_ROOT in environ:
        raw = environ[ENV_UPSTREAM_ROOT].strip()
        if not raw:
            raise UpstreamConformanceError(f"{ENV_UPSTREAM_ROOT} must not be empty")
        return Path(raw).expanduser().resolve()
    return default_gnn_root(project_root)


def gnn_checkout_python(root: Path) -> Path:
    """The checkout-local interpreter used to execute the pinned parser."""
    return Path(root) / ".venv" / "bin" / "python"


def checkout_available(root: Path) -> bool:
    """Whether the checkout supplies both the upstream parser source and its interpreter."""
    return (Path(root) / PARSER_RELATIVE_PATH).is_file() and gnn_checkout_python(root).is_file()


def _normalize_version(text: str) -> str:
    """Normalize ``GNN v1.1`` / ``1.1`` / ``v1.1`` to ``1.1``."""
    cleaned = str(text).strip()
    cleaned = re.sub(r"^GNN\s*", "", cleaned)
    return re.sub(r"^v", "", cleaned).strip()


def _normalize_time(text: str) -> str:
    """Classify a ``## Time`` section body the way upstream does.

    Upstream does not keep the section text: it scans the lines and records
    ``Static`` / ``Dynamic`` (later keyword wins, default ``Static``).  The
    digest applies the same rule to the project-parsed body so the two sides
    are compared as classifications rather than raw text.
    """
    kind = "Static"
    for raw_line in str(text).splitlines():
        line = raw_line.strip().lower()
        if "dynamic" in line:
            kind = "Dynamic"
        elif "static" in line:
            kind = "Static"
    return kind


def _normalize_dtype(raw: object) -> str:
    """Normalize a declared dtype (``float`` / ``DataType.FLOAT`` / ``INTEGER``)."""
    text = str(raw).strip().lower()
    if "." in text:
        text = text.rsplit(".", 1)[-1]
    return _DTYPE_ALIASES.get(text, text)


def _normalized_param_text(value: object) -> str:
    """Text-normalize a ModelParameters value (sequences and comma lists included)."""
    if isinstance(value, (list, tuple)):
        return ",".join(_normalized_param_text(item) for item in value)
    text = str(value).strip()
    if "," in text:
        return ",".join(part.strip() for part in text.split(","))
    return text


def _normalized_edges(edges: Sequence[Sequence[object]]) -> Counter[tuple[str, str, str, str]]:
    """Connection edges as comparable 4-tuples, with the direction token lowercased.

    The project parser records the direction as a boolean (``directed`` /
    ``undirected``); upstream records an enum whose value is lowercase but whose
    serialization could be the enum *name*.  Lowercasing keeps the comparison
    about edge semantics rather than serialization style.
    """
    return Counter(
        (str(edge[0]), str(edge[1]), str(edge[2]).strip().lower(), "" if edge[3] is None else str(edge[3]))
        for edge in edges
    )


def spec_digest(model: GnnModel) -> dict[str, object]:
    """Normalize a project-parsed :class:`~gnn.model.GnnModel` into a conformance digest.

    The digest is the comparable projection of a parsed GNN file: model name,
    version, time, declared variables (dims + dtype), connection edges,
    ontology bindings, ``ModelParameters`` entries, and every
    ``InitialParameterization`` value.
    """
    variables = {
        name: {"dims": [int(d) for d in var.dims], "dtype": _normalize_dtype(var.dtype)}
        for name, var in model.variables.items()
    }
    connections = sorted(
        [edge.source, edge.target, "directed" if edge.directed else "undirected", edge.label or ""]
        for edge in model.connections
    )
    parameters = {
        name: np.asarray(var.value, dtype=np.float64).tolist()
        for name, var in model.variables.items()
        if var.value is not None
    }
    return {
        "model_name": model.name.strip(),
        "version": _normalize_version(model.version),
        "time": _normalize_time(model.time),
        "variables": variables,
        "connections": connections,
        "ontology": dict(model.ontology),
        "model_parameters": dict(model.model_parameters),
        "parameters": parameters,
    }


def normalize_upstream_digest(payload: Mapping[str, object]) -> dict[str, object]:
    """Normalize the upstream driver's JSON digest into the project digest shape.

    Raises:
        UpstreamConformanceError: if the payload is missing required digest fields.
    """
    required = (
        "model_name",
        "version",
        "time",
        "variables",
        "connections",
        "ontology",
        "model_parameters",
        "parameters",
    )
    missing = [key for key in required if key not in payload]
    if missing:
        raise UpstreamConformanceError(f"upstream digest is missing fields: {missing}")

    raw_variables = payload["variables"]
    if not isinstance(raw_variables, Sequence):
        raise UpstreamConformanceError("upstream digest 'variables' must be a sequence")
    variables: dict[str, object] = {}
    for entry in raw_variables:
        if not isinstance(entry, Mapping):
            raise UpstreamConformanceError("upstream digest variable entries must be mappings")
        name = str(entry["name"])
        variables[name] = {"dims": [int(d) for d in entry["dims"]], "dtype": _normalize_dtype(entry["dtype"])}

    raw_connections = payload["connections"]
    if not isinstance(raw_connections, Sequence):
        raise UpstreamConformanceError("upstream digest 'connections' must be a sequence")
    connections = sorted(
        [str(edge[0]), str(edge[1]), str(edge[2]), "" if edge[3] is None else str(edge[3])] for edge in raw_connections
    )

    raw_ontology = payload["ontology"]
    if not isinstance(raw_ontology, Sequence):
        raise UpstreamConformanceError("upstream digest 'ontology' must be a sequence")
    ontology = {str(entry["variable"]): str(entry["term"]) for entry in raw_ontology}

    raw_parameters = payload["parameters"]
    raw_model_parameters = payload["model_parameters"]
    if not isinstance(raw_parameters, Mapping) or not isinstance(raw_model_parameters, Mapping):
        raise UpstreamConformanceError("upstream digest 'parameters' / 'model_parameters' must be mappings")

    return {
        "model_name": str(payload["model_name"]).strip(),
        "version": _normalize_version(str(payload["version"])),
        "time": _normalize_time(str(payload["time"])),
        "variables": variables,
        "connections": connections,
        "ontology": ontology,
        "model_parameters": {str(key): value for key, value in raw_model_parameters.items()},
        "parameters": {str(key): value for key, value in raw_parameters.items()},
    }


def _parameters_differ(project_value: object, upstream_value: object) -> bool:
    left = np.asarray(project_value, dtype=np.float64)
    right = np.asarray(upstream_value, dtype=np.float64)
    if left.shape != right.shape:
        return True
    return bool(np.abs(left - right).max() > 0.0) if left.size else False


def _mapping_field(digest: Mapping[str, object], key: str) -> dict[str, object]:
    """Read a digest field that must be a mapping.

    Raises:
        UpstreamConformanceError: if the field is absent-and-not-a-mapping or malformed.
    """
    value = digest.get(key, {})
    if not isinstance(value, Mapping):
        raise UpstreamConformanceError(f"digest field {key!r} must be a mapping, got {type(value).__name__}")
    return dict(value)


def digest_divergences(project: Mapping[str, object], upstream: Mapping[str, object]) -> list[str]:
    """Compare two conformance digests and describe every divergence.

    Returns an empty list when the two digests agree on model name, version,
    time, variables (dims + dtype), connections, ontology bindings,
    ``ModelParameters`` values, and parameterized values.  Any non-empty list
    is a conformance failure.
    """
    issues: list[str] = []
    for field in ("model_name", "version", "time"):
        if project.get(field) != upstream.get(field):
            issues.append(f"{field}: project={project.get(field)!r} upstream={upstream.get(field)!r}")

    project_variables = _mapping_field(project, "variables")
    upstream_variables = _mapping_field(upstream, "variables")
    for name in sorted(set(project_variables) | set(upstream_variables)):
        if name not in project_variables:
            issues.append(f"variables: {name!r} declared upstream only")
        elif name not in upstream_variables:
            issues.append(f"variables: {name!r} declared in the project parser only")
        elif project_variables[name] != upstream_variables[name]:
            issues.append(f"variables[{name!r}]: project={project_variables[name]} upstream={upstream_variables[name]}")

    project_edges = _normalized_edges(project.get("connections", []))  # type: ignore[arg-type]
    upstream_edges = _normalized_edges(upstream.get("connections", []))  # type: ignore[arg-type]
    if project_edges != upstream_edges:
        issues.append(
            "connections differ: project-only "
            f"{sorted((project_edges - upstream_edges).elements())}, upstream-only "
            f"{sorted((upstream_edges - project_edges).elements())}"
        )

    if _mapping_field(project, "ontology") != _mapping_field(upstream, "ontology"):
        issues.append(f"ontology: project={project.get('ontology')!r} upstream={upstream.get('ontology')!r}")

    project_model_parameters = _mapping_field(project, "model_parameters")
    upstream_model_parameters = _mapping_field(upstream, "model_parameters")
    for key in sorted(set(project_model_parameters) | set(upstream_model_parameters)):
        if key not in project_model_parameters:
            issues.append(f"model_parameters: {key!r} present upstream only")
        elif key not in upstream_model_parameters:
            issues.append(f"model_parameters: {key!r} present in the project parser only")
        elif _normalized_param_text(project_model_parameters[key]) != _normalized_param_text(
            upstream_model_parameters[key]
        ):
            issues.append(
                f"model_parameters[{key!r}]: project={project_model_parameters[key]!r} "
                f"upstream={upstream_model_parameters[key]!r}"
            )

    project_parameters = _mapping_field(project, "parameters")
    upstream_parameters = _mapping_field(upstream, "parameters")
    for name in sorted(set(project_parameters) | set(upstream_parameters)):
        if name not in project_parameters:
            issues.append(f"parameters: {name!r} present upstream only")
        elif name not in upstream_parameters:
            issues.append(f"parameters: {name!r} present in the project parser only")
        elif _parameters_differ(project_parameters[name], upstream_parameters[name]):
            issues.append(
                f"parameters[{name!r}]: project={project_parameters[name]!r} upstream={upstream_parameters[name]!r}"
            )
    return issues


#: Stdlib-only driver executed by the *pinned checkout's* interpreter.
#:
#: The conformance test runs this with ``PYTHONPATH`` pointing at the pinned
#: commit's extracted ``src/`` tree, so ``import gnn`` resolves to the pinned
#: release rather than the live working tree.  The driver prints one JSON
#: object: ``{"parser": {...}, "specs": {<path>: <digest>}}``.
DIGEST_DRIVER_SOURCE = r'''
"""Print upstream-parser digests for one or more GNN spec files (stdlib only)."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path


def _to_json(value):
    if isinstance(value, (list, tuple)):
        return [_to_json(item) for item in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _dtype(data_type):
    name = getattr(data_type, "name", None)
    return str(name if name is not None else data_type)


def _digest(result):
    model = result.model
    declared = {variable.name for variable in model.variables}
    parameters = {}
    model_parameters = {}
    for parameter in model.parameters:
        value = _to_json(parameter.value)
        if parameter.name in declared and parameter.name not in parameters:
            parameters[parameter.name] = value
        elif parameter.name not in model_parameters:
            model_parameters[parameter.name] = value
    connections = []
    for connection in model.connections:
        connection_type = str(connection.connection_type).rsplit(".", 1)[-1].lower()
        for source in connection.source_variables:
            for target in connection.target_variables:
                connections.append([source, target, connection_type, connection.annotation or ""])
    return {
        "model_name": model.model_name,
        "version": model.version,
        "time": model.time_specification.time_type if model.time_specification else "",
        "variables": [
            {"name": variable.name, "dims": list(variable.dimensions), "dtype": _dtype(variable.data_type)}
            for variable in model.variables
        ],
        "connections": sorted(connections),
        "ontology": [
            {"variable": mapping.variable_name, "term": mapping.ontology_term}
            for mapping in model.ontology_mappings
        ],
        "parameters": parameters,
        "model_parameters": model_parameters,
        "diagnostics": {
            "success": bool(result.success),
            "errors": [str(error) for error in result.errors],
            "warnings": [str(warning) for warning in result.warnings],
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--module", required=True)
    parser.add_argument("--class-name", required=True, dest="class_name")
    parser.add_argument("--spec", action="append", required=True)
    args = parser.parse_args(argv)

    module = importlib.import_module(args.module)
    parser_class = getattr(module, args.class_name)
    instance = parser_class()

    parser_file = Path(sys.modules[module.__name__].__file__)
    payload = {
        "parser": {
            "module": args.module,
            "class": args.class_name,
            "file": str(parser_file),
            "sha256": hashlib.sha256(parser_file.read_bytes()).hexdigest(),
            "python": sys.version.split()[0],
            "gnn_version": getattr(sys.modules["gnn"], "__version__", None),
        },
        "specs": {},
    }
    for spec in args.spec:
        result = instance.parse_file(spec)
        payload["specs"][str(spec)] = _digest(result)
    json.dump(payload, sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
