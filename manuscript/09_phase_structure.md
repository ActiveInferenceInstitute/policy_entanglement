# Phase Structure and Symmetry Breaking

## Phase diagram

Sweep $\lambda$ for fixed $J, K_c$. Three generic regimes:

**(I) Disordered phase, $\lambda < \lambda_c^{(1)}$.** Schmidt rank $r(q_\lambda) = $ rank of marginal product. Total correlation $I$ small. Behavior dominated by per-stream posteriors. *Cognitive analogue: dissociated streams; absent-minded multitasking.*

**(II) Mixed phase, $\lambda_c^{(1)} < \lambda < \lambda_c^{(2)}$.** Schmidt rank intermediate. Total correlation grows. Several archetypal modes have comparable weight. *Cognitive analogue: flexible coordinated behavior; the "sweet spot" of skilled multi-stream activity.*

**(III) Frozen phase, $\lambda > \lambda_c^{(2)}$.** Schmidt rank collapses to small number; one or a few archetypes dominate. Total correlation high. Behavior approaches pure archetypal joint policies. *Cognitive analogue: rigid habits, automatized routines, possibly compulsive behaviors.*

A schematic phase band along $\lambda$ with illustrative thresholds
$(\lambda_c^{(1)}, \lambda_c^{(2)}) = ([[VAR:phase_lambda_c1]], [[VAR:phase_lambda_c2]])$
for the K=2 Ising toy is shown below; the actual thresholds are
model-dependent and arise from sign-changes of the free-energy
curvature in
[`src/lean/bernoulli_toy.py`](../src/lean/bernoulli_toy.py).
The companion alignment $\alpha(\lambda) = \tanh(\lambda/2)$ takes the
sentinel values
$\alpha(0.5) = [[VAR:ising_alignment_at_lam_05:.4f]]$,
$\alpha(1) = [[VAR:ising_alignment_at_lam_1:.4f]]$,
$\alpha(2) = [[VAR:ising_alignment_at_lam_2:.4f]]$,
$\alpha(3) = [[VAR:ising_alignment_at_lam_3:.4f]]$.

[[FIG:phase_diagram]]

The 2-D analogue across $(\lambda, \mathrm{utility})$ shows the same
three-regime structure as the utility surplus $\Delta_{\mathrm{util}}$
varies; the colour minimum at each utility traces the locus
$\lambda^\star(\Delta_{\mathrm{util}})$ derived in [[SECREF:examples]] ([[EQREF:optimal_lambda]]).

[[FIG:phase_landscape]]

## Order parameters

Two natural order parameters:

- **Largest gap:** $\Delta(\lambda) = s_1 - s_2$ in the spectral decomposition. Small in (I), peaks in (III), discontinuities at phase transitions.
- **Effective rank:** $r_{\mathrm{eff}}(\lambda) = e^{S_E(q_\lambda)}$. Smooth indicator of phase.

## Predictions and connections to clinical phenomena

The framework predicts that:

- *Compulsive disorders* correspond to rigid coupling — high $\lambda$ regime, Schmidt rank near 1, behavior collapses onto a single archetypal joint policy.
- *Disorganized (e.g., severe ADHD, dissociative) phenotypes* correspond to insufficient coupling — $\lambda$ too low, $I(q_\lambda)$ near zero, streams dissociated.
- *Skilled adaptive behavior* corresponds to middle-regime $\lambda \sim \lambda^*$ with rich but not collapsed entanglement spectrum.

These map onto existing computational psychiatry hypotheses about precision dysregulation [@friston-2014; @adams-2013] and habit-vs-deliberation balance [@doll-2015], with the added precision that the framework now tells you *which precision parameter* is dysregulated (the coupling precision $\lambda$, not per-stream precision $\gamma_k$).

---
