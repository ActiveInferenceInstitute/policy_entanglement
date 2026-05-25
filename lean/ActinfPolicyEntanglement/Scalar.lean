/- `ActinfPolicyEntanglement.Scalar` — abstract scalar interface for the
   boundary fragment.

   Stock Lean 4 does **not** ship symbolic ring lemmas for `Float` (IEEE
   754 arithmetic is genuinely not associative or distributive in
   general). Adding axioms that would be unsound for `NaN`/`Inf` would
   be worse than honest `sorry`s.

   Instead, the load-bearing algebraic theorems of the boundary
   fragment (`Coupling`, `Geometry`, `Decomposition`, `Heterogeneous`)
   are stated polymorphically over a `CommScalar α` typeclass that
   bundles the commutative-ring laws we actually need. Stock concrete
   types like `Int` may instantiate it directly; any real-valued
   instantiation is discharged in a downstream `MathlibProofs`
   extension that ships with Mathlib enabled.

   This file is Mathlib-free, `sorry`-free, and `axiom`-free. -/

namespace ActinfPolicyEntanglement

/-! ## `CommScalar`: minimal commutative-ring interface

`CommScalar α` is the algebraic skeleton needed to phrase and prove the
λ-deformation theorems. Each field is a ring law expressed as a
universally-quantified equation in `α`. -/

/-- Minimal commutative-ring interface for the boundary fragment.

The fields are the ring laws (commutativity, associativity,
distributivity, neutral elements) phrased on the existing `Add`, `Mul`,
`Sub`, `Neg`, `Zero`, `One` operations. -/
class CommScalar (α : Type) extends
    Add α, Mul α, Sub α, Neg α, Zero α, One α where
  /-- `0` is a right identity for `+`. -/
  add_zero      : ∀ a : α, a + 0 = a
  /-- `0` is a left identity for `+`. -/
  zero_add      : ∀ a : α, 0 + a = a
  /-- `+` is commutative. -/
  add_comm      : ∀ a b : α, a + b = b + a
  /-- `+` is associative. -/
  add_assoc     : ∀ a b c : α, a + b + c = a + (b + c)
  /-- Subtraction is addition of the additive inverse. -/
  sub_def       : ∀ a b : α, a - b = a + (-b)
  /-- `0` is a right absorber for `*`. -/
  mul_zero      : ∀ a : α, a * 0 = 0
  /-- `0` is a left absorber for `*`. -/
  zero_mul      : ∀ a : α, 0 * a = 0
  /-- `1` is a right identity for `*`. -/
  mul_one       : ∀ a : α, a * 1 = a
  /-- `1` is a left identity for `*`. -/
  one_mul       : ∀ a : α, 1 * a = a
  /-- `*` is commutative. -/
  mul_comm      : ∀ a b : α, a * b = b * a
  /-- `*` is associative. -/
  mul_assoc     : ∀ a b c : α, a * b * c = a * (b * c)
  /-- Right distributivity of `*` over `+`. -/
  mul_add       : ∀ a b c : α, a * (b + c) = a * b + a * c
  /-- `*` distributes through unary `-`. -/
  mul_neg       : ∀ a b : α, a * (-b) = -(a * b)
  /-- The additive inverse cancels: `a + (-a) = 0`. -/
  add_neg_self  : ∀ a : α, a + (-a) = 0

namespace CommScalar
variable {α : Type} [CommScalar α]

/-! ## Derived lemmas

Everything below is proven from the ring axioms above; no further
axioms or `sorry`s are required. -/

/-- `*` distributes through `-`: `a * (b - c) = a * b - a * c`. -/
theorem mul_sub (a b c : α) : a * (b - c) = a * b - a * c := by
  rw [sub_def, mul_add, mul_neg, ← sub_def]

/-- Right distributivity for `-`: `(a - b) * c = a * c - b * c`. -/
theorem sub_mul (a b c : α) : (a - b) * c = a * c - b * c := by
  rw [mul_comm (a - b) c, mul_sub, mul_comm c a, mul_comm c b]

/-- A scalar minus itself is zero. -/
theorem sub_self (a : α) : a - a = 0 := by
  rw [sub_def, add_neg_self]

/-- Multiplying by zero on either side gives zero. -/
theorem zero_mul_left (a : α) : (0 : α) * a = 0 := zero_mul a

/-- Affine-in-`λ` identity: the difference of two evaluations of a
linear-in-`λ` form factors out the slope.

`λ₁ * J − γ * λ₁ * K − (λ₂ * J − γ * λ₂ * K) = (λ₁ − λ₂) * (J − γ * K)`

This is the core algebraic identity used by `couplingLogWeight_affine_in_lam`. -/
theorem affine_diff (lam1 lam2 gamma J K : α) :
    (lam1 * J - gamma * lam1 * K) - (lam2 * J - gamma * lam2 * K)
      = (lam1 - lam2) * (J - gamma * K) := by
  -- Expand the RHS via distributivity and rearrange.
  rw [sub_mul, mul_sub, mul_sub]
  -- Now both sides are linear combinations; align terms.
  -- LHS pieces: (lam1*J - gamma*lam1*K) - lam2*J + gamma*lam2*K
  -- RHS pieces: lam1*J - lam1*(gamma*K) - lam2*J + lam2*(gamma*K)
  -- Use commutativity/associativity of * to match `gamma * lam_i * K` with
  -- `lam_i * (gamma * K)`.
  have h1 : gamma * lam1 * K = lam1 * (gamma * K) := by
    rw [mul_assoc, mul_comm gamma (lam1 * K), mul_assoc, mul_comm K gamma]
  have h2 : gamma * lam2 * K = lam2 * (gamma * K) := by
    rw [mul_assoc, mul_comm gamma (lam2 * K), mul_assoc, mul_comm K gamma]
  rw [h1, h2]

/-- Specialisation at `λ = 0`: a linear-in-`λ` form vanishes. -/
theorem affine_at_zero (gamma J K : α) :
    (0 : α) * J - gamma * 0 * K = 0 := by
  rw [zero_mul, mul_zero, zero_mul, sub_def, add_neg_self]

end CommScalar

/-! ## `Int` instance

Lean 4 core ships `Int` with all the required ring laws as named
theorems. Providing the instance here lets every theorem stated against
`[CommScalar α]` be exercised on `Int` directly — useful for property
tests and worked examples. -/

instance : CommScalar Int where
  add_zero      := Int.add_zero
  zero_add      := Int.zero_add
  add_comm      := Int.add_comm
  add_assoc     := Int.add_assoc
  sub_def       := fun a b => by rw [Int.sub_eq_add_neg]
  mul_zero      := Int.mul_zero
  zero_mul      := Int.zero_mul
  mul_one       := Int.mul_one
  one_mul       := Int.one_mul
  mul_comm      := Int.mul_comm
  mul_assoc     := Int.mul_assoc
  mul_add       := Int.mul_add
  mul_neg       := Int.mul_neg
  add_neg_self  := Int.add_right_neg

end ActinfPolicyEntanglement
