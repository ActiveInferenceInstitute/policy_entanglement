# Open Theoretical Questions

A list of well-defined open problems, each suitable for focused investigation.

## Existence and uniqueness of lambda*

**Q1.** Under what general conditions on $J, K_c$ is $F[q_\lambda]$ convex on $[0, \infty)$? [[THMREF:thm_4_3]] gives a sufficient condition (log-concavity); is there a tight characterization?

**Q2.** For non-convex $F$, what are the bifurcation structures of $\lambda^*$ as $J, K_c$ vary? Conjecture: cusps and Hopf-like bifurcations on a finite-codimensional set in potential-space.

## Universality classes

**Q3.** Different choices of $J$ (sparse pairwise, low-rank, hierarchical) give qualitatively different phase diagrams. Is there a universality classification of policy entanglement, analogous to the classification of phase transitions in statistical mechanics?

## Continuous-state extensions

**Q4.** The framework as stated is for finite $\Pi^k$. The continuous case (e.g., motor torques, continuous attention) requires Gaussian/copula extension. Is there a clean analogue of [[THMREF:thm_4_1]] for Gaussian-coupled policies? Gaussian copula structure suggests yes; details to be worked out.

## Identifiability

**Q5.** Given observed agent behavior, can we identify $J, K_c, \lambda$? Unique up to gauge transformations (e.g., adding a mean-field-decomposable term to $J$ has no observable effect)? Identifiability conditions for active inference parameters are an active topic [@schwartenbeck-friston-2016]; the entangled extension introduces new parameters with their own identifiability questions.

## Connection to free energy of free energy

**Q6.** Updating $\lambda$ by gradient descent on $F[q_\lambda]$ is itself a meta-inference. Does this admit a free-energy-of-free-energy interpretation, and does it close into a self-consistent variational hierarchy? The "infinite regress" question is well-known in AIF; we conjecture that the entanglement framework provides a *finite-rank* truncation of the regress, with the bond dimensions of the tensor-train representation indexing the depth of belief-about-belief.

## Algorithmic complexity

**Q7.** Coordinate-descent inference on coupled factor graphs ([[SECREF:heterogeneous.coupled]]) has known complexity for tree-structured $J$. For loopy $J$, complexity is the standard belief-propagation question. Is there a tensor-train-aware inference algorithm specialized to policy entanglement that strictly dominates generic loopy BP?

## Connection to graph neural networks

**Q8.** Coupled policy inference is structurally a message-passing computation on the coupling graph. Does this admit a GNN-style implementation that learns $J, K_c$ end-to-end from environment interactions? This would be the *learning-to-couple* version of the framework, with potential for industrial-scale applications.

## Quantum analogue

**Q9.** The Schmidt-rank machinery is borrowed directly from quantum many-body theory. Is there a meaningful *quantum* policy entanglement that goes beyond the formal analogy — e.g., for quantum-mechanical agents in the spirit of the scale-free / RG-AIF framework [@friston-2024]? This is speculative but conceptually clean.

## Connection to integrated information theory

**Q10.** Total correlation is one of several measures of informational integration. Is there a connection between $I(q_\lambda)$ and the integrated information $\Phi$ of IIT [@tononi-2008]? Both quantify the "more-than-the-sum-of-parts" content of a system; the framework gives a candidate operationalization in the policy-inference setting.

## Cognitive integrity / adversarial robustness

**Q11.** The Cognitive Integrity Framework (DAF, in the AII research program) considers robustness of cognition to adversarial perturbations. Does the entanglement framework provide robustness guarantees, e.g., bounds on how much $q_\lambda$ can be perturbed by adversarial $J$ deformations? This is the "cognitive security" version of robustness theory in entangled systems.

---
