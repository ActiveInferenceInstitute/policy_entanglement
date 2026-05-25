# Basic — primitive types and stream-mode classification

Manuscript section:
[`../manuscript/2B_setup.md`](../../manuscript/2B_setup.md).

Lean source:
[`Basic.lean`](../../lean/ActinfPolicyEntanglement/Basic.lean).

## Role in the boundary fragment

`Basic` is the foundational module on which every other Lean
submodule depends.  It supplies the *type* layer: stream indices,
per-stream policy factors, the joint policy space, and the
planning-vs-reflexive trichotomy.  It is Mathlib-free and
`sorry`-free.

## Types

| Identifier | Type | Meaning |
|---|---|---|
| `StreamIdx K` | `Fin K` (abbrev) | Index of one stream in a `K`-stream ensemble |
| `PolicyFactor K` | `StreamIdx K → Type` (abbrev) | Per-stream policy *type* assignment |
| `PolicySpace K Pol` | `∀ k, Pol k` | Joint policy tuple: one policy per stream |

`PolicySpace` is exactly the dependent-product type that every
distribution module (`JointDist`, `Coupling`, `FreeEnergy`,
`Geometry`, `Spectral`, `Heterogeneous`, `Decomposition`) operates
over.  Keeping it as a `def` (not an abbrev) lets us hang
typeclass / theorem statements off it without unfolding by default.

## Stream classification

```lean
def IsPlanningStream  (horizon : Nat) : Prop := 0 < horizon
def IsReflexiveStream (horizon : Nat) : Prop := horizon = 0
```

A stream is *planning* iff its horizon is positive (it computes
expected free energy over a non-trivial roll-out); *reflexive* iff
its horizon is zero (it descends VFE one step at a time).  This
mirrors §3 of the manuscript.

Both predicates carry decidability instances
(`instDecidableIsPlanningStream`, `instDecidableIsReflexiveStream`)
so case analysis is constructive — no `Classical` axiom is invoked.

## Trichotomy theorem

```lean
theorem stream_classification (horizon : Nat) :
  IsPlanningStream horizon ∨ IsReflexiveStream horizon
```

Every horizon is either positive or zero — the partition is
exhaustive.  Proof is one `cases horizon` followed by `Or.inr rfl`
or `Or.inl (Nat.succ_pos _)`.

This theorem is used by `Heterogeneous` to phrase the three-level
update hierarchy (Theorem 9.1) without classical logic.

## Where to look

* Lean: [`Basic.lean`](../../lean/ActinfPolicyEntanglement/Basic.lean) (59 lines).
* Imported by: every other submodule under `lean/ActinfPolicyEntanglement/`.
* Python mirror: there is no separate Python file for `Basic` —
  the corresponding numerical layer treats stream indices as plain
  Python `int` and policies as flat `numpy` arrays; see
  [`src/lean/joint_dist.py`](../../src/lean/joint_dist.py).
