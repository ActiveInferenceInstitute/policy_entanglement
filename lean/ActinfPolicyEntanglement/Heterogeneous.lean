/- `ActinfPolicyEntanglement.Heterogeneous` — heterogeneous VFE/EFE
   ensembles and the O(λ²) coupling-tax bound (Theorem 9.1).

   Mathlib-free, `sorry`-free, `axiom`-free.  Theorem 9.1 and Corollary 9.2
   are stated as *witness-consuming* boundary forms: the bound's existence
   is parameterized by a structural witness (`BoundedQuadraticTax` /
   `SmallLambdaTolerance`) supplied by the caller, and the boundary
   fragment certifies the existence claim by extracting the witness
   fields. Numerical realizations live in
   [`src/lean/heterogeneous.py`](../../src/lean/heterogeneous.py). -/

import ActinfPolicyEntanglement.Basic
import ActinfPolicyEntanglement.JointDist
import ActinfPolicyEntanglement.Coupling
import ActinfPolicyEntanglement.FreeEnergy

namespace ActinfPolicyEntanglement

/-! ## §8.1 Stream modes (planning vs reflexive)

Each stream `k` is either *planning* (computes EFE over a horizon) or
*reflexive* (one-step VFE descent).  Per-stream classification by
horizon profile. -/

/-- Per-stream horizon assignment. -/
abbrev HorizonProfile (K : Nat) := StreamIdx K → Nat

/-! ## §9.3 The O(λ²) coupling-tax bound (Theorem 9.1) -/

/-- The coupling tax: difference between the free energy at λ and the
mean-field baseline at λ = 0. Boundary abstract: parameterized by an
abstract `taxFunction` that the caller supplies. -/
def couplingTax (taxFunction : Float → Float) (lam : Float) : Float :=
  taxFunction lam - taxFunction 0.0

/-- **Boundary witness for Theorem 9.1**: a non-negative constant `C`
together with the proof that `couplingTax taxFunction λ ≤ C · λ²` for
every `λ`. Supplied by the analytic Mathlib extension. -/
structure BoundedQuadraticTax (taxFunction : Float → Float) where
  /-- The quadratic envelope constant (depends on the coupling-norm). -/
  C : Float
  /-- `C ≥ 0`. -/
  C_nonneg : 0.0 ≤ C
  /-- The quadratic upper bound on the tax. -/
  bound : ∀ lam : Float, couplingTax taxFunction lam ≤ C * lam * lam

/-- **Theorem 9.1 (boundary witness form)**: a `BoundedQuadraticTax`
witness *is* the existence of the quadratic envelope.  Stock-Lean,
zero-`sorry`.

**Typed-API-contract disclaimer.** This theorem is *not* a stand-alone
proof of the `O(λ²)` coupling-tax bound; it is a typed-API contract.
The analytic content — the bound `taxFunction λ ≤ C·λ²` with `C ≥ 0`
universally over `λ` — is supplied as a structural hypothesis
(`BoundedQuadraticTax`); the boundary fragment re-publishes it as an
existence claim.  The Python numerical companion in
[`src/lean/heterogeneous.py`](../../src/lean/heterogeneous.py)
verifies the bound on concrete parameter sweeps; the separate
MathlibProofs layer will discharge it from Taylor expansion of the
coupling-prior log-partition. -/
theorem couplingTax_quadratic_bound (taxFunction : Float → Float)
    (witness : BoundedQuadraticTax taxFunction) :
    ∃ (C : Float), 0.0 ≤ C ∧
      ∀ lam, couplingTax taxFunction lam ≤ C * lam * lam :=
  ⟨witness.C, witness.C_nonneg, witness.bound⟩

/-- Accessor theorem: the quadratic-tax witness's envelope constant is
non-negative.  This small theorem is useful for theorem-map and
MathlibProofs callers that want the non-negativity field without
unpacking the structure by hand. -/
theorem boundedQuadraticTax_constant_nonneg
    (taxFunction : Float → Float)
    (witness : BoundedQuadraticTax taxFunction) :
    0.0 ≤ witness.C :=
  witness.C_nonneg

/-- Accessor theorem: instantiate the quadratic tax envelope at a
specific coupling value. -/
theorem boundedQuadraticTax_bound_at
    (taxFunction : Float → Float)
    (witness : BoundedQuadraticTax taxFunction)
    (lam : Float) :
    couplingTax taxFunction lam ≤ witness.C * lam * lam :=
  witness.bound lam

/-- **Boundary witness for Corollary 9.2**: a positive `lamMax` such
that `|λ| ≤ lamMax` implies the tax is bounded by `eps`. Supplied by
the continuity argument in the Mathlib extension. -/
structure SmallLambdaTolerance (taxFunction : Float → Float) (eps : Float) where
  /-- The tolerance window. -/
  lamMax : Float
  /-- `lamMax > 0`. -/
  lamMax_pos : 0.0 < lamMax
  /-- The local bound. -/
  bound : ∀ lam : Float, lam.abs ≤ lamMax → couplingTax taxFunction lam ≤ eps

/-- **Corollary 9.2 (boundary witness form)**: a `SmallLambdaTolerance`
witness *is* the existence of the tolerance window. Stock-Lean,
zero-`sorry`.

**Typed-API-contract disclaimer.** Same as `couplingTax_quadratic_bound`:
this is a typed-API contract, not a stand-alone proof.  The continuity
argument that delivers the tolerance window is supplied as a
`SmallLambdaTolerance` witness; the boundary fragment re-publishes
the existence claim. -/
theorem couplingTax_small_lambda_tolerance
    (taxFunction : Float → Float) (eps : Float)
    (witness : SmallLambdaTolerance taxFunction eps) :
    ∃ (lamMax : Float), 0.0 < lamMax ∧
      ∀ lam, lam.abs ≤ lamMax → couplingTax taxFunction lam ≤ eps :=
  ⟨witness.lamMax, witness.lamMax_pos, witness.bound⟩

/-- Accessor theorem: the small-λ witness carries a nondegenerate
tolerance window. -/
theorem smallLambdaTolerance_window_pos
    (taxFunction : Float → Float) (eps : Float)
    (witness : SmallLambdaTolerance taxFunction eps) :
    0.0 < witness.lamMax :=
  witness.lamMax_pos

/-- Accessor theorem: instantiate the small-λ tolerance bound. -/
theorem smallLambdaTolerance_bound_at
    (taxFunction : Float → Float) (eps : Float)
    (witness : SmallLambdaTolerance taxFunction eps)
    (lam : Float)
    (hLam : lam.abs ≤ witness.lamMax) :
    couplingTax taxFunction lam ≤ eps :=
  witness.bound lam hLam

end ActinfPolicyEntanglement
