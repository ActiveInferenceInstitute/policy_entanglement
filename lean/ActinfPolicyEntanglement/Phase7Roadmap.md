# Phase 7 Roadmap: Mathlib Integration for Policy Entanglement

**Project**: `actinf_policy_entanglement_lean`  
**Date**: 2026-05-04  
**Status**: Phase 6 complete, Phase 7 in progress  

## Overview

This document outlines the detailed plan for completing Phase 7: full Mathlib integration. The goal is to replace all `sorry` markers with formal proofs using Mathlib's library, thereby making the formalization complete and machine-checked.

## Current State

All Lean files have been restored with `sorry` markers for the unproven theorems. The files compile with `lake build` (assuming the necessary Mathlib imports are in place). The remaining work is to prove the following theorems:

### Theorems Requiring Proof

#### 1. `Constructive.lean`
- `klNonNeg`: KL divergence is non-negative
- `logSumExpBound`: Log-sum-exp inequality
- `jensenConvex`: Jensen's inequality for convex functions
- `maxEntropyUniform`: Entropy maximization by uniform distribution

#### 2. `FreeEnergy.lean`
- Definitions need to be connected to Mathlib's measure-theoretic probability
- Need to prove properties of `kl`, `entropy`, `variationalFreeEnergy`

#### 3. `Decomposition.lean`
- `entanglementDecomposition`: Main entanglement decomposition theorem
- `couplingPaysForItself`: Coupling pays for itself corollary
- `lambdaZeroDecomposition`: λ=0 decomposition
- `strictGainNonMeanField`: Strict gain when non-mean-field

#### 4. `Geometry.lean`
- `isEGeodesic`: Characterization of e-geodesics
- `fisherInformation`: Fisher information matrix
- `isExponentialFamily`: Exponential family properties

#### 5. `Coupling.lean`
- `marginalCouplingCost`: Marginal coupling cost definition and properties

#### 6. `Spectral.lean`
- `schmidtRank`: Schmidt rank computation
- `tensorTrainRank`: Tensor train rank computation

#### 7. `Heterogeneous.lean`
- `treeStructuredComplexity`: Complexity of tree-structured coupling

#### 8. `Monotonicity.lean`
- `freeEnergyMonotonicity`: Free energy monotonicity along e-geodesics
- `couplingCostMonotonicity`: Coupling cost monotonicity

#### 9. `BernoulliToy.lean`
- `bernoulliLambdaStar`: Closed-form optimal lambda
- `bernoulliFreeEnergyAtLambdaStar`: Free energy at lambda*
- `bernoulliTotalCorrelationAtLambdaStar`: Total correlation at lambda*

## Proof Strategy

### Phase 7.1: Foundational Setup (Easy)

**Target**: Prove the theorems in `Constructive.lean` that rely on basic analysis and probability.

**Dependencies**: Mathlib's `Analysis.SpecialFunctions.Ln`, `Analysis.NormedSpace.Vector`, `Data.Real.Complex`, `Analysis.Calculus.ContDiff`.

**Proof Strategy**:
1. `klNonNeg`: Use the standard proof that KL divergence = ∫ p log(p/q) ≥ 0 via non-negativity of log.
2. `logSumExpBound`: Prove using concavity of log and Jensen's inequality.
3. `jensenConvex`: Directly apply Mathlib's `Convex.jensen` lemma.
4. `maxEntropyUniform`: Use Lagrange multipliers or the fact that uniform maximizes entropy on a finite set.

**Timeline**: 1-2 weeks for an expert.

### Phase 7.2: Information Theory Foundations (Medium)

**Target**: Establish properties of KL divergence, entropy, and mutual information in `FreeEnergy.lean`.

**Dependencies**: Mathlib's `MeasureTheory`, `ProbabilityTheory`, `InformationTheory` (if available).

**Proof Strategy**:
1. Connect our `kl` definition to Mathlib's `KL_divergence`.
2. Prove non-negativity of KL using the standard argument.
3. Establish relationship between entropy, cross-entropy, and KL.
4. Define mutual information as KL between joint and product of marginals.

**Challenges**: Mathlib's information theory library may not be fully developed. May need to build necessary infrastructure.

**Timeline**: 2-4 weeks.

### Phase 3: Main Entanglement Decomposition (Hard)

**Target**: Prove the central `entanglementDecomposition` theorem in `Decomposition.lean`.

