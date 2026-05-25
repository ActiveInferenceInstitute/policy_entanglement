# Open Theoretical Questions: Analytical Gaps, Identifiability, Empirical Frontiers, and Practical Research Directions

A list of well-defined open problems, each suitable for focused
investigation.  The questions are grouped by methodological
character — analytical, identifiability / inference, empirical,
conceptual / cross-disciplinary, practical / formalization — and
each carries an explicit statement, conjecture (where we have one),
and a pointer to the section it would extend.

## Where to start

For a contributor choosing an entry point, the highest-leverage
items by category are:

- **Q1 (uniqueness of $\lambda^\star$) — analytical, highest-leverage.**
  Convexity of $F[q_\lambda]$ on $[0, \infty)$ governs whether the
  framework's central control parameter is *learnable* by ordinary
  gradient descent on free energy. A positive resolution promotes a
  large fraction of the typed-API theorems in [[SECREF:lean_plan]]
  from analytic-boundary contracts to substantive proofs in the same
  Mathlib4 layer, because the dispersion-comparison inequality
  reformulated in Q1 is the missing analytic content.
- **Q5 (gauge freedom in $J$) — identifiability, necessary
  preparation.** No empirical fitting of $\lambda$, $J$, or $K_c$ to
  observed behavior can proceed until the gauge orbit is
  characterised; this is the bottleneck for *any* identifiability
  result downstream.
- **Q14 (Mathlib4 analytic discharge) — practical, immediate
  follow-on.** The central result is discharged at $\mathbb{R}$-level
  by `MathlibProofs.free_energy_decomposition_full`; the open question
  is the Mathlib4 abstraction layer for the remaining typed-API rows.

Beyond these three, **Q4 (continuous-state extension)** is the
single highest-impact scope-broadening item, **Q9 / Q10** are
incrementally extendable by writing new pymdp scenarios against the
existing harness, and **Q15 (multi-project coupling)** is the
right entry point for a contributor whose interest is multi-agent.

## How to read each question

A few orientation notes for readers triaging which question to
attack.  The **analytical** questions Q1–Q4 are the ones whose
resolution would most directly extend the manuscript's theorem suite;
of these, Q1 (uniqueness of $\lambda^\star$) is the highest-leverage
because convexity directly governs whether optimal coupling is
*learnable* by gradient on free energy.  The **identifiability /
inference** questions Q5–Q8 concern statistical and algorithmic
contracts the framework currently leaves open; Q5 (gauge freedom in
$J$) is necessary preparation for any empirical fitting.  The
**empirical** questions Q9–Q10 stress-test the framework on richer
ensembles than the K=2 Ising toy; the current harness ships initial
answers for both (long-horizon habit accumulation across
$T = [[VAR:long_horizon_steps]]$ steps; revertibility identity to
floating-point tolerance),
so the Q9 and Q10 entries below are reframed as the next-order
follow-ons those initial witnesses make precise.  The **conceptual / cross-disciplinary** questions
Q11–Q13 connect the framework to adversarial robustness, integrated
information, and quantum analogs.  The **practical /
formalization** questions Q14–Q15 are the engineering prerequisites
for the Mathlib4 analytic-discharge plan ([[SECREF:lean_plan]]).

## Analytical questions

**Q1 — Existence and uniqueness of $\lambda^\star$.**
Using the closed-form identity [[EQREF:closed_form_F]] and its second
derivative [[EQREF:d2F_dlambda2]], convexity of $F[q_\lambda]$ on
$[0,\infty)$ reduces to the *dispersion-comparison inequality*
[[EQ:dispersion_comparison]],
a crisper characterization than [[THMREF:thm_4_3]]'s "log-concavity of
$J - \gamma K_c$".

*Why the reformulation holds.* On $\lambda \in [0, \infty)$ where
$Z_E(\lambda)$ and $Z(\lambda)$ are finite and strictly positive
(automatic for finite policy spaces with bounded $J$, $K_c$), the
log-partition $\log Z(\lambda)$ is the cumulant-generating function
of $J - \gamma K_c$ under the $\lambda$-tilted base measure
$\propto E_{\mathrm{MF}}\,\exp(\lambda(J-\gamma K_c))$, so
$\partial_\lambda^2 \log Z(\lambda) = \mathrm{Var}_{q_\lambda}(J - \gamma K_c)$
is the variance under the entangled posterior. The matching log-prior
partition gives
$\partial_\lambda^2 \log Z_E(\lambda) = \mathrm{Var}_{\mathcal{E}_\lambda}(J)$,
and [[EQREF:d2F_dlambda2]] unfolds to the difference
$\partial_\lambda^2 F[q_\lambda] = \mathrm{Var}_{\mathcal{E}_\lambda}(J) - \mathrm{Var}_{q_\lambda}(J - \gamma K_c)$
*pointwise on the domain where both cumulant-generating functions are
finite*. Convexity of $F$ in $\lambda$ on that domain is therefore
*equivalent* to the dispersion-comparison inequality
[[EQREF:dispersion_comparison]], not
merely implied by it; uniqueness of any interior $\lambda^\star$
follows from strict convexity, i.e. strict inequality on the open
interval.

*Conjecture* (sharpened): when $E_{\mathrm{MF}}$ is uniform and
$K_c \equiv 0$, the inequality reduces to
$\mathrm{Var}_{\mathcal{E}_\lambda}(J) \geq \mathrm{Var}_{q_\lambda}(J)$ on
the same exponential family, which by Brascamp–Lieb / Bakry–Émery
holds whenever the natural-statistic distribution under the
entangled prior is log-concave [@brascamp-lieb-1976; @bakry-emery-1985]; under that hypothesis
$\lambda^\star$ is unique. Empirically testable via
[`output/data/parameter_sweep.csv`](../output/data/parameter_sweep.csv)
across the registered $J$ families: a measured negative left-hand
side at any sweep point falsifies global convexity for that family.

**Q2 — Bifurcation structure.**
For non-convex $F$, what are the bifurcation structures of
$\lambda^\star$ as $J, K_c$ vary?  *Conjecture*: cusps and Hopf-like
bifurcations on a finite-codimensional set in potential-space.
The dispersion-comparison reformulation of Q1 makes the bifurcation
locus the level set
$\{(\lambda, J, K_c) : \mathrm{Var}_{\mathcal{E}_\lambda}(J) = \mathrm{Var}_{q_\lambda}(J - \gamma K_c)\}$,
codimension-one in the joint $(\lambda, J, K_c, \gamma)$ space —
testable empirically via the [[SECREF:phase]] phase-diagram code.

**Q3 — Universality classes.**
Different choices of $J$ (sparse pairwise, low-rank, hierarchical)
give qualitatively different phase diagrams.  Is there a universality
classification of policy entanglement, analogous to the classification
of phase transitions in statistical mechanics?  Connection to the
RG-AIF mapping ([[SECREF:connections_multi_agent_geometry]])
suggests the tensor-train rank profile is a candidate order
parameter.  *Sharpened conjecture*: the relevant universality class
is determined by the *rank-growth exponent*
$\rho(\lambda) = \mathrm{d}\log r_k(\lambda)/\mathrm{d}\log \lambda$
across the bipartite cuts of [[SECREF:app.tt_inference]], with
distinct exponents for sparse-pairwise / low-rank-MPS / hierarchical
families.

**Q4 — Continuous-state extension.**
The framework as stated is for finite $\Pi^k$.  The continuous case
(motor torques, continuous attention) requires Gaussian / copula
extension.  Is there a clean analog of [[THMREF:thm_4_1]] for
Gaussian-coupled policies?  *Conjecture*: yes — the closed-form
identity [[EQREF:closed_form_F]] survives intact in the
Gaussian-copula setting because both $\log Z_E$ and $\log Z$ remain
finite-dimensional log-partitions of Gaussian exponential families,
provided the covariance structure remains positive-definite throughout
the deformation (a non-trivial condition for $\lambda > 0$); we
believe this holds for moderate $\lambda$ in the regularized Gaussian
copula but a rigorous statement is open.  Under that hypothesis, the
multi-information appearing in the Gibbs decomposition becomes
the negative log-determinant of a copula correlation matrix.

## Identifiability and inference questions

**Q5 — Identifiability.**
Given observed agent behavior, can we identify $J, K_c, \lambda$?

*Gauge group, explicit.* The entangled posterior is invariant under
$J(\pi) \mapsto J(\pi) + f(\pi)$ for any mean-field-decomposable
$f(\pi) = \sum_k f_k(\pi^k)$: such an $f$ contributes a per-stream
log-weight absorbed into the per-stream priors $E_k$, leaving
$q_\lambda$ pointwise unchanged. Writing
$\mathcal{F}_{\mathrm{MF}}(\Pi) := \{f : \Pi \to \mathbb{R} \mid f = \textstyle\sum_k f_k\}$
for the additive group of mean-field-decomposable potentials, the
*identifiable* coupling lives in the quotient
$\mathcal{F}(\Pi)/\mathcal{F}_{\mathrm{MF}}(\Pi)$. For $K=2$ on
$\Pi = \Pi^1 \times \Pi^2$ with $|\Pi^k| = n_k$, the ambient space
$\mathcal{F}(\Pi)$ has dimension $n_1 n_2$ and the mean-field
subspace has dimension $n_1 + n_2 - 1$ (after subtracting the
shared constant), so the identifiable $J$ space has dimension
$(n_1-1)(n_2-1)$ — equal to the dimension of the bipartite
Schmidt-rank ceiling described in [[SECREF:spectral]], which is the
content the framework can recover from joint-action data.

A symmetric identifiability statement holds for $K_c$ under the
same quotient. The scalar $\lambda$ is identifiable on
$[0, \infty)$ from the *strength* of joint structure once the gauge
orbit of $(J, K_c)$ is factored out; model comparison against the
$\lambda = 0$ mean-field posterior is the operational
identifiability test ([[SECREF:discussion]]). Identifiability
conditions for active-inference parameters are an active topic
[@smith-2022; @schwartenbeck-friston-2016]; the entangled extension
introduces new parameters with their own identifiability questions,
and the quotient characterization above is the prerequisite
specification.

**Q6 — Free energy of free energy.**
Updating $\lambda$ by gradient descent on $F[q_\lambda]$ is itself a
meta-inference.  Does this admit a free-energy-of-free-energy
interpretation, and does it close into a self-consistent variational
hierarchy?  The closed-form gradient [[EQREF:dF_dlambda]] suggests a
clean answer: the gradient of $F$ in $\lambda$ is *itself* a
difference of two prior/posterior expectations of the same statistic
$J$, so precision-like learning on $\lambda$ has the same
exponential-family algebraic shape as ordinary precision learning on
$\gamma$.  *Conjecture*: the entanglement framework provides a
*finite-rank* truncation of the regress, with the bond dimensions of
the tensor-train representation indexing the depth of
belief-about-belief, and the closed-form gradient identity extends
recursively (each meta-level adds one $J^{(\ell)}$ statistic and one
$\langle J^{(\ell)}\rangle_{E^{(\ell)}_\lambda} - \langle J^{(\ell)}\rangle_{q^{(\ell)}_\lambda}$
gradient).  This is a formal modeling conjecture, not a current
neural or clinical claim.

**Q7 — Algorithmic complexity.**
Coordinate-descent inference on coupled factor graphs
([[SECREF:heterogeneous.coupled]]) has known complexity by case:

- **Tree-structured $J$ (no cycles in the coupling graph)**: one
  forward-backward sweep on the coupling tree via the standard
  junction-tree algorithm converges in a single pass with
  per-iteration cost
  $\Theta\!\big(K \cdot \max_k |\Pi^k|^2\big)$ — quadratic in the
  largest per-stream support and linear in the tree-edge count.
- **Loopy $J$ (coupling graph with cycles)**: exact inference is
  $\#$P-hard (the partition function is a permanent-class
  computation); loopy belief propagation converges to a fixed point
  of the Bethe free energy without general convergence-or-accuracy
  guarantees, with the gap from the true marginal bounded by the
  Wainwright–Jordan duality on convex relaxations of the marginal
  polytope [@wainwright-jordan-2008].
- **TT-aware ($J$ admits a matrix-product factorization with bond
  dimension $r$)**: exact marginals via tensor-train contraction
  cost $\Theta\!\big(K \cdot r^2 \cdot \max_k |\Pi^k|\big)$ per
  sweep, strictly dominating loopy BP whenever the coupling has
  low-rank tensor-network structure.

The open question is whether a TT-aware inference algorithm
specialized to policy entanglement strictly dominates generic loopy
BP in *practice* (not just in worst-case scaling) when $J$ has the
empirical rank profile recorded in
`output/data/manuscript_variables.json`. The TT-rank profile across
the configured $\lambda$ sweep is the falsification input: if
measured ranks stay bounded across the sweep, the TT-aware path
dominates; if they grow with $\lambda$, generic loopy BP becomes
competitive.

**Q8 — Learning to couple (graph-neural-network connection).**
Coupled policy inference is structurally a message-passing
computation on the coupling graph.  Does this admit a graph-neural-network-style
implementation that learns $J, K_c$ end-to-end from environment
interactions?  This would be the *learning-to-couple* version of the
framework, with industrial-scale applications to multi-agent and
embodied AI.  (Note: the acronym "GNN" is used in [[SECREF:app.gnn_extension]] to mean
*Generalized Notation Notation*, an orthogonal model-description language; the
two meanings are disambiguated at [[SECREF:app.gnn_disambiguation]].)

## Empirical questions

**Q9 — Habit-accumulation dynamics.**
*Initial answer in the current harness* — see
[[SECREF:empirical]]: a deterministic $T = [[VAR:long_horizon_steps]]$-step
coupled rollout at $\lambda = [[VAR:long_horizon_lambda:g]]$ records a
monotone habit-accumulation signal
$[[VAR:long_horizon_habit_accumulation:.4f]]$ and steady-state
$\mathrm{KL}$ bounded by
$[[VAR:long_horizon_tail_kl_window_max:.4f]]$ across the tail window
against its empirical mean.
*Follow-on*: pair the long-horizon rollout with a slow $J$-update
Hebbian rule and ask how the resulting $J$ trajectories interact with
the phase boundaries of [[SECREF:phase]].  *Conjecture* (unchanged):
habits accumulate fastest near the mixed / frozen boundary, where the
system has maximum sensitivity to small coupling-potential
perturbations.

**Q10 — Revertibility under perturbation.**
*Initial answer in the current harness* — the $m$-projection identity
$I(q) = D_{\mathrm{KL}}(q\,\|\,\hat m(q))$ ([[THMREF:prop_6_3]]) holds
numerically to floating-point tolerance ($\le [[VAR:revertibility_max_kl_residual:.2e]]$
maximum residual) across the
$[[VAR:revertibility_num_lambdas]]$-point sweep (see
[[SECREF:empirical]]: maximum $\mathrm{KL}$ residual
$[[VAR:revertibility_max_kl_residual:.2e]]$, maximum marginal
difference $[[VAR:revertibility_max_marginal_diff:.2e]]$).  *Follow-
on*: under environmental perturbations (e.g. adversarial coupling
injection), how robust is the $m$-projection estimator?  This is the
empirical counterpart to Q11.

## Conceptual / cross-disciplinary questions

**Q11 — Cognitive integrity / adversarial robustness.**
Cognitive integrity programs in active inference consider the
robustness of cognition to adversarial perturbations. Does the
entanglement framework provide robustness guarantees — bounds on
how much $q_\lambda$ can be perturbed by adversarial $J$
deformations?

*Initial harness answer (shipped, not a controlled adversarial study).*
The closed-form [[EQREF:closed_form_F]] yields a first-order
Lipschitz bound (to first order in $\varepsilon$, uniformly for
$\lambda \in [0, \lambda_{\max}]$ on any bounded sub-interval)
$\Delta q(\varepsilon, \lambda) \leq \lambda \varepsilon \cdot \mathrm{Var}_{q_\lambda}(J)^{1/2} + O(\varepsilon^2 \lambda^2)$
via the cumulant-generating-function derivative used in Q1's
reformulation [@brascamp-lieb-1976; @barrett-etal-2022-lipschitz-vae].
The adversarial sidecar measures KL drift on a configured
$(\varepsilon,\lambda)$ grid with three $\Delta J$ classes:
(i) rank-one stress aligned with coupling covariance,
(ii) uniformly random norm-$\varepsilon$ perturbations,
(iii) sparse single-cell perturbations.
The gate compares the empirical Lipschitz slope against the
analytical first-order bound and surfaces the large-$\varepsilon$
regime where the linearization is exceeded ([[VAR:adversarial_bound_holds_fraction]], [[VAR:adversarial_empirical_lipschitz]]).
Implementation:
[`../src/simulation/adversarial.py`](../src/simulation/adversarial.py).
A compute-matched adversarial study remains open work.

**Q12 — Connection to integrated information theory.**
Total correlation is one of several measures of informational
integration.  Is there a connection between $I(q_\lambda)$ and the
integrated information $\Phi$ of IIT [@tononi-2008]?  Both quantify
cross-part dependence in different mathematical settings; the
framework gives only a candidate operationalization in the
policy-inference setting.

**Q13 — Quantum analog.**
The Schmidt-rank machinery is borrowed directly from quantum
many-body theory.  Is there a meaningful *quantum* policy
entanglement that goes beyond the formal analogy — e.g. for
quantum-mechanical agents in the spirit of the scale-free / RG-AIF
framework [@friston-2024]?  This is speculative but conceptually
clean and may interact with Q3's universality program.

## Practical / formalization questions

**Q14 — Mathlib4 analytic discharge for the typed-API rows ([[SECREF:lean_plan]]).**
The central result ([[THMREF:thm_4_1]]) is discharged in
`MathlibProofs.free_energy_decomposition_full`, with the
multi-information non-negativity surfaced as the standalone-named
`multiInformation_nonneg_at_joint` (using `streamMarginal_pos` as
the per-stream-marginal positivity precondition); both are on the
foundational-only `#print axioms` audit keystone list. The open
question is the cleanest Mathlib4 abstraction layer to discharge
the analytic payloads of the remaining [[VAR:theorem_status_witness_count]] typed-API rows
([[THMREF:thm_4_3]], [[THMREF:prop_6_5]], [[THMREF:prop_7_2]],
[[THMREF:thm_7_3]], [[THMREF:thm_8_1]], [[THMREF:cor_8_2]],
[[THMREF:prop_10_1]], [[THMREF:thm_11_1]], [[THMREF:prop_11_2]],
[[THMREF:prop_11_3]]) and the boundary-form completion for
[[THMREF:thm_4_2]], using finite KL / entropy chain rules,
convexity / Taylor payloads, semicontinuity / matrix-rank,
tensor-product rank envelopes, and concentration witnesses. A
related question is the *verified* Float$\leftrightarrow\mathbb{R}$
bridge — Flocq-style formal IEEE-754 model or interval arithmetic —
that would formally tie the $\mathbb{R}$-level proofs to the Float
pipeline (currently bound empirically by the dashboard
invariants).

**Q15 — Multi-project coupling.**
What does the framework predict for multi-agent settings —
populations of agents with their own $\lambda$, or hierarchical
agents whose sub-streams are themselves entangled ensembles?  The
[[SECREF:connections_multi_agent_geometry]] mapping is a starting
point; the open question is whether the bookkeeping admits a clean
recursive identity à la [[THMREF:thm_4_1]].

---
