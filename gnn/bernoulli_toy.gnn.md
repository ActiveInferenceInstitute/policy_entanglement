# GNN Example: K=2 Bernoulli / Ising Policy-Entanglement Toy

# GNN Version: 1.1

# The simplest non-trivial policy-entanglement model: two binary policy
# streams with a symmetric Ising habit coupling on the joint policy space.
# This is the canonical worked example of manuscript §6.1 / Supplement S03,
# expressed here as the *fifth track* (GNN) alongside prose, equations,
# Python/pymdp, and Lean. See manuscript/S08_gnn_generalized_notation_extension.md.

## GNNSection

ActInfPolicyEntanglement_K2_Ising

## GNNVersionAndFlags

GNN v1.1

## ModelName

K=2 Bernoulli/Ising Policy-Entanglement Toy

## ModelAnnotation

Two binary Active Inference policy streams coupled by a symmetric Ising habit:

- Stream 1 and Stream 2 each select a binary policy pi^k in {0, 1}.
- Each stream carries a habit / policy-prior E^k (here symmetric Bernoulli(1/2)).
- A cross-stream coupling potential J(pi^1, pi^2) over the JOINT policy space
  favours aligned policies (0,0)/(1,1) and penalises anti-aligned (0,1)/(1,0).
- The deformation parameter lambda is the e-coordinate of the entanglement family:
  the entangled joint posterior is q_lambda(pi) proportional to E(pi) * exp(lambda * J(pi)).
- The cross-stream coupling is encoded with a STOCK GNN v1.1 joint variable over the
  product policy space plus connection edges binding each stream to it -- the same
  pattern the Active Inference Institute's own multi_agent_coordination.md uses for
  its s_joint joint-state variable. No non-stock GNN primitive is required.

The closed-form mutual information of the entangled joint is
I(lambda) = log 2 - H_b(sigma(lambda)), where sigma is the logistic and H_b the
binary entropy; it is zero at lambda=0 and saturates at log 2 as |lambda| grows.

## StateSpaceBlock

# Per-stream binary policy distributions

pi1[2,1,type=float]      # Stream-1 policy distribution over {0,1}
pi2[2,1,type=float]      # Stream-2 policy distribution over {0,1}

# Per-stream habit / policy-prior (symmetric Bernoulli(1/2) for this toy)

E1[2,1,type=float]       # Stream-1 habit prior E^1
E2[2,1,type=float]       # Stream-2 habit prior E^2

# Cross-stream coupling potential J over the joint policy space (2 x 2).
# Stock-GNN joint variable: rows index pi^1, columns index pi^2.

J[2,2,type=float]        # Cross-stream coupling potential J(pi^1,pi^2)

# Scalar parameters

lam[1,type=float]        # Deformation parameter lambda (e-coordinate)
gamma[1,type=float]      # Sophistication weight (weights K_c; zero here)

# Entangled joint posterior over (pi^1, pi^2)

q_joint[2,2,type=float]  # Entangled joint posterior q_lambda(pi^1,pi^2)

## Connections

E1>pi1
E2>pi2
pi1-J:cross_stream_coupling
pi2-J:cross_stream_coupling
pi1>q_joint
pi2>q_joint
J>q_joint:coupling
lam>q_joint:deformation

## InitialParameterization

# Symmetric Bernoulli(1/2) per-stream habit priors

E1={(0.5, 0.5)}
E2={(0.5, 0.5)}

# Ising coupling: aligned (0,0)/(1,1) favoured, anti-aligned penalised.
# Mean-zero, swing-1 form J(pi) = aligned_indicator(pi) - 1/2:
#   J[0,0]=J[1,1]=+0.5 (aligned), J[0,1]=J[1,0]=-0.5 (anti-aligned).

J={
  (0.5, -0.5),
  (-0.5, 0.5)
}

# Operating point: lambda=0 (independent baseline); gamma=0 (no K_c term).

lam={(0.0)}
gamma={(0.0)}

## Equations

# Entangled joint posterior (gamma=0, K_c=0):
#   q_lambda(pi^1,pi^2) proportional to E1(pi^1) * E2(pi^2) * exp(lambda * J(pi^1,pi^2))
# Closed-form mutual information of the entangled joint:
#   I(lambda) = log 2 - H_b(sigma(lambda))
# where sigma(x) = 1/(1+exp(-x)) and H_b(p) = -p log p - (1-p) log(1-p).

## Time

Static

## ActInf Ontology Annotation

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
policy_cardinality_per_stream: 2
coupling: ising_symmetric
gamma: 0.0

## Footer

K=2 Bernoulli/Ising Policy-Entanglement Toy v1.1 - GNN Representation.
The fifth track of the policy-entanglement framework. The cross-stream coupling
is a stock GNN v1.1 joint variable (no upstream extension required). The round-trip
in scripts/simulate_gnn.py reconstructs the mutual-information curve from THIS file's
J matrix via the framework's entangled_posterior + total_correlation and matches the
closed form I(lambda) = log 2 - H_b(sigma(lambda)) to BERNOULLI_VERIFICATION_TOLERANCE.

## Signature

Generated and verified by the policy-entanglement GNN bridge (src/gnn/). Not cryptographically signed.
