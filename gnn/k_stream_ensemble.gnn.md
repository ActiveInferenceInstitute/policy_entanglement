# GNN Example: K=3 Policy-Entanglement Ensemble (chain coupling)

# GNN Version: 1.1

# Demonstrates that the stock-GNN joint-variable encoding of cross-stream coupling
# scales to K > 2. Three binary policy streams with pairwise Ising couplings on a
# chain topology (J12 between streams 1-2, J23 between streams 2-3). The point of
# this file is generality of the ENCODING, not a closed-form round-trip: it shows the
# cross-stream coupling pattern of bernoulli_toy.gnn.md composes to arbitrary K and
# arbitrary coupling topology using only stock GNN v1.1 primitives.

## GNNSection

ActInfPolicyEntanglement_K3_Chain

## GNNVersionAndFlags

GNN v1.1

## ModelName

K=3 Policy-Entanglement Ensemble (Chain Coupling)

## ModelAnnotation

Three binary Active Inference policy streams with a chain coupling topology:

- Streams 1, 2, 3 each select a binary policy pi^k in {0, 1}.
- Pairwise Ising couplings J12 (streams 1-2) and J23 (streams 2-3) form a chain;
  stream 1 and stream 3 are coupled only through stream 2 (no J13 edge).
- Each pairwise coupling is a stock-GNN joint variable over the relevant 2x2 product
  policy space, with connection edges binding the two participating streams.
- This is the heterogeneous-ensemble / sparse-topology setting of manuscript §8-9:
  the coupling graph's sparsity (here, a chain rather than a clique) is read off the
  Connections block directly.

The encoding requires no GNN primitive beyond stock v1.1 joint variables and edges:
K streams compose to K-1 pairwise blocks for a chain, or C(K,2) for a clique.

## StateSpaceBlock

# Per-stream binary policy distributions

pi1[2,1,type=float]      # Stream-1 policy
pi2[2,1,type=float]      # Stream-2 policy
pi3[2,1,type=float]      # Stream-3 policy

# Per-stream habit priors

E1[2,1,type=float]
E2[2,1,type=float]
E3[2,1,type=float]

# Pairwise cross-stream couplings (chain topology: 1-2 and 2-3)

J12[2,2,type=float]      # Coupling on the (pi^1,pi^2) product space
J23[2,2,type=float]      # Coupling on the (pi^2,pi^3) product space

# Scalar parameters

lam[1,type=float]        # Deformation parameter lambda
gamma[1,type=float]      # Sophistication weight

# Entangled joint posterior over (pi^1,pi^2,pi^3)

q_joint[2,2,2,type=float]  # Entangled joint posterior

## Connections

E1>pi1
E2>pi2
E3>pi3
pi1-J12:cross_stream_coupling
pi2-J12:cross_stream_coupling
pi2-J23:cross_stream_coupling
pi3-J23:cross_stream_coupling
pi1>q_joint
pi2>q_joint
pi3>q_joint
J12>q_joint:coupling
J23>q_joint:coupling
lam>q_joint:deformation

## InitialParameterization

E1={(0.5, 0.5)}
E2={(0.5, 0.5)}
E3={(0.5, 0.5)}

# Symmetric Ising couplings on each chain edge

J12={
  (0.5, -0.5),
  (-0.5, 0.5)
}

J23={
  (0.5, -0.5),
  (-0.5, 0.5)
}

lam={(0.0)}
gamma={(0.0)}

## Equations

# Entangled joint (gamma=0):
#   q_lambda(pi) proportional to prod_k E^k(pi^k) * exp(lambda * (J12(pi^1,pi^2) + J23(pi^2,pi^3)))
# The chain topology means I(pi^1 ; pi^3 | pi^2) structure follows the coupling graph.

## Time

Static

## ActInf Ontology Annotation

pi1=Stream1PolicyVector
pi2=Stream2PolicyVector
pi3=Stream3PolicyVector
E1=Stream1HabitPrior
E2=Stream2HabitPrior
E3=Stream3HabitPrior
J12=CrossStreamCouplingPotential
J23=CrossStreamCouplingPotential
lam=EntanglementDeformationParameter
gamma=SophisticationWeight
q_joint=EntangledJointPosterior

## ModelParameters

num_streams: 3
policy_cardinality_per_stream: 2
coupling: ising_chain
coupling_topology: chain
gamma: 0.0

## Footer

K=3 Policy-Entanglement Ensemble (Chain Coupling) v1.1 - GNN Representation.
Demonstrates the stock-GNN cross-stream coupling encoding scales to K>2 and to
sparse coupling topologies, using only stock GNN v1.1 joint variables and edges.

## Signature

Generated and verified by the policy-entanglement GNN bridge (src/gnn/). Not cryptographically signed.
