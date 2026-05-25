"""GNN -> policy-entanglement framework binding (the executable Triple-Play view).

This module realizes the "executable view" of the GNN Triple Play for the
policy-entanglement framework: given a parsed :class:`~gnn.model.GnnModel`, it
constructs the framework's coupling structures and reconstructs the entangled
joint posterior and its mutual-information curve **from the GNN-declared
parameters alone**.

Integrity invariant (ISA ISC-64, ``feedback-shape-tests-dont-bind-truth``):
this module sources the coupling matrix from the parsed ``.gnn`` file and
reconstructs the mutual information via the framework's general-purpose
:func:`~lean.coupling.entangled_posterior` + :func:`~lean.free_energy.total_correlation`.
It deliberately does **not** import ``ising_coupling`` or
``ising_mutual_information`` — the closed form is the comparison oracle used by
the round-trip script/test, never the reconstruction route.

This is an *integration / internal-consistency* check, not an independent
re-derivation: for the symmetric K=2 toy the general machinery provably reduces
to the closed form, so the two routes are the same scalar function written two
ways. What the agreement establishes — and what makes it a genuine witness
rather than an ``f(a) ≈ f(a)`` tautology — is that the GNN-sourced spec, pushed
through the *general* code path, reproduces the analytic prediction: a parser
error, a coupling-ignoring bridge, or a wrong coupling gap would each break it
(the zero-coupling negative control proves the bridge responds to the declared
coupling). Note the round-trip pins the gauge-invariant coupling *gap*, not the
literal matrix entries (which are pinned separately by ``to_pymdp_config`` and
the concordance parity test).
"""

from __future__ import annotations

import re
from typing import Any, cast

import numpy as np
from numpy.typing import NDArray

from gnn.model import GnnModel
from lean.coupling import entangled_posterior
from lean.free_energy import total_correlation

ArrayF = NDArray[np.float64]

_PAIR_COUPLING_RE = re.compile(r"^J(\d)(\d)$")


def stream_cardinality(model: GnnModel) -> int:
    """Policy cardinality per stream (read from the ``pi1`` declaration)."""
    return int(model.variable("pi1").dims[0])


def per_stream_priors(model: GnnModel) -> list[ArrayF]:
    """Return the per-stream habit priors ``[E1, E2, ...]`` as 1-D arrays.

    Raises:
        KeyError: if a stream's ``Ek`` prior is not declared/parameterized.
    """
    k = model.num_streams
    if k == 0:
        raise ValueError(f"GNN model {model.section!r} declares no policy streams (pi1, pi2, ...)")
    priors: list[ArrayF] = []
    for i in range(1, k + 1):
        priors.append(model.variable(f"E{i}").vector())
    return priors


def build_joint_coupling(model: GnnModel) -> ArrayF:
    """Construct the joint coupling tensor over the product policy space.

    For ``K=2`` the joint coupling is the single declared ``J`` matrix.  For
    ``K>2`` it is assembled from the pairwise coupling variables ``Jab`` (a,b
    1-indexed stream pair) by broadcasting each pairwise matrix onto the
    relevant axes and summing — exactly the additive coupling-graph structure
    of the framework (manuscript §8): ``J(pi) = sum_{(a,b) in edges} J_ab(pi^a, pi^b)``.

    This is the stock-GNN cross-stream encoding: each ``Jab`` is a joint
    variable over a 2-D product slice, with the coupling graph read off the
    ``Connections`` block.
    """
    k = model.num_streams
    card = stream_cardinality(model)
    shape = (card,) * k

    if k == 2 and model.has("J"):
        j = model.variable("J").matrix()
        if j.shape != shape:
            raise ValueError(f"coupling J shape {j.shape} != joint policy shape {shape}")
        return j

    joint = np.zeros(shape, dtype=np.float64)
    found = False
    for name, var in model.variables.items():
        m = _PAIR_COUPLING_RE.match(name)
        if not m:
            continue
        a, b = int(m.group(1)) - 1, int(m.group(2)) - 1
        if not (0 <= a < k and 0 <= b < k):
            raise ValueError(f"pairwise coupling {name!r} indexes streams outside 1..{k}")
        pair = var.matrix()  # (card, card)
        # Broadcast pair[pi^a, pi^b] onto the full joint tensor.
        bshape = [1] * k
        bshape[a] = card
        # Build via an einsum-free broadcast: place pair on axes (a, b).
        idx: list[object] = [None] * k
        idx[a] = slice(None)
        idx[b] = slice(None)
        # Construct an array that varies only along axes a and b.
        full = np.zeros(shape, dtype=np.float64)
        it = np.nditer(full, flags=["multi_index"], op_flags=[["writeonly"]])  # type: ignore[list-item]
        for x in it:
            mi = it.multi_index
            cast(Any, x)[...] = pair[mi[a], mi[b]]
        joint += full
        found = True
    if not found:
        raise ValueError(f"GNN model {model.section!r} declares no coupling variable (J or Jab)")
    return joint


