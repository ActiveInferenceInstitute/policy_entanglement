# `ActinfPolicyEntanglement.Scalar` — abstract scalar typeclass

The `Scalar` module is the foundation that lets the boundary fragment
prove its algebraic identities **on stock Lean 4 v4.29.0**, without
Mathlib, without `axiom`s, and without `sorry`s.

It exists because IEEE 754 `Float` arithmetic does not literally
satisfy commutative-ring laws (e.g. `0 * NaN = NaN`, not `0`), so we
cannot prove the affine-in-λ identity by direct rewriting on `Float`.
Instead, every algebraic theorem in the boundary fragment is stated
**polymorphically over `[CommScalar α]`** — a typeclass that bundles
the ring laws as fields the caller discharges.

## File

[`lean/ActinfPolicyEntanglement/Scalar.lean`](../../lean/ActinfPolicyEntanglement/Scalar.lean)

## The typeclass

```lean
class CommScalar (α : Type) extends
    Add α, Mul α, Sub α, Neg α, Zero α, One α where
  add_zero      : ∀ a : α, a + 0 = a
  zero_add      : ∀ a : α, 0 + a = a
  add_comm      : ∀ a b : α, a + b = b + a
  add_assoc     : ∀ a b c : α, a + b + c = a + (b + c)
  sub_def       : ∀ a b : α, a - b = a + (-b)
  mul_zero      : ∀ a : α, a * 0 = 0
  zero_mul      : ∀ a : α, 0 * a = 0
  mul_one       : ∀ a : α, a * 1 = a
  one_mul       : ∀ a : α, 1 * a = a
  mul_comm      : ∀ a b : α, a * b = b * a
  mul_assoc     : ∀ a b c : α, a * b * c = a * (b * c)
  mul_add       : ∀ a b c : α, a * (b + c) = a * b + a * c
  mul_neg       : ∀ a b : α, a * (-b) = -(a * b)
  add_neg_self  : ∀ a : α, a + (-a) = 0
```

The 14 fields are the standard commutative-ring axioms, phrased as
universally-quantified equations over the existing `Add`/`Mul`/`Sub`/
`Neg`/`Zero`/`One` operations. There is no `Inv`/division, no
ordering, no measure structure — just the ring skeleton.

## Derived lemmas

Everything below is proven from the typeclass fields; no further
axioms or `sorry`s.

| Lemma | Statement | Used by |
|---|---|---|
| `mul_sub` | `a * (b - c) = a * b - a * c` | `affine_diff` |
| `sub_mul` | `(a - b) * c = a * c - b * c` | `affine_diff` |
| `sub_self` | `a - a = 0` | `Constructive.couplingTax_zero_at_zero` |
| `affine_diff` | `(λ₁·J − γ·λ₁·K) − (λ₂·J − γ·λ₂·K) = (λ₁ − λ₂)·(J − γ·K)` | `Coupling.couplingLogWeight_affine_in_lam` |
| `affine_at_zero` | `0·J − γ·0·K = 0` | `Coupling.couplingLogWeight_at_zero` |

These are the load-bearing identities used to prove the e-geodesic
property of the λ-deformation (Theorem 7.4) and its λ = 0 specialization.

## Shipped instance: `Int`

```lean
instance : CommScalar Int where
  add_zero      := Int.add_zero
  zero_add      := Int.zero_add
  add_comm      := Int.add_comm
  add_assoc     := Int.add_assoc
  sub_def       := fun a b => by rw [Int.sub_eq_add_neg]
  mul_zero      := Int.mul_zero
  …
```

`Lean 4 core` provides every required ring law for `Int` as a named
theorem, so the instance is a forwarder. This means every algebraic
theorem stated against `[CommScalar α]` can be exercised on `Int`
directly — useful for property tests and worked examples.

## Why this matters

| Approach | Hygiene cost | Soundness |
|---|---|---|
| `sorry` placeholder | every sorry is an unscoped admission of `False` | unsound on combination |
| `axiom Float.zero_mul : ∀ x : Float, 0.0 * x = 0.0` | adds 1 named axiom per identity | **unsound** for `NaN`/`Inf` |
| Mathlib import | adds gigabytes of dependency, ~10 min build | sound |
| **`CommScalar α` typeclass (this approach)** | adds 14 typeclass fields the caller discharges | sound — `Int` instance is fully proved on stock Lean |

The typeclass approach gives a *strict* improvement over `sorry`: the
algebraic content is genuinely proven, the discharge surface is named
and bounded, and downstream consumers can supply their own scalar
type without touching the boundary fragment.

## How to add a custom scalar instance

If a downstream consumer wants to instantiate the boundary fragment
on `Real`/`ℝ` (with Mathlib) or on a fixed-precision rational, they
write:

```lean
import ActinfPolicyEntanglement.Scalar

namespace MyExtension

instance : ActinfPolicyEntanglement.CommScalar MyScalar where
  add_zero      := MyScalar.add_zero
  zero_add      := MyScalar.zero_add
  …  -- discharge each ring law
```

After that, every theorem in `Coupling`, `Geometry`,
`Decomposition`, `Constructive` etc. is automatically callable on
`MyScalar` without modifying the boundary fragment.

## Where it is used

| Module | Theorems polymorphic over `[CommScalar α]` |
|---|---|
| `Coupling` | `couplingLogWeight`, `entangledPosteriorLogWeight`, `couplingLogWeight_affine_in_lam`, `couplingLogWeight_at_zero` |
| `Geometry` | `entangledFamily_eGeodesic` |
| `Decomposition` | `couplingLogWeight_pointwise_at_zero` (Cor 5.3) |
| `Constructive` | `entangledPosteriorLogWeight_at_zero`, `couplingLogWeight_trivialCoupling`, `couplingNormSq_of_trivialCoupling`, `couplingTax_zero_at_zero` |

Float-typed quantities (probabilities, free energies) use `Float`
directly via the looser `[Mul α] [Sub α]` constraints on
`couplingLogWeight`'s evaluation; the *theorems* about those
quantities require the full `[CommScalar α]`.

## Related

* [`lean_reference.md`](../reference/lean_reference.md) — per-theorem status table
* [`information_geometry.md`](information_geometry.md) — uses `entangledFamily_eGeodesic`
* [`decomposition_theorem.md`](decomposition_theorem.md) — uses `couplingLogWeight_pointwise_at_zero`
