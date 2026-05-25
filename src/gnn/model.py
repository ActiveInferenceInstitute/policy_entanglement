"""Typed model objects for the Generalized Notation Notation (GNN) fifth track.

These dataclasses are the parsed, in-memory representation of a GNN source
file (see :mod:`gnn.parser`).  They are deliberately framework-agnostic: a
:class:`GnnModel` knows about GNN sections, variable declarations, connection
edges, and initial parameterization, but knows *nothing* about the
policy-entanglement framework's :func:`entangled_posterior` /
:func:`total_correlation` machinery.  The binding from a parsed model to the
framework lives in :mod:`gnn.bridge`; the binding to Lean lives in
:mod:`gnn.lean_emit`.

GNN is the notation introduced by Smékal & Friedman (2023); this module
implements the v1.1 grammar documented at the upstream repository's
``doc/gnn/gnn_syntax.md``.  No upstream GNN code is imported — the parser is
project-owned and spec-conformant (the upstream repository is CC BY-NC-SA 4.0;
it is cited, not vendored).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

ArrayF = NDArray[np.float64]


@dataclass(frozen=True)
class GnnVariable:
    """One ``StateSpaceBlock`` declaration, e.g. ``J[2,2,type=float]``.

    Attributes:
        name: The variable identifier (``J``, ``pi1``, ``lam``, ...).
        dims: Declared dimensions as a tuple of positive ints.
        dtype: The declared ``type=`` value (``float``, ``int``, ``bool``).
        comment: Trailing inline comment, if any.
        value: The parsed ``InitialParameterization`` tensor, if the file
            supplied one for this variable; otherwise ``None``.
    """

    name: str
    dims: tuple[int, ...]
    dtype: str
    comment: str = ""
    value: ArrayF | None = None

    @property
    def size(self) -> int:
        """Total declared element count (product of dims)."""
        n = 1
        for d in self.dims:
            n *= d
        return n

    def matrix(self) -> ArrayF:
        """Return the parameterized value reshaped to the declared dims.

        Raises:
            ValueError: if no value was parameterized for this variable.
        """
        if self.value is None:
            raise ValueError(f"variable {self.name!r} has no InitialParameterization")
        return np.asarray(self.value, dtype=np.float64).reshape(self.dims)

    def vector(self) -> ArrayF:
        """Return the parameterized value flattened to 1-D (for priors)."""
        if self.value is None:
            raise ValueError(f"variable {self.name!r} has no InitialParameterization")
        return np.asarray(self.value, dtype=np.float64).reshape(-1)

    def scalar(self) -> float:
        """Return the parameterized value as a Python float (size-1 only)."""
        v = self.vector()
        if v.size != 1:
            raise ValueError(f"variable {self.name!r} is not a scalar (size {v.size})")
        return float(v[0])


@dataclass(frozen=True)
class GnnConnection:
    """One ``Connections`` edge, e.g. ``pi1-J:cross_stream_coupling``.

    Attributes:
        source: Left-hand variable name.
        target: Right-hand variable name.
        directed: ``True`` for ``A>B`` (causal), ``False`` for ``A-B``.
        label: Optional ``:label`` annotation (v1.1), else ``None``.
    """

    source: str
    target: str
    directed: bool
    label: str | None = None


@dataclass
class GnnModel:
    """A fully parsed GNN model.

    The model is the single declarative surface from which the GNN "Triple
    Play" (linguistic / visual / executable views) is emitted.  In this
    project the executable view is realized by :mod:`gnn.bridge`.
    """

    section: str
    version: str
    name: str
    variables: dict[str, GnnVariable] = field(default_factory=dict)
    connections: list[GnnConnection] = field(default_factory=list)
    ontology: dict[str, str] = field(default_factory=dict)
    model_parameters: dict[str, str] = field(default_factory=dict)
    annotation: str = ""
    equations: list[str] = field(default_factory=list)
    time: str = ""

    def variable(self, name: str) -> GnnVariable:
        """Look up a declared variable by name.

        Raises:
            KeyError: if no variable with that name was declared.
        """
        if name not in self.variables:
            raise KeyError(f"GNN model {self.section!r} declares no variable {name!r}")
        return self.variables[name]

    def has(self, name: str) -> bool:
        """Whether a variable was declared."""
        return name in self.variables

    def edges_for(self, name: str) -> list[GnnConnection]:
        """All connection edges touching the named variable."""
        return [c for c in self.connections if c.source == name or c.target == name]

    @property
    def num_streams(self) -> int:
        """Number of policy streams declared as ``pi1, pi2, ...``."""
        k = 0
        while f"pi{k + 1}" in self.variables:
            k += 1
        return k
