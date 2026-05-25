"""Project-owned, spec-conformant parser for Generalized Notation Notation.

Implements the GNN v1.1 grammar (Smékal & Friedman 2023; grammar at the
upstream repository's ``doc/gnn/gnn_syntax.md``): a GNN file is a UTF-8
Markdown document of ordered ``## Section`` blocks.  The required sections are
``GNNSection``, ``GNNVersionAndFlags``, ``ModelName``, ``StateSpaceBlock``, and
``Connections``; ``InitialParameterization``, ``ActInf Ontology Annotation``,
``ModelParameters``, ``Equations``, ``Time``, and ``ModelAnnotation`` are
optional.

The parser is **project-owned** — it does not import any upstream GNN code (the
upstream repository is CC BY-NC-SA 4.0; it is cited, not vendored).  It is also
**non-vacuous**: it raises :class:`GNNParseError` on a missing required section,
a missing ``type=`` declaration, a named-dimension reference (unsupported here),
and a parameterization whose element count disagrees with the declared
dimensions.  Those raises are exercised as negative controls in
``tests/test_gnn_parser.py``.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import numpy as np

from gnn.model import GnnConnection, GnnModel, GnnVariable

REQUIRED_SECTIONS = (
    "GNNSection",
    "GNNVersionAndFlags",
    "ModelName",
    "StateSpaceBlock",
    "Connections",
)

# A StateSpaceBlock declaration: NAME[dims...] optional trailing # comment.
_DECL_RE = re.compile(r"^(?P<name>[^\s\[]+)\[(?P<body>[^\]]*)\]\s*(?:#\s*(?P<comment>.*))?$")
# A connection edge: A>B or A-B, optionally :label.
_EDGE_RE = re.compile(r"^(?P<src>[^\s>\-]+)\s*(?P<op>[>\-])\s*(?P<dst>[^\s:>\-]+)(?::(?P<label>[\w]+))?$")


class GNNParseError(Exception):
    """Raised on a structural or grammatical GNN parse failure.

    Mirrors the upstream error taxonomy (``GNN-E001`` missing section,
    ``GNN-E002`` dimension mismatch); the message names the offending
    construct so a model author can locate it.
    """


def _split_sections(text: str) -> dict[str, str]:
    """Split a GNN document into ``{section_name: body_text}``.

    Section headers are level-2 Markdown (``## Name``).  Leading ``#`` comment
    lines before the first section header are ignored.  Section names are
    normalized by stripping surrounding whitespace; ``ActInf Ontology
    Annotation`` and ``ActInfOntologyAnnotation`` are both accepted.
    """
    sections: dict[str, str] = {}
    current: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def _section(sections: dict[str, str], *names: str) -> str | None:
    """Return the first present section among ``names`` (alias-tolerant)."""
    for n in names:
        if n in sections:
            return sections[n]
    return None


def _parse_dims_and_type(name: str, body: str) -> tuple[tuple[int, ...], str]:
    """Parse the ``[...]`` body of a declaration into (dims, dtype).

    Raises:
        GNNParseError: on a named-dimension reference (unsupported) or a
            missing required ``type=`` field.
    """
    dims: list[int] = []
    dtype: str | None = None
    for tok in (t.strip() for t in body.split(",")):
        if not tok:
            continue
        if "=" in tok:
            key, _, val = tok.partition("=")
            if key.strip() == "type":
                dtype = val.strip()
            # other key=value hints (default=..., etc.) are preserved-ignored
            continue
        if re.fullmatch(r"\d+", tok):
            dims.append(int(tok))
        else:
            raise GNNParseError(
                f"variable {name!r}: named-dimension reference {tok!r} is not supported "
                f"by this parser; use explicit integer cardinalities"
            )
    if dtype is None:
        raise GNNParseError(f"variable {name!r}: missing required 'type=' declaration")
    if not dims:
        raise GNNParseError(f"variable {name!r}: no integer dimensions declared")
    return tuple(dims), dtype


def _parse_state_space(body: str) -> dict[str, tuple[tuple[int, ...], str, str]]:
    """Parse ``StateSpaceBlock`` into ``{name: (dims, dtype, comment)}``."""
    out: dict[str, tuple[tuple[int, ...], str, str]] = {}
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _DECL_RE.match(line)
        if not m:
            raise GNNParseError(f"malformed StateSpaceBlock declaration: {line!r}")
        name = m.group("name")
        dims, dtype = _parse_dims_and_type(name, m.group("body"))
        out[name] = (dims, dtype, (m.group("comment") or "").strip())
    return out


def _parse_connections(body: str) -> list[GnnConnection]:
    """Parse the ``Connections`` edge list."""
    edges: list[GnnConnection] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        m = _EDGE_RE.match(line)
        if not m:
            raise GNNParseError(f"malformed connection edge: {line!r}")
        edges.append(
            GnnConnection(
                source=m.group("src"),
                target=m.group("dst"),
                directed=(m.group("op") == ">"),
                label=m.group("label"),
            )
        )
    return edges


def _strip_comment_lines(body: str) -> str:
    """Drop whole-line ``#`` comments (keeps numeric content lines)."""
    return "\n".join(ln for ln in body.splitlines() if not ln.strip().startswith("#"))


def _parse_param_blocks(body: str) -> dict[str, np.ndarray]:
    """Parse ``InitialParameterization`` into ``{name: ndarray}``.

    Each block is ``NAME = { ... }`` where the brace body uses parentheses to
    group rows/slices.  Braces and parentheses are mapped to brackets and the
    result is evaluated with :func:`ast.literal_eval` (numeric literals only),
    which handles arbitrary nesting (vectors, matrices, 3-tensors) uniformly.
    """
    text = _strip_comment_lines(body)
    out: dict[str, np.ndarray] = {}
    i = 0
    n = len(text)
    name_re = re.compile(r"([^\s=]+)\s*=\s*\{")
    while i < n:
        m = name_re.search(text, i)
        if not m:
            break
        name = m.group(1)
        # Scan brace-balanced from the opening '{'.
        depth = 0
        j = m.end() - 1  # position of '{'
        start = j
        while j < n:
            ch = text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        if depth != 0:
            raise GNNParseError(f"unbalanced braces in InitialParameterization for {name!r}")
        block = text[start : j + 1]
        literal = block.replace("{", "[").replace("}", "]").replace("(", "[").replace(")", "]")
        try:
            parsed = ast.literal_eval(literal)
        except (ValueError, SyntaxError) as exc:
            raise GNNParseError(f"cannot parse InitialParameterization for {name!r}: {exc}") from exc
        out[name] = np.asarray(parsed, dtype=np.float64)
        i = j + 1
    return out


def _parse_kv(body: str) -> dict[str, str]:
    """Parse ``key: value`` (ModelParameters) or ``key=value`` (Ontology)."""
    out: dict[str, str] = {}
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, _, v = line.partition(":")
        elif "=" in line:
            k, _, v = line.partition("=")
        else:
            continue
        out[k.strip()] = v.strip()
    return out


def parse_gnn(text: str, *, source: str = "<string>") -> GnnModel:
    """Parse GNN source text into a :class:`GnnModel`.

    Args:
        text: The full GNN Markdown document.
        source: A label for error messages (e.g. the file path).

    Raises:
        GNNParseError: on any missing required section or grammatical error.
    """
    sections = _split_sections(text)
    for req in REQUIRED_SECTIONS:
        if req not in sections:
            raise GNNParseError(f"{source}: missing required section '## {req}' (GNN-E001)")

    declarations = _parse_state_space(sections["StateSpaceBlock"])
    params = _parse_param_blocks(sections.get("InitialParameterization", ""))

    variables: dict[str, GnnVariable] = {}
    for name, (dims, dtype, comment) in declarations.items():
        value = params.get(name)
        var = GnnVariable(name=name, dims=dims, dtype=dtype, comment=comment, value=value)
        if value is not None and value.size != var.size:
            raise GNNParseError(
                f"{source}: variable {name!r} declared dims {dims} (size {var.size}) "
                f"but InitialParameterization has {value.size} elements (GNN-E002)"
            )
        variables[name] = var

    ontology = _parse_kv(_section(sections, "ActInf Ontology Annotation", "ActInfOntologyAnnotation") or "")
    model_parameters = _parse_kv(sections.get("ModelParameters", ""))
    equations = [ln for ln in sections.get("Equations", "").splitlines() if ln.strip()]

    return GnnModel(
        section=sections["GNNSection"].strip(),
        version=sections["GNNVersionAndFlags"].strip(),
        name=sections["ModelName"].strip(),
        variables=variables,
        connections=_parse_connections(sections["Connections"]),
        ontology=ontology,
        model_parameters=model_parameters,
        annotation=sections.get("ModelAnnotation", ""),
        equations=equations,
        time=sections.get("Time", "").strip(),
    )


def parse_gnn_file(path: str | Path) -> GnnModel:
    """Read and parse a ``.gnn.md`` file from disk."""
    p = Path(path)
    return parse_gnn(p.read_text(encoding="utf-8"), source=str(p))
