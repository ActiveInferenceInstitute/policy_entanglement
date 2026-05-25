"""Generalized Notation Notation (GNN) — the fifth track of the framework.

This package is the project-owned implementation of the GNN bridge scoped in
``manuscript/S08_gnn_generalized_notation_extension.md``.  It parses authentic
GNN v1.1 source files (``gnn/*.gnn.md``), reconstructs the policy-entanglement
mutual-information curve from the GNN-declared coupling (the round-trip), and
emits a Lean typed-structure contract from a GNN model.

Public API:
    * :func:`~gnn.parser.parse_gnn`, :func:`~gnn.parser.parse_gnn_file`,
      :class:`~gnn.parser.GNNParseError`
    * :class:`~gnn.model.GnnModel`, :class:`~gnn.model.GnnVariable`,
      :class:`~gnn.model.GnnConnection`
    * :func:`~gnn.bridge.reconstruct_mi_curve`, :func:`~gnn.bridge.entangled_joint`,
      :func:`~gnn.bridge.build_joint_coupling`, :func:`~gnn.bridge.per_stream_priors`
    * :func:`~gnn.lean_emit.emit_lean_structure`
"""

from __future__ import annotations

from gnn.bridge import (  # noqa: F401
    build_joint_coupling,
    entangled_joint,
    per_stream_priors,
    reconstruct_mi_curve,
)
from gnn.lean_emit import emit_lean_structure  # noqa: F401
from gnn.model import GnnConnection, GnnModel, GnnVariable  # noqa: F401
from gnn.parser import GNNParseError, parse_gnn, parse_gnn_file  # noqa: F401

__all__ = [
    "GNNParseError",
    "GnnConnection",
    "GnnModel",
    "GnnVariable",
    "build_joint_coupling",
    "emit_lean_structure",
    "entangled_joint",
    "parse_gnn",
    "parse_gnn_file",
    "per_stream_priors",
    "reconstruct_mi_curve",
]