def entangled_joint(model: GnnModel, lam: float) -> ArrayF:
    """Reconstruct the entangled joint posterior at coupling ``lam``.

    Uses the GNN-declared per-stream priors and joint coupling, with zero
    per-stream EFE and ``K_c = 0`` (the canonical toy operating point), pushed
    through the framework's :func:`entangled_posterior`.
    """
    priors = per_stream_priors(model)
    coupling_j = build_joint_coupling(model)
    k = model.num_streams
    card = stream_cardinality(model)
    per_stream_g = [np.zeros(card, dtype=np.float64) for _ in range(k)]
    coupling_kc = np.zeros((card,) * k, dtype=np.float64)
    gamma = model.variable("gamma").scalar() if model.has("gamma") else 0.0
    return entangled_posterior(
        mf_prior=priors,
        per_stream_G=per_stream_g,
        coupling_j=coupling_j,
        coupling_kc=coupling_kc,
        gamma=gamma,
        lam=float(lam),
    )


def to_pymdp_config(model: GnnModel) -> dict[str, object]:
    """Emit a pymdp/hyperparameters-equivalent config dict from a GNN model.

    This is the "GNN -> pymdp" generator scoped in S08 (``scripts/gnn_to_pymdp.py``):
    it consumes a parsed GNN source and produces the structural configuration a
    pymdp-style harness needs — stream count, per-stream policy cardinality,
    per-stream habit priors, the joint coupling tensor, and the scalar
    parameters — sourced entirely from the ``.gnn`` declarations.
    """
    priors = per_stream_priors(model)
    coupling = build_joint_coupling(model)
    gamma = model.variable("gamma").scalar() if model.has("gamma") else 0.0
    lam = model.variable("lam").scalar() if model.has("lam") else 0.0
    return {
        "model_section": model.section,
        "num_streams": model.num_streams,
        "policy_cardinality_per_stream": stream_cardinality(model),
        "per_stream_habit_priors": [p.tolist() for p in priors],
        "joint_coupling": coupling.tolist(),
        "gamma": float(gamma),
        "lambda": float(lam),
        "coupling_topology": model.model_parameters.get("coupling_topology", "clique"),
    }


def reconstruct_mi_curve(model: GnnModel, lambdas: NDArray[np.float64]) -> ArrayF:
    """Reconstruct the multi-information curve I(lambda) from the GNN model.

    For each ``lam`` in ``lambdas``, builds the entangled joint via
    :func:`entangled_joint` and returns its total correlation
    (multi-information).  This is the GNN-sourced route; the round-trip
    compares it against the closed form computed independently elsewhere.
    """
    lams = np.asarray(lambdas, dtype=np.float64)
    return np.array([total_correlation(entangled_joint(model, float(lam))) for lam in lams], dtype=np.float64)
