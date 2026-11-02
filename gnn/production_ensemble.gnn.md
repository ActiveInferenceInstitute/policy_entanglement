# GNN Example: Policy-Entanglement Production K=2 Ising Ensemble (pymdp harness)

# GNN Version: 1.1

# The production configuration of the pymdp simulation harness, expressed in
# stock GNN v1.1. This is the model that src/simulation/builders.py
# ::make_ising_ensemble materialises for scripts/simulate_pymdp.py,
# scripts/simulate_multi_k.py, scripts/simulate_long_horizon.py,
# scripts/simulate_revertibility.py, and scripts/simulate_robustness.py under
# the simulation.hyperparameters constants. See
# tests/test_gnn_harness_conformance.py for the drift gate.

## GNNSection

ActInfPolicyEntanglement_ProductionEnsemble

## GNNVersionAndFlags

GNN v1.1

## ModelName

Policy-Entanglement Production K=2 Ising Ensemble (pymdp harness)

## ModelAnnotation

The production K-stream ensemble of the pymdp simulation harness, specified in
stock GNN v1.1. Every stream is the same 2-state / 2-observation / 2-control
POMDP, and the streams are coupled by a symmetric Ising potential on the joint
policy space:

- Streams: K = PYMDP_ENSEMBLE_K = 2 in the default production ensemble; the
  multi-K experiments (MULTI_K_VALUES = 3, 4, 5) reuse the same per-stream
  factors and the same coupling rule for larger K.
- Likelihood: A^k = I over (observation, state) -- each hidden state emits its
  own discrete signal (builders.two_state_identity_likelihood).
- Transition: B^k[next state, previous state, control] with control 0 "hold"
  (B[:, :, 0] = I) and control 1 "swap" (B[:, :, 1] = the cyclic shift),
  each control slice column-stochastic over the previous state
  (builders.two_action_swap_transitions).
- Preferences: C^k = (0, 1) over observations -- outcome 1 is preferred with
  unit strength (builders.make_bernoulli_stream, preference_strength = 1).
- Prior: D^k = (1/2, 1/2) -- the uniform hidden-state prior
  (builders.make_bernoulli_stream, prior_bias = 1/2).
- Habit: E^k = (1/2, 1/2) -- the uniform policy prior, matching pymdp's
  default E vector for the per-stream agents.
- Coupling: J is the symmetric Ising potential on the product policy space,
  mean-zero and peak-normalized to coupling_amplitude = 1.0, i.e. the pairwise
  aligned-indicator sum centered and scaled to unit peak
  (builders.ising_coupling_tensor). For K = 2 this is
  J = ((+1, -1), (-1, +1)).
- Sophistication: gamma = PYMDP_ENSEMBLE_GAMMA = 1.0 weights the (here zero)
  K_c term in the entangled posterior.

The arrays declared here are verified elementwise against
simulation.builders by tests/test_gnn_harness_conformance.py; drift between
this specification and the production harness fails the test suite and the
scripts/simulate_gnn.py pipeline stage.

## StateSpaceBlock

# Per-stream POMDP factors (stream k = 1, 2). pymdp orientation:
# A[observation, state]; B[next state, previous state, control];
# C[observation]; D[state].

A1[2,2,type=float]      # stream-1 likelihood (identity)
B1[2,2,2,type=float]    # stream-1 transitions (hold / swap), 2 controls
C1[2,type=float]        # stream-1 log-preferences over observations
D1[2,type=float]        # stream-1 prior over hidden states
s1[2,1,type=float]      # stream-1 hidden state factor (cardinality 2)
o1[2,1,type=int]        # stream-1 observation (cardinality 2)
u1[1,type=int]          # stream-1 control index (2 controls, declared by B1)

A2[2,2,type=float]      # stream-2 likelihood (identity)
B2[2,2,2,type=float]    # stream-2 transitions (hold / swap), 2 controls
C2[2,type=float]        # stream-2 log-preferences over observations
D2[2,type=float]        # stream-2 prior over hidden states
s2[2,1,type=float]      # stream-2 hidden state factor (cardinality 2)
o2[2,1,type=int]        # stream-2 observation (cardinality 2)
u2[1,type=int]          # stream-2 control index (2 controls, declared by B2)

# Per-stream policy distributions and habit priors (uniform over the two
# policies). The cross-stream coupling is encoded as a stock GNN joint
# variable over the product policy space, with connection edges binding each
# stream to it -- the same encoding as bernoulli_toy.gnn.md.

pi1[2,1,type=float]     # stream-1 policy distribution over {0, 1}
pi2[2,1,type=float]     # stream-2 policy distribution over {0, 1}
E1[2,1,type=float]      # stream-1 habit / policy prior (uniform)
E2[2,1,type=float]      # stream-2 habit / policy prior (uniform)

# Cross-stream coupling potential over the joint policy space (2 x 2).
# Rows index pi^1, columns index pi^2.

