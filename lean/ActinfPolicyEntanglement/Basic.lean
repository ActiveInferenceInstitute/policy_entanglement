/- `ActinfPolicyEntanglement.Basic` — primitive types and stream-mode
   classification. Mathlib-free boundary fragment.

   This module defines:
   * `StreamIdx K`         — finite index of one stream in a `K`-ensemble
   * `PolicyFactor K`      — per-stream policy type assignment
   * `PolicySpace K Pol`   — joint policy tuple
   * `IsPlanningStream`,
     `IsReflexiveStream`   — planning vs reflexive stream classification
   * decidability instances + the trichotomy theorem `stream_classification`.
-/

namespace ActinfPolicyEntanglement

/-! ## Stream identity and policy spaces -/

/-- Index of one stream in a `K`-stream ensemble. -/
abbrev StreamIdx (K : Nat) := Fin K

/-- Per-stream policy factor: each of `K` streams has its own (finite)
    policy type. -/
abbrev PolicyFactor (K : Nat) := StreamIdx K → Type

/-- The joint policy space: a tuple of one policy per stream. -/
def PolicySpace (K : Nat) (Pol : PolicyFactor K) : Type :=
  ∀ k : StreamIdx K, Pol k

/-! ## Stream classification (planning vs reflexive)

A stream is *planning* when it computes expected free energy over a
horizon `> 0`; *reflexive* when it descends VFE one step at a time
(horizon 0). The two predicates partition the stream set. -/

/-- A stream is planning iff its horizon is positive. -/
def IsPlanningStream (horizon : Nat) : Prop := 0 < horizon

/-- A stream is reflexive iff its horizon is zero. -/
def IsReflexiveStream (horizon : Nat) : Prop := horizon = 0

/-- Decidability instance for `IsPlanningStream` so case analysis on
horizon mode can be performed without classical logic. -/
instance instDecidableIsPlanningStream (horizon : Nat) :
    Decidable (IsPlanningStream horizon) :=
  inferInstanceAs (Decidable (0 < horizon))

/-- Decidability instance for `IsReflexiveStream`. -/
instance instDecidableIsReflexiveStream (horizon : Nat) :
    Decidable (IsReflexiveStream horizon) :=
  inferInstanceAs (Decidable (horizon = 0))

/-- Every stream is either planning or reflexive: the horizon is either
positive or zero. -/
theorem stream_classification (horizon : Nat) :
    IsPlanningStream horizon ∨ IsReflexiveStream horizon := by
  cases horizon with
  | zero => exact Or.inr rfl
  | succ n => exact Or.inl (Nat.succ_pos n)

end ActinfPolicyEntanglement
