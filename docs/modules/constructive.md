# Constructive — `λ = 0` and trivial-coupling boundary lemmas

Manuscript section:
[`../manuscript/2C_lambda_deformation.md`](../../manuscript/2C_lambda_deformation.md)
(§4 mean-field reduction at `λ = 0`) and
[`../manuscript/2D_decomposition.md`](../../manuscript/2D_decomposition.md)
(§5 `λ = 0` baseline of the decomposition).

Lean source:
[`Constructive.lean`](../../lean/ActinfPolicyEntanglement/Constructive.lean).

## Role in the boundary fragment

`Constructive` supplies the *substantive* algebraic lemmas about the
two boundary cases of the λ-deformation:

1. **`λ = 0`**: the entangled-posterior log-weight collapses to the
   bare mean-field log-weight `logE π − γ · G π` (no trailing
   `+ 0` artifact).
2. **Trivial coupling** (`J ≡ 0`, `K_c ≡ 0`): every coupling-related
   quantity is identically `0`, not just shape-equal.

These are the reductions that justify the manuscript's claim that
the mean-field baseline is *recovered exactly* by the deformation
at the relevant boundaries.  Every theorem is proven using the
`CommScalar α` typeclass — they are genuine `= 0` statements (not
`x = x` reflexivity placeholders), exercised on `Int` via the
`CommScalar Int` instance in `Scalar.lean`.

## Theorems (all proven, zero `sorry`)

### `λ = 0` reduction

```lean
theorem entangledPosteriorLogWeight_at_zero {K Pol}
    (logE G : PolicySpace K Pol → α)
    (J K_c : CouplingPotential α K Pol)
    (gamma : α) (π : PolicySpace K Pol) :
    entangledPosteriorLogWeight logE G J K_c gamma 0 π
    = logE π - gamma * G π
```

Proof: unfolds `entangledPosteriorLogWeight`, rewrites with
`couplingLogWeight_at_zero` (from `Coupling.lean`), then closes
with `CommScalar.add_zero`.

### Trivial-coupling collapse

```lean
theorem couplingLogWeight_trivialCoupling
    (gamma lam : α) (π : PolicySpace K Pol) :
    couplingLogWeight (trivialCoupling : CouplingPotential α K Pol)
                      (trivialCoupling : CouplingPotential α K Pol)
                      gamma lam π = 0
```

Proof: unfolds `couplingLogWeight` and `trivialCoupling`, then
`rw` with `CommScalar.{mul_zero, sub_self}`.

```lean
theorem couplingNormSq_of_trivialCoupling (π : PolicySpace K Pol) :
    (trivialCoupling : CouplingPotential α K Pol) π
      * (trivialCoupling : CouplingPotential α K Pol) π = 0
```

Proof: one-line `CommScalar.zero_mul`.

### Coupling-tax at zero

```lean
theorem couplingTax_zero_at_zero (taxFunction : α → α)
    (h : taxFunction 0 = 0) :
    taxFunction 0 - taxFunction 0 = 0
```

Used by `Heterogeneous` to phrase the `O(λ²)` coupling-tax bound
(Theorem 9.1) at the `λ = 0` baseline: when the tax function is
pinned at `0`, its self-difference is `0`.

## Where to look

* Lean: [`Constructive.lean`](../../lean/ActinfPolicyEntanglement/Constructive.lean) (69 lines).
* Imports: `Basic`, `JointDist`, `Coupling`, `Scalar`.
* Imported by: the root `ActinfPolicyEntanglement.lean` and any
  caller that needs the explicit `λ = 0` / trivial-coupling
  reductions (notably the manuscript prose for §5 and §6.1, which
  cites `entangledPosteriorLogWeight_at_zero` as the boundary
  condition for the decomposition theorem).
* No standalone Python mirror — the Python layer realizes these
  reductions numerically inside
  [`src/lean/decomposition.py`](../../src/lean/decomposition.py)
  (e.g. `entanglement_decomposition_rhs(..., lam=0.0)` returns the
  bare marginal-free-energy sum).
