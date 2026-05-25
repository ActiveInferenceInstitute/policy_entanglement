/- GENERATED — DO NOT EDIT BY HAND.
   Emitted by `src/gnn/lean_emit.py` from a GNN v1.1 source file
   (`gnn/bernoulli_toy.gnn.md`, section 'ActInfPolicyEntanglement_K2_Ising').

   This is a TYPED CONTRACT, not a proof.  Type-checking this file certifies the
   structural signature of the GNN-specified policy-entanglement model; it does
   NOT establish any analytic content and does NOT promote any registry row to
   `proved`/`witness`.  Self-contained core Lean 4 (Mathlib-free) so it
   type-checks on the stock toolchain the boundary fragment pins. -/

namespace GnnGenerated

/-- A binary policy stream's habit prior: a probability per action `{0,1}`. -/
abbrev StreamPrior := Bool → Float

/-- A cross-stream coupling potential over the joint policy space `{0,1}²`. -/
abbrev Coupling2 := Bool → Bool → Float

/-- Typed contract for a K=2 policy-entanglement GNN model.  Field names mirror
    the manuscript symbol concordance (E^k, J, λ, γ). -/
structure PolicyEntanglementK2 where
  numStreams  : Nat
  cardinality : Nat
  habitPrior1 : StreamPrior
  habitPrior2 : StreamPrior
  coupling    : Coupling2
  lambda      : Float
  gamma       : Float

def habitPrior1_ActInfPolicyEntanglement_K2_Ising : Bool → Float := fun a =>
  match a with
  | false => 0.5
  | true => 0.5

def habitPrior2_ActInfPolicyEntanglement_K2_Ising : Bool → Float := fun a =>
  match a with
  | false => 0.5
  | true => 0.5

def coupling_ActInfPolicyEntanglement_K2_Ising : Bool → Bool → Float := fun a b =>
  match a, b with
  | false, false => 0.5
  | false, true => (-0.5)
  | true, false => (-0.5)
  | true, true => 0.5

/-- The model emitted from the GNN source. -/
def ActInfPolicyEntanglement_K2_Ising : PolicyEntanglementK2 where
  numStreams  := 2
  cardinality := 2
  habitPrior1 := habitPrior1_ActInfPolicyEntanglement_K2_Ising
  habitPrior2 := habitPrior2_ActInfPolicyEntanglement_K2_Ising
  coupling    := coupling_ActInfPolicyEntanglement_K2_Ising
  lambda      := 0.0
  gamma       := 0.0

/-- Structural sanity (typed contract, not an analytic proof): the emitted
    model declares two binary streams at the GNN-specified cardinality. -/
example : ActInfPolicyEntanglement_K2_Ising.numStreams = 2 := rfl
example : ActInfPolicyEntanglement_K2_Ising.cardinality = 2 := rfl

end GnnGenerated
