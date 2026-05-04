/- `ActinfPolicyEntanglement.Monotonicity` — zero-`sorry` constructive
   monotonicity lemmas about non-negative real / Float scalars and
   simple list folds.

   These lemmas form the *constructive* sub-fragment of the Lean track:
   no Mathlib, no `sorry`. They support the boundary statements in
   `Coupling`, `FreeEnergy`, `Geometry`, and `Heterogeneous`. -/

import ActinfPolicyEntanglement.Basic

namespace ActinfPolicyEntanglement
namespace Monotonicity

/-! ## Nat monotonicity helpers -/

theorem nat_le_refl (n : Nat) : n ≤ n := Nat.le_refl n

theorem nat_le_trans {a b c : Nat} (hab : a ≤ b) (hbc : b ≤ c) :
    a ≤ c := Nat.le_trans hab hbc

theorem nat_succ_pos (n : Nat) : 0 < n + 1 := Nat.succ_pos n

theorem nat_zero_le (n : Nat) : 0 ≤ n := Nat.zero_le n

theorem nat_le_succ (n : Nat) : n ≤ n + 1 := Nat.le_succ n

theorem nat_lt_succ_self (n : Nat) : n < n + 1 := Nat.lt_succ_self n

/-! ## Or / decidability lemmas for stream classification -/

theorem or_self_iff (P : Prop) : P ∨ P ↔ P :=
  ⟨fun h => h.elim id id, fun h => Or.inl h⟩

theorem or_comm_iff (P Q : Prop) : P ∨ Q ↔ Q ∨ P :=
  ⟨fun h => h.elim Or.inr Or.inl, fun h => h.elim Or.inr Or.inl⟩

theorem and_self_iff (P : Prop) : P ∧ P ↔ P :=
  ⟨fun h => h.1, fun h => ⟨h, h⟩⟩

/-! ## List length and fold monotonicity -/

theorem list_length_nonneg {α : Type} (l : List α) : 0 ≤ l.length :=
  Nat.zero_le _

theorem list_length_cons {α : Type} (x : α) (l : List α) :
    (x :: l).length = l.length + 1 := rfl

/-- Length of an appended list (boundary form, omega-discharged). -/
theorem list_length_append {α : Type} (l₁ l₂ : List α) :
    (l₁ ++ l₂).length = l₁.length + l₂.length := by
  induction l₁ with
  | nil => simp [Nat.zero_add]
  | cons _ xs ih =>
      simp [List.cons_append, list_length_cons, ih]
      omega

/-- Right-identity of append. -/
theorem list_append_nil {α : Type} (l : List α) : l ++ [] = l := by
  induction l with
  | nil => rfl
  | cons _ _ ih =>
      show _ :: (_ ++ []) = _ :: _
      rw [ih]

theorem list_nil_append {α : Type} (l : List α) : [] ++ l = l := rfl

/-! ## Fin monotonicity -/

theorem fin_lt_size (K : Nat) (k : Fin K) : k.val < K := k.isLt

theorem fin_zero_lt {K : Nat} (h : 0 < K) : (⟨0, h⟩ : Fin K).val = 0 := rfl

end Monotonicity
end ActinfPolicyEntanglement