J[2,2,type=float]       # production Ising coupling J(pi^1, pi^2)
lam[1,type=float]       # deformation parameter (harness probe grid)
gamma[1,type=float]     # sophistication weight (K_c term is zero here)
q_joint[2,2,type=float] # entangled joint posterior q_lam(pi^1, pi^2)

## Connections

# Per-stream generative-model edges

D1>s1
s1-A1
A1-o1
s1-B1
B1>u1
D2>s2
s2-A2
A2-o2
s2-B2
B2>u2

# Policy-level habit and cross-stream coupling

E1>pi1
E2>pi2
pi1-J:cross_stream_coupling
pi2-J:cross_stream_coupling
pi1>q_joint
pi2>q_joint
J>q_joint:coupling
lam>q_joint:deformation

## InitialParameterization

# Identity observation likelihood A[observation, state] = I.

A1={
  (1.0, 0.0),
  (0.0, 1.0)
}

A2={
  (1.0, 0.0),
  (0.0, 1.0)
}

# Two-control transition tensor B[next state, previous state, control], each
# control slice column-stochastic over the previous state:
#   control 0 "hold": B[:, :, 0] = I
#   control 1 "swap": B[:, :, 1] = ((0, 1), (1, 0))

B1={
  ( (1.0, 0.0), (0.0, 1.0) ),
  ( (0.0, 1.0), (1.0, 0.0) )
}

B2={
  ( (1.0, 0.0), (0.0, 1.0) ),
  ( (0.0, 1.0), (1.0, 0.0) )
}

# Log-preference vector over observations: outcome 1 preferred with unit
# strength; uniform state prior; uniform habit / policy prior.

C1={(0.0, 1.0)}
C2={(0.0, 1.0)}
D1={(0.5, 0.5)}
D2={(0.5, 0.5)}
E1={(0.5, 0.5)}
E2={(0.5, 0.5)}

# Production Ising coupling: mean-zero, peak-normalized to coupling_amplitude
# 1.0; aligned (0,0)/(1,1) favoured, anti-aligned (0,1)/(1,0) penalised.

J={
  (1.0, -1.0),
  (-1.0, 1.0)
}

# Operating point: lambda = 0 (independent baseline; the harness probes
# lambda over its configured grid) and gamma = 1.0.

lam={(0.0)}
gamma={(1.0)}

## Equations

# Entangled joint posterior over the joint policy space (gamma = 0, K_c = 0):
#   q_lam(pi) proportional to (prod_k E^k(pi^k)) * exp(lam * J(pi)).
# Production Ising coupling rule (builders.ising_coupling_tensor):
#   J(pi) = c * (sum over stream pairs (a < b) of (1{pi^a = pi^b} - 1/2)),
#   with the pair sum centered to zero mean and c chosen so that
#   max |J| = coupling_amplitude; for K = 2, J = ((+1, -1), (-1, +1)) at
#   coupling_amplitude = 1.0.
# Per-stream transitions (builders.two_action_swap_transitions):
#   B[:, :, 0] = I ("hold"); B[:, :, 1] = the cyclic shift ("swap").

## Time

Static

## ActInfOntologyAnnotation

A1=LikelihoodMatrix
B1=TransitionMatrix
C1=LogPreferenceVector
D1=PriorOverHiddenStates
s1=HiddenState
o1=Observation
u1=Action
A2=LikelihoodMatrix
B2=TransitionMatrix
C2=LogPreferenceVector
D2=PriorOverHiddenStates
s2=HiddenState
o2=Observation
u2=Action
pi1=Stream1PolicyVector
pi2=Stream2PolicyVector
E1=Stream1HabitPrior
E2=Stream2HabitPrior
J=CrossStreamCouplingPotential
lam=EntanglementDeformationParameter
gamma=SophisticationWeight
q_joint=EntangledJointPosterior

## ModelParameters

num_streams: 2
multi_k_stream_counts: 3, 4, 5
num_states_per_stream: 2
num_observations_per_stream: 2
num_controls_per_stream: 2
policy_cardinality_per_stream: 2
likelihood: identity
transition: hold_swap
preference_strength: 1.0
prior_bias: 0.5
b_tensor_order: next_state_previous_state_control
coupling: ising_symmetric_peak_normalized
coupling_amplitude: 1.0
gamma: 1.0

## Footer

Policy-Entanglement Production K=2 Ising Ensemble (pymdp harness) v1.1 - GNN
Representation. Specifies the arrays that src/simulation/builders.py
::make_ising_ensemble materialises for the production pipeline; conformance is
enforced by tests/test_gnn_harness_conformance.py and the
scripts/simulate_gnn.py sidecar output/data/gnn_production_conformance.json.

## Signature

Generated and verified by the policy-entanglement GNN harness bridge
(src/gnn/harness.py). Not cryptographically signed.