**Dependencies**: 
- Free energy definitions
- Total correlation (multi-information)
- Marginalization operations
- KL divergence chain rule
- Measure theory (Fubini's theorem)

**Proof Strategy**:
1. Expand variational free energy expression as in the manuscript.
2. Use Fubini's theorem to interchange sums/integrals.
3. Apply KL chain rule to decompose joint entropy.
4. Show that the total correlation term arises naturally from the difference between joint and marginal entropies.

**Key Lemma**: `totalCorrelation_def`: `I(p) = KL(p || ∏ marginals)`.

**Challenges**: This is the most complex proof in the project, requiring measure theory and careful analysis of the decomposition.

**Timeline**: 1-2 months.

### Phase 7.4: Geometry and Exponential Families (Medium-Hard)

**Target**: Prove results in `Geometry.lean` about e-geodesics and exponential families.

**Dependencies**:
- Information geometry (Fisher information, e-connection)
- Exponential family theory
- Differential geometry (manifolds, connections)

**Proof Strategy**:
1. Define exponential family using Mathlib's `ExponentialFamily` structure if available.
2. Prove that the family {q_λ} is an exponential family.
3. Show that the curve λ ↦ q_λ is an e-geodesic by verifying the geodesic equation.
4. Compute Fisher information and show it's positive definite.

**Challenges**: Requires differential geometry library in Mathlib, which may be limited.

**Timeline**: 1 month.

### Phase 7.5: Spectral Properties (Medium)

**Target**: Prove Schmidt rank and tensor train rank results in `Spectral.lean`.

**Dependencies**:
- Linear algebra (singular value decomposition)
- Tensor products
- Matrix rank properties

**Proof Strategy**:
1. Define Schmidt rank using singular values of the joint matrix.
2. Prove that Schmidt rank = 1 iff the distribution is a product state.
3. Define tensor train rank using tensor network decomposition.
4. Show bounds on tensor train rank in terms of coupling structure.

**Challenges**: Need to formalize singular value decomposition and tensor operations in Mathlib.

**Timeline**: 2-3 weeks.

### Phase 7.6: Heterogeneous Inference (Medium)

**Target**: Prove complexity results for tree-structured coupling in `Heterogeneous.lean`.

**Dependencies**:
- Graph theory (trees, factor graphs)
- Complexity theory
- Belief propagation algorithms

**Proof Strategy**:
1. Model the coupled factor graph as a tree.
2. Show that belief propagation runs in linear time on trees.
3. Extend to loopy graphs with approximations.

**Challenges**: Requires formalizing graph algorithms and complexity bounds.

**Timeline**: 3-4 weeks.

### Phase 7.7: Monotonicity Results (Medium)

**Target**: Prove monotonicity of free energy and coupling cost in `Monotonicity.lean`.

**Dependencies**:
- Convexity/concavity of free energy in λ
- Properties of e-geodesics
- Jensen's inequality

**Proof Strategy**:
1. Show that free energy is convex in λ along the e-geodesic.
2. Use derivative analysis to prove monotonicity.
3. Apply to specific coupling potentials.

**Challenges**: Requires careful analysis of derivatives and convexity.

**Timeline**: 2 weeks.

### Phase 7.8: Bernoulli Toy Model (Easy)

**Target**: Derive closed-form expressions in `BernoulliToy.lean`.

**Dependencies**:
- Basic algebra and calculus
- Properties of logarithms and exponentials

**Proof Strategy**:
1. Write down the joint distribution for K=2 Bernoulli.
2. Compute marginals, free energy, total correlation explicitly.
3. Find λ* that minimizes free energy by solving derivative = 0.
4. Verify second-order conditions.

**Timeline**: 1 week.

## Dependencies Graph

```
Foundational (7.1) → Information Theory (7.2) → Main Decomposition (7.3)
      ↓
Geometry (7.4) → Spectral (7.5) → Heterogeneous (7.6)
      ↓
Monotonicity (7.7) → Bernoulli Toy (7.8)
```

## Required Mathlib Developments

To complete Phase 7, the following Mathlib components would ideally be available or need to be developed:

1. **Information Theory**: KL divergence, mutual information, total correlation, conditional KL
2. **Measure Theory**: Fubini's theorem, product measures, integration
3. **Probability Theory**: Expectation, variance, distributions
4. **Differential Geometry**: Manifolds, connections, geodesics, Fisher information
5. **Linear Algebra**: Singular value decomposition, tensor products, matrix rank
6. **Convex Analysis**: Convex/concave functions, Jensen's inequality
7. **Real Analysis**: Differentiation, integration, Taylor series

## Recommendations

Given the enormous scope, we recommend:

1. **Immediate Goal**: Prove the foundational theorems in `Constructive.lean` and establish basic properties of KL divergence and entropy.
2. **Medium-Term Goal**: Complete the main entanglement decomposition theorem, as this is the heart of the paper.
3. **Long-Term Goal**: Gradually build out the geometric and spectral theory as Mathlib develops.

## Success Criteria

Phase 7 is complete when:
- All `sorry` markers in the Lean formalization have been replaced with proofs.
- `lake build` succeeds without errors.
- All theorems verify against Mathlib's library.
- The formalization is fully type-checked and ready for publication.

## Next Steps

1. Assign a Lean expert to work on Phase 7.1 (foundational theorems).
2. Begin developing necessary Mathlib infrastructure (information theory, differential geometry).
3. Create a shared repository for Phase 7 proofs to enable collaboration.
4. Set up regular check-ins to review progress and integrate contributions.

---

**This roadmap is a living document.** It will be updated as proofs are completed and new dependencies are identified.

**Last Updated**: 2026-05-04  
**Next Review**: 2026-05-18