# Phase Structure: Disordered, Mixed, and Frozen Coupling Regimes

**A note on "phase" as language.** On finite policy spaces with
$|\Pi^k|, K < \infty$ the free energy
$F[q_\lambda] = \log Z_E(\lambda) - \log Z(\lambda)$ is *real-analytic*
on $[0, \infty)$ — it is a continuous function of a finite log-partition
sum over a compact policy alphabet, so no non-analyticity is possible.
True non-analyticities (the strict statistical-mechanics sense of
"phase transition") require the thermodynamic limit, i.e.\ $K \to \infty$
or $|\Pi^k| \to \infty$.  Everything in this section therefore concerns
*smooth crossovers* on a finite system, not strict phase transitions; we
use the word "phase" as a *behavioral metaphor* for the qualitative
shifts in policy-posterior structure (Schmidt rank dropping toward $1$,
total correlation saturating, archetypal modes becoming dominant) that
are nevertheless sharp enough to read off the relevant order parameters
in practice.  When we conjecture genuine phase transitions in
[[SECREF:open_questions]] (Q1), we do so explicitly in the
thermodynamic-limit setting.

## Phase diagram

The three regimes below describe the structure of a *single* coupled
ensemble as $\lambda$ varies along its axis, holding the underlying
potentials $J$ and $K_c$ fixed. They should not be conflated with the
*bifurcation* phenomenon mentioned in [[SECREF:decomposition.optimal]]
and [[SECREF:open_questions]] (Q1), which concerns multiple optima of
$\lambda \mapsto F[q_\lambda]$ that arise when $(J, K_c)$ are themselves
incoherent. Phases live along the $\lambda$ axis at fixed potentials;
bifurcations live in the space of potentials at the optimal $\lambda$.

Sweep $\lambda$ for fixed $J, K_c$. Three generic regimes:

**(I) Disordered phase, $\lambda < \lambda_c^{(1)}$.** Schmidt rank $r(q_\lambda)$ equals the rank of the marginal product. Total correlation $I$ small. Behavior dominated by per-stream posteriors. *Model analogy:* weakly coordinated streams. *Behavioral signature to test:* per-stream actions are statistically independent in repeated trials — a reach is uncorrelated with the gaze direction at the moment of reach onset because each stream is sampling its own posterior.

**(II) Mixed phase, $\lambda_c^{(1)} < \lambda < \lambda_c^{(2)}$.** Schmidt rank intermediate. Total correlation grows. Several archetypal modes have comparable weight. *Model analogy:* flexible coordinated behavior; the "sweet spot" of skilled multi-stream activity. *Behavioral signature to test:* a small repertoire of *modes of coordination* alternates from trial to trial — reach-with-saccade-to-target on most attempts, reach-with-saccade-elsewhere on a smaller fraction, etc., each mode internally coherent but the agent retains the option of choosing a different mode under context.

**(III) Frozen phase, $\lambda > \lambda_c^{(2)}$.** Schmidt rank collapses to small number; one or a few archetypes dominate. Total correlation high. Behavior approaches pure archetypal joint policies. *Model analogy:* rigid habits or automatized routines. *Behavioral signature to test:* the same coupled motor program recurs across stimulus contexts — saccade and reach are stereotyped and indivisible; perturbing one stream forces a recompute of the entire joint program rather than a local correction.

A schematic phase band along $\lambda$ with illustrative thresholds
$(\lambda_c^{(1)}, \lambda_c^{(2)}) = ([[VAR:phase_lambda_c1]], [[VAR:phase_lambda_c2]])$
for the K=2 Ising toy is shown below; the actual thresholds are
model-dependent and arise from the analytic conditions stated next.

**Analytic conditions for the phase boundaries.** On a finite system
the boundaries are *crossovers*, not non-analyticities, but each is
characterised by a derivative or gap condition on the
$\lambda$-trace of the spectral and entropic order parameters:

- the *disordered$\,\to\,$mixed* crossover $\lambda_c^{(1)}$ is the
  smallest $\lambda \geq 0$ at which the largest spectral gap
  $\Delta_{\mathrm{spec}}(\lambda) = s_1 - s_2$ of the Schmidt
  decomposition exceeds half the bare gap of the marginal product —
  equivalently, the smallest $\lambda$ at which the effective rank
  $r_{\mathrm{eff}}(\lambda) = e^{S_E(q_\lambda)}$ drops below
  $r_{\mathrm{eff}}(0) - 1$;
- the *mixed$\,\to\,$frozen* crossover $\lambda_c^{(2)}$ is the
  smallest $\lambda$ at which the effective rank drops to within a
  small tolerance of unity, $r_{\mathrm{eff}}(\lambda) \leq 1 + \epsilon$
  for a chosen $\epsilon \in (0, 1)$, equivalently the smallest
  $\lambda$ at which total correlation $I(q_\lambda)$ reaches
  $(1-\epsilon)\,\log K$ (the upper bound).

Both conditions reduce to one-dimensional searches on the spectral
trace produced by
[`src/lean/bernoulli_toy.py`](../src/lean/bernoulli_toy.py): the
illustrative thresholds reflect the $\epsilon = 0.1$ choice on the
K=2 Ising trace and shift continuously with $\epsilon$, the
potentials $J$, $K_c$, and the marginal priors. In the thermodynamic
limit $K \to \infty$, the same gap conditions become genuine
non-analyticities; the conjectured universality classes
([[SECREF:open_questions]] Q3) are indexed by the rank-growth
exponent of $\Delta_{\mathrm{spec}}$ across the bipartite cut at the
lower crossover.
The companion alignment $\alpha(\lambda) = \tanh(\lambda/2)$ takes the
sentinel values
$\alpha(0.5) = [[VAR:ising_alignment_at_lam_05:.4f]]$,
$\alpha(1) = [[VAR:ising_alignment_at_lam_1:.4f]]$,
$\alpha(2) = [[VAR:ising_alignment_at_lam_2:.4f]]$,
$\alpha(3) = [[VAR:ising_alignment_at_lam_3:.4f]]$.

[[FIG:phase_diagram]]

The 2-D analog across $(\lambda, \Delta_{\mathrm{util}})$ exhibits the same
three-regime structure as utility surplus varies; the full $[[VAR:phase_landscape_lambda_points]] \times [[VAR:phase_landscape_utility_points]]$ sampled
free-energy landscape is shown in the empirical suite ([[SECREF:empirical]],
[[FIGREF:phase_landscape]]), where the color minimum at each utility column traces
the VFE-optimal coupling $\lambda^\star_{\mathrm{VFE}}(u)$ — a numerical
quantity that should not be conflated with the alignment-inversion formula
[[EQREF:optimal_lambda]] in [[SECREF:examples]], which inverts the
alignment correspondence rather than minimizing free energy (see the
distinction made explicit in [[SECREF:app.bernoulli]]).

## Order parameters

Two natural order parameters:

- **Largest gap:** $\Delta_{\mathrm{spec}}(\lambda) \;=\; s_1 - s_2$ in the spectral decomposition (distinct from the utility surplus $\Delta_{\mathrm{util}}$ above). Small in (I), peaks in (III), and changes most rapidly near finite-system crossover bands.
- **Effective rank:** $r_{\mathrm{eff}}(\lambda) = e^{S_E(q_\lambda)}$. Smooth indicator of phase.

## Model predictions and behavioral hypotheses

The finite model yields three testable hypotheses for controlled
joint-action tasks.  They are not clinical classifications; each
would require an empirical protocol that estimates $\lambda$, total
correlation, and the coupling-spectrum diagnostics from behavior:

- Rigid, habit-dominated behavior would appear *in the model* as high effective coupling — high $\lambda$ regime, Schmidt rank near 1, behavior concentrated on one archetypal joint policy.
- Poor cross-stream coordination would appear *in the model* as insufficient coupling — $\lambda$ too low, $I(q_\lambda)$ near zero, streams dissociated despite intact per-stream marginals.
- Skilled adaptive behavior would appear *in the model* as middle-regime $\lambda \sim \lambda^*$ with a rich but not collapsed entanglement spectrum.

The mechanism is the same in each case: $\lambda$ controls how much the joint posterior is allowed to depart from the mean-field surface, so a tonic over- or under-shoot of $\lambda$ shifts the archetypal spectrum without necessarily distorting any individual per-stream prior.  The empirical claim is therefore narrower than a clinical diagnosis: under this model, controlled behavioral tasks would test cross-stream correlation (mutual information across modalities, between-trial joint-action repertoire, or coupling-spectrum effective rank) alongside univariate stream metrics, because the coupling account predicts the informative signal should live in the joint statistics.

These hypotheses are adjacent to existing computational psychiatry accounts of precision dysregulation [@friston-2014; @adams-2013] and habit-vs-deliberation balance [@doll-2015].  The contribution here is a candidate coupling statistic $\lambda$ that could be estimated or falsified from joint-action data; it is not evidence, by itself, that any named disorder is explained by coupling drift.

---
