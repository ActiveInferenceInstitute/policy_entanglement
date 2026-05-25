"""Emit a Lean *typed-structure contract* from a parsed GNN model (path d).

This is the "GNN -> Lean elaboration" scoped in S08: a GNN source elaborates to
a Lean ``structure`` whose fields mirror the manuscript symbol concordance
(per-stream habit priors ``E^k``, cross-stream coupling ``J``, deformation
``lambda``, sophistication ``gamma``).

**Explicit non-claim (ISA ISC-32/65/66, S08 "parsing is not proving").**  The
emitted Lean is a *typed contract*, not a proof.  Type-checking the emitted
structure certifies the model's structural signature; it does **not** establish
any analytic content, and it does **not** promote any registry row to
``proved`` or ``witness``.  The emitted file is self-contained core Lean 4
(``Bool``/``Float``/``Nat``/``structure``/``def``) — Mathlib-free, project-import
free — so it type-checks on the stock toolchain the boundary fragment pins.
"""

from __future__ import annotations

import numpy as np

from gnn.bridge import per_stream_priors, stream_cardinality
from gnn.model import GnnModel


def _lean_float(x: float) -> str:
    """Format a Python float as a Lean ``Float`` literal (parenthesized if negative).

    ``repr`` of any finite float yields a Lean-parseable literal (``0.5``,
    ``-0.5``, ``0.0``, ``2.0``); negatives are parenthesized for use in match arms.
    """
    s = repr(float(x))
    return f"({s})" if float(x) < 0 else s


def _bool_arg(i: int) -> str:
    """Map a 0/1 action index to a Lean ``Bool`` literal."""
    return "false" if i == 0 else "true"


def _emit_binary_fn1(name: str, vec: np.ndarray) -> str:
    """Emit a ``Bool -> Float`` function body from a length-2 vector."""
    arms = "\n".join(f"  | {_bool_arg(i)} => {_lean_float(float(vec[i]))}" for i in range(2))
    return f"def {name} : Bool → Float := fun a =>\n  match a with\n{arms}"


def _emit_binary_fn2(name: str, mat: np.ndarray) -> str:
    """Emit a ``Bool -> Bool -> Float`` function body from a 2x2 matrix."""
    arms = "\n".join(
        f"  | {_bool_arg(i)}, {_bool_arg(j)} => {_lean_float(float(mat[i, j]))}"
        for i in range(2)
        for j in range(2)
    )
    return f"def {name} : Bool → Bool → Float := fun a b =>\n  match a, b with\n{arms}"


def emit_lean_structure(model: GnnModel, *, namespace: str = "GnnGenerated") -> str:
    """Emit a self-contained Lean typed-structure contract for a K=2 GNN model.

    Args:
        model: A parsed K=2 policy-entanglement GNN model.
        namespace: Lean namespace for the emitted declarations.

    Returns:
        Lean 4 source text (Mathlib-free, self-contained).

    Raises:
        ValueError: if the model is not the K=2 binary form this emitter targets.
    """
    k = model.num_streams
    card = stream_cardinality(model)
    if k != 2 or card != 2:
        raise ValueError(
            f"emit_lean_structure targets the K=2 binary contract; got K={k}, cardinality={card}"
        )
    priors = per_stream_priors(model)
    coupling = model.variable("J").matrix()
    lam = model.variable("lam").scalar() if model.has("lam") else 0.0
    gamma = model.variable("gamma").scalar() if model.has("gamma") else 0.0

    ident = model.section.replace(" ", "_")
    return f"""\
/- GENERATED — DO NOT EDIT BY HAND.
   Emitted by `src/gnn/lean_emit.py` from a GNN v1.1 source file
   (`gnn/bernoulli_toy.gnn.md`, section {model.section!r}).

   This is a TYPED CONTRACT, not a proof.  Type-checking this file certifies the
   structural signature of the GNN-specified policy-entanglement model; it does
   NOT establish any analytic content and does NOT promote any registry row to
   `proved`/`witness`.  Self-contained core Lean 4 (Mathlib-free) so it
   type-checks on the stock toolchain the boundary fragment pins. -/

namespace {namespace}

/-- A binary policy stream's habit prior: a probability per action `{{0,1}}`. -/
abbrev StreamPrior := Bool → Float

/-- A cross-stream coupling potential over the joint policy space `{{0,1}}²`. -/
abbrev Coupling2 := Bool → Bool → Float

/-- Typed contract for a K=2 policy-entanglement GNN model.  Field names mirror
    the manuscript symbol concordance (E^k, J, λ, γ). -/
structure PolicyEntanglementK2 where
  numStreams  : Nat
  cardinality : Nat
  habitPrior1 : StreamPrior
  habitPrior2 : StreamPrior
  coupling    : Coupling2
  lambda      : Float
  gamma       : Float

{_emit_binary_fn1("habitPrior1_" + ident, priors[0])}

{_emit_binary_fn1("habitPrior2_" + ident, priors[1])}

{_emit_binary_fn2("coupling_" + ident, coupling)}

/-- The model emitted from the GNN source. -/
def {ident} : PolicyEntanglementK2 where
  numStreams  := {k}
  cardinality := {card}
  habitPrior1 := habitPrior1_{ident}
  habitPrior2 := habitPrior2_{ident}
  coupling    := coupling_{ident}
  lambda      := {_lean_float(lam)}
  gamma       := {_lean_float(gamma)}

/-- Structural sanity (typed contract, not an analytic proof): the emitted
    model declares two binary streams at the GNN-specified cardinality. -/
example : {ident}.numStreams = 2 := rfl
example : {ident}.cardinality = 2 := rfl

end {namespace}
"""
