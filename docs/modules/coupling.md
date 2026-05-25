# Coupling — λ-entangled prior / posterior log-weights

Manuscript section:
[`../manuscript/2C_lambda_deformation.md`](../../manuscript/2C_lambda_deformation.md)
(§4.1 coupling potentials, §4.2 entangled posterior).

Lean source:
[`Coupling.lean`](../../lean/ActinfPolicyEntanglement/Coupling.lean).

## Role in the boundary fragment

`Coupling` introduces the *coupling potential* abstraction
(`J : PolicySpace → α` for the prior side, `K_c` for the EFE side)
and the affine-in-λ log-weight that bends a mean-field baseline
into the λ-entangled prior / posterior.

It is polymorphic over the `CommScalar α` typeclass declared in
[`Scalar.lean`](../../lean/ActinfPolicyEntanglement/Scalar.lean), so
the algebraic theorems are genuine `(=)` facts on any commutative
scalar (instantiated on `Int` for proof certification, on `Float`
for evaluation).

## Types

```lean
abbrev CouplingPotential (α : Type) (K : Nat) (Pol : PolicyFactor K) : Type :=
  PolicySpace K Pol → α

def trivialCoupling [Zero α] : CouplingPotential α K Pol :=
  fun _ => 0
```

`J` is the *habit coupling* (prior side); `K_c` is the *preference
coupling* (EFE side).  `trivialCoupling` is the boundary case
`λ = 0` reduces to.

## Log-weights

```lean
def couplingLogWeight (J K_c : CouplingPotential α K Pol)
    (gamma lam : α) : PolicySpace K Pol → α :=
  fun π => lam * J π - gamma * lam * K_c π

def entangledPosteriorLogWeight (logE G : PolicySpace K Pol → α)
    (J K_c : CouplingPotential α K Pol)
    (gamma lam : α) : PolicySpace K Pol → α :=
  fun π => logE π - gamma * G π + couplingLogWeight J K_c gamma lam π
```

`entangledPosteriorLogWeight` is the unnormalized log-weight of the
λ-entangled posterior at policy `π`.  Working at the *log-weight*
level keeps everything **affine in λ** and defers partition-function
bookkeeping until normalization.

## Theorems (all proven, zero `sorry`)

```lean
theorem couplingLogWeight_affine_in_lam :
    couplingLogWeight J K_c gamma lam1 π
      - couplingLogWeight J K_c gamma lam2 π
    = (lam1 - lam2) * (J π - gamma * K_c π)
```

This is the algebraic boundary statement of **Theorem 7.4**
(`entangledFamily_eGeodesic`) — it certifies that the log-weight
moves linearly in λ, which is the property an e-geodesic must
have on the dually-flat manifold of §7.

```lean
theorem couplingLogWeight_at_zero :
    couplingLogWeight J K_c gamma 0 π = 0
```

The mean-field reduction at `λ = 0`.  Combined with
`entangledPosteriorLogWeight_at_zero` from `Constructive.lean`,
this certifies that `λ = 0` recovers the bare mean-field log-weight
`logE π − γ · G π`.

## Where to look

* Lean: [`Coupling.lean`](../../lean/ActinfPolicyEntanglement/Coupling.lean) (87 lines).
* Imports: `Basic`, `JointDist`, `Scalar`.
* Imported by: `FreeEnergy`, `Geometry`, `Decomposition`,
  `Heterogeneous`, `Constructive`, `BernoulliToy`.
* Python mirror: [`src/lean/coupling.py`](../../src/lean/coupling.py)
  (`trivial_coupling`, `entangled_prior_unnormalised`,
  `entangled_prior`, `entangled_posterior`, `expected_value`,
  `entangled_log_weight_affine_in_lambda`, `coupling_log_weight`).
* Tests: [`tests/test_coupling.py`](../../tests/test_coupling.py).
