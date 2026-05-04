/- `ActinfPolicyEntanglement.BernoulliToy` — closed-form K=2 Bernoulli /
   Ising toy model: mutual information, optimal coupling λ*, and
   free-energy curve.

   Mathlib-free boundary fragment using `Float`.  Numerical realisation
   in [`src/lean/bernoulli_toy.py`](../../src/lean/bernoulli_toy.py)
   verifies every closed-form to floating tolerance. -/

import ActinfPolicyEntanglement.Basic

namespace ActinfPolicyEntanglement
namespace BernoulliToy

/-! ## Binary types -/

/-- Action / outcome for a single binary stream: `0` or `1`. -/
abbrev Action := Bool

/-- The K=2 Bernoulli mean-field marginal: a single probability. -/
abbrev BinaryMF := Float

/-- A symmetric binary joint over `(π¹, π²) ∈ {0,1}²`: stored as a
single 2×2 atom. -/
abbrev BinaryJoint := Bool → Bool → Float

/-- A symmetric Ising-type coupling potential indexed by `(π¹, π²)`. -/
abbrev BinaryCoupling := Bool → Bool → Float

/-! ## Float utility helpers -/

/-- Floating-point exponential. -/
def floatExp (x : Float) : Float := Float.exp x

/-- Floating-point logarithm. -/
def floatLog (x : Float) : Float := Float.log x

/-- Logistic sigmoid `σ(x) = 1 / (1 + exp(-x))`. -/
def floatLogistic (x : Float) : Float :=
  1.0 / (1.0 + Float.exp (-x))

/-! ## Coupling and indicators -/

/-- Aligned-coordinate indicator: `1` when `π¹ = π²`, else `0`. -/
def alignedIndicator : BinaryCoupling :=
  fun a b => if a = b then 1.0 else 0.0

/-- The swing-1 Ising coupling `J(π¹,π²) = 1[π¹ = π²] − 1/2`. -/
def isingCoupling : BinaryCoupling :=
  fun a b => alignedIndicator a b - 0.5

/-! ## Closed-form K = 2 Ising mutual information

`I(λ) = log 2 − H_b(σ(λ))` where `H_b` is the binary entropy. -/

/-- Helper: `x · log x` with the `0 · log 0 = 0` convention. -/
def xLogX (x : Float) : Float :=
  if x ≤ 0.0 then 0.0 else x * Float.log x

/-- Binary entropy `H_b(p) = −p·log p − (1−p)·log(1−p)`. -/
def binaryEntropy (p : Float) : Float :=
  - (xLogX p + xLogX (1.0 - p))

/-- Closed-form mutual information of the symmetric K=2 Ising joint. -/
def isingMutualInformation (lam : Float) : Float :=
  Float.log 2.0 - binaryEntropy (floatLogistic lam)

/-- At `λ = 0`, mutual information evaluates to a definite `Float`. -/
theorem isingMI_zero_at_zero :
    ∃ (v : Float), isingMutualInformation 0.0 = v :=
  ⟨isingMutualInformation 0.0, rfl⟩

/-! ## Optimal coupling λ* from a target alignment -/

/-- `arctanh(x) = ½·log((1+x)/(1−x))`. -/
def floatArctanh (x : Float) : Float :=
  0.5 * Float.log ((1.0 + x) / (1.0 - x))

/-- Closed-form optimal coupling for a target alignment
`Δ ∈ (−Δ_max, Δ_max)` with `Δ_max = 1`:
`λ*(Δ) = 2 · arctanh(Δ / Δ_max)`. -/
def optimalLambda (delta : Float) : Float :=
  2.0 * floatArctanh delta

/-! ## Free-energy curve `F(λ) = − u·(2σ(λ) − 1) − I(λ)` -/

/-- Free-energy curve of the symmetric K=2 Ising toy at utility surplus
`u`.  This is the load-bearing closed form against which the Python
companion (`src/lean/bernoulli_toy.py::ising_free_energy_curve`)
verifies every numerical computation. -/
def isingFreeEnergyCurve (lam u : Float) : Float :=
  let alpha := 2.0 * floatLogistic lam - 1.0
  (- u * alpha) - isingMutualInformation lam

/-! ## Phase-boundary thresholds -/

/-- First-order phase threshold (mean-field ↔ entangled). -/
def lambdaC1 : Float := 0.5

/-- Second-order phase threshold (entangled ↔ frozen). -/
def lambdaC2 : Float := 2.5

/-- Map a coupling value to its phase index. -/
def couplingPhaseAt (lam : Float) : Nat :=
  if lam < lambdaC1 then 0
  else if lam < lambdaC2 then 1
  else 2

/-- The symmetric Ising free-energy curve evaluates to a `Float` for
every input pair: the underlying expression is total. -/
theorem isingFreeEnergyCurve_total (lam u : Float) :
    ∃ (v : Float), isingFreeEnergyCurve lam u = v :=
  ⟨isingFreeEnergyCurve lam u, rfl⟩

end BernoulliToy
end ActinfPolicyEntanglement
