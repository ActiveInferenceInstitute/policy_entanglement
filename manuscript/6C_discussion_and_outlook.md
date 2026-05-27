# Discussion and Outlook: Worldview, Live Artifact State, and Limitations

## What the framework commits to

The framework commits to: (i) finite, discrete-time POMDP active inference as the home setting; (ii) mean-field as the *baseline*, not the *target*; (iii) coupling structure as a *learnable hyperprior*, not a hand-engineered architectural choice; (iv) revertibility — any coupled habit can be marginalized to its mean-field component — as a non-negotiable property; (v) information geometry as the natural language for parametric extensions of variational families.

## What the framework declines to commit to

The framework does *not* commit to: (i) embodiment as the primary structuring principle; the same finite-policy formalism can be applied to robots, brains, institutions, or colonies only after a modeler has chosen the relevant streams and boundaries; (ii) any specific neural implementation; the message-passing structure ([[SECREF:heterogeneous.coupled]]) is biologically suggestive but optional; (iii) any specific coupling potential structure; sparse, low-rank, hierarchical, or learned-tabular are all admissible.

## The parametric-entanglement worldview

Structural couplings between behavioral streams are treated as learned hyperpriors rather than architectural commitments. The framework operationalizes this stance with a single dial ($\lambda$) and a single mathematical object (the coupling potential $J$) that together determine *how much* and *what kind* of cross-stream coordination an agent learns to express.

The design sits on a three-point spectrum rather than a single opposition:

- **Modular embodiment.** Build separate controllers for separate functions; engineer a translation layer between them. Costs: the translation layer is the alignment problem in microcosm; the modular boundaries are not learnable.
- **Joint enumeration.** Treat the joint policy as monolithic; suffer the combinatorial cost. Costs: doesn't scale; loses interpretability.
- **Parametric entanglement (this manuscript).** Marginal-preserving, structure-permitting, geometrically principled, and machine-checkable where the claim is algebraic or formally witnessed, with broader biological readings kept hypothesis-labeled.

## Relation to the Free Energy Principle and active-inference process theory

The contribution is best read as a local refinement of active
inference, not as a competing global principle.  The Free Energy
Principle supplies the broader variational story: adaptive systems can
be modeled as maintaining beliefs and actions that keep their sensory
states within viable bounds by optimizing variational free energy
[@friston-2006; @friston-2010; @buckley-2017; @ramstead-2018].
Active inference supplies the process theory: finite agents carry
generative models, update beliefs, and select policies by expected
free energy [@friston-2017; @parr-friston-2017-uncertainty;
@kaplan-friston-2018; @dacosta-2020; @smith-2022; @parr-2022;
@pezzulo-2024-sentient].
This manuscript operates one level down from those commitments.  It
asks what kind of variational family the policy posterior should be
when an agent has several concurrent streams whose actions are neither
independent nor cheaply enumerable as one monolithic policy.

The empirical status of that broader program should be read
cautiously.  Reviews of predictive coding and active inference report
a growing but still incomplete empirical base, and emphasize that
direct validation requires comparisons against alternative models, not
only successful behavioral fits [@hodson-2024].  The present artifact
therefore treats FEP/AIF as the normative and computational frame in
which the finite-policy posterior is defined.  Its validated results
are theorem rows, generated numerical sidecars, figures, and
validator/PDF gates, not direct evidence for a biological
implementation of the $\lambda$-deformation.

This also fixes the identifiability target for future empirical work.
Estimating $\lambda$ from data would require a model-comparison design
that pits the coupled posterior against a mean-field policy posterior,
alternative structured priors, and ordinary changes in $E$, $C$, $G$,
or policy precision.  A large fitted $\lambda$ would not by itself
identify neural precision, desire, conscious integration, or a clinical
mechanism; it would identify, under the chosen model, residual
cross-stream dependence in policy space.  Conversely, a misspecified
$J$ can make coupling harmful or uninterpretable, so the present
finite binary and pymdp sidecars should be read as controlled
existence-and-stress evidence rather than broad behavioral validation.

That positioning matters for interpretation.  Precision parameters in
active inference weight confidence in beliefs, prediction errors, or
policy preferences; precision-weighting accounts of attention,
salience, action, and psychosis motivate the vocabulary but do not
identify this manuscript's $\lambda$ with a neural gain parameter
[@parr-friston-2017-working-memory; @haarsma-2021; @limanowski-2024].
The coupling
strength $\lambda$ introduced here weights cross-stream policy
dependence.  Precision in active inference itself has multiple roles
across discrete policy selection, continuous sensorimotor control,
attention, and action; $\lambda$ is only a coupling-precision analog
inside the present finite policy posterior.  These roles can interact,
and [[SECREF:open_questions]] flags that interaction as a live
question, but the framework does not collapse one into the other.  A
high-precision stream can still be
weakly coupled to its peers; a strongly coupled ensemble can still
contain uncertain marginals.  This separation is the reason the
decomposition of [[THMREF:thm_4_1]] is useful: it identifies the
free-energy terms attributable to marginal belief quality, coupling
structure, and total correlation separately.

The Markov-blanket literature also helps delimit the claim.  Markov
blankets and particular-physics accounts address how a system is
distinguished from its environment, and why conditional independences
matter for autonomy [@kirchhoff-2018; @friston-2019;
@aguilera-2021; @raja-2021; @menary-gillett-2022].  The present
framework assumes such a modeling boundary has already been chosen and
studies dependence *inside* the agent's policy space.  Multi-agent and
biological readings are therefore hypotheses generated by the
mathematics, not conclusions proved by it.  The artifact's current
empirical evidence is finite,
discrete, and pymdp-grounded; the broader FEP reading remains
interpretive unless a paragraph points to a theorem row, a generated
sidecar, a figure, and the relevant validation gate.

## Six load-bearing properties

Each item below is a pointer into a body section.  Together, these
six items constitute the load-bearing properties of the framework:
policy entanglement *classifies* existing architectures as exact,
parametric, or analogical relationships to a common joint-policy
posterior (economy), *explains* when joint structure pays for itself
(decomposition + geometry), *predicts* the small set of dominant
coordination modes a coupled agent expresses (spectral), *bounds* the
suboptimality of mixing reflexive and planning streams
(heterogeneous), and is *auditable* end-to-end against a
stock Lean 4 boundary fragment plus generated numerical artifacts
(formalization).  The framework is therefore positioned as a
candidate model of multi-stream policy inference and an engineering
tool for building agents that
interpolate between modular and joint inference without committing
to either pole.

1. **Theoretical economy.**  A single coupling parameter $\lambda$ exactly recovers the mean-field baseline ([[THMREF:cor_4_3]]) and then organizes the neighboring active-inference variants by claim class: hierarchical AIF is a witness-form concentration analog ([[THMREF:thm_11_1]]), sophisticated inference is a witness-form embedding whose recursive observation-conditioning must be supplied through $J$ ([[THMREF:prop_11_2]]), and branching-time AIF is an algorithmic analogy through policy-tree compression rather than a current head-to-head empirical result.

2. **Decomposition theorem.**  The free-energy decomposition ([[THMREF:thm_4_1]], [[EQREF:tc_decomp]]) factors variational free energy into per-stream marginals, a coupling-potential bundle, and the multi-information $I(q_\lambda) \geq 0$.

3. **Geometric principle.**  The family $\{q_\lambda\}$ traces an e-geodesic away from the mean-field submanifold ([[THMREF:thm_6_4]], [[EQREF:e_geodesic]]); revertibility is the canonical m-projection ([[THMREF:prop_6_2]]); phase structure is symmetry-breaking on the entanglement manifold.

4. **Spectral interpretation.**  Schmidt rank and tensor-train bond dimensions ([[THMREF:prop_7_1]]) give a computable handle on *archetypal eigenvectors* — the dominant cross-stream behavioral modes a coupled agent expresses.

5. **Heterogeneous-ensemble bound.**  The $O(\lambda^2)$ coupling-tax ([[THMREF:thm_8_1]], [[EQREF:coupling_tax_bound]]) bounds the suboptimality of VFE-only streams operating inside EFE-planning ensembles, with a small-$\lambda$ tolerance corollary ([[THMREF:cor_8_2]]).

6. **Lean verification.** The central result — the full S01 free-energy identity ([[THMREF:thm_4_1]]) $F[q_\lambda]=\sum_k F[q^k_\lambda]+\gamma\lambda\langle K_c\rangle+\log Z_E(\lambda)-\lambda\langle J\rangle+I(q_\lambda)$ — is machine-checked in $\mathbb{R}$ by `MathlibProofs.free_energy_decomposition_full` for the genuine entangled posterior ($\log Z_E$ the definitional log-normalizer, positivity/unit-mass proved, the multi-information term discharged through the axiom-clean general-$K$ kernel), with `#print axioms` foundational-only and two independent negative controls. A stock-Lean [[VAR:lean_toolchain_version]] boundary fragment ships the [[VAR:theorem_registry_count]]-row theorem surface as a typed API for the Python computational layer (zero `sorry`, zero axioms beyond stock Lean, zero Mathlib dependency); the per-row content table at [[SECREF:lean_plan]] and the running audit at `docs/reference/veridical_status.md` document what each row certifies in the boundary fragment versus the Mathlib4 discharge target.

## Live state of the artifact

This manuscript is rendered against a real, reproducible run:

* The K=2 Bernoulli closed form is verified to floating tolerance ($\leq [[VAR:param_sweep_agreement_tolerance:.0e]]$ across $[[VAR:param_sweep_grid_points]]$ grid points).
* The [[VAR:pymdp_distribution_version]] grounded harness ([[SECREF:pymdp_harness]]) sweeps $\lambda \in [0, [[VAR:pymdp_sweep_lambda_max:g]]]$ on a $[[VAR:pymdp_sweep_grid_points]]$-point grid; the half-saturation coupling $\lambda_{1/2} \approx [[VAR:pymdp_summary_lambda_at_half_saturation:.3f]]$ locates the half-maximum of total correlation $I_{\max} \approx [[VAR:pymdp_summary_tc_max:.4f]]$ nats.
* The same harness exercises the configured multi-stream ensemble set $K \in \{[[VAR:multi_k_values_list]]\}$ ($I(q_{[[VAR:multi_k_sentinel_lambda:g]]}) \approx [[VAR:multi_information_K3_lambda_2:.4f]]$, $[[VAR:multi_information_K4_lambda_2:.4f]]$, and $[[VAR:multi_information_K5_lambda_2:.4f]]$ nats across the configured $K$ values at $\lambda = [[VAR:multi_k_sentinel_lambda:g]]$), runs a $T = [[VAR:long_horizon_steps]]$-step long-horizon rollout with steady-state KL $[[VAR:long_horizon_steady_state_kl:.4f]]$ and habit-accumulation signal $[[VAR:long_horizon_habit_accumulation:.4f]]$, reports a long-horizon replicate pass rate of $[[VAR:long_horizon_replicate_habit_pass_rate:.2f]]$, and witnesses the $m$-projection revertibility identity $I(q) = D_{\mathrm{KL}}(q\,\|\,\hat m(q))$ to round-off precision ($[[VAR:revertibility_max_kl_residual:.2e]]$ maximum residual across the $[[VAR:revertibility_num_lambdas]]$-point sweep). The revertibility identity is computed by two independent code paths — $I(q)$ via $\sum_k H(q^k) - H(q)$ (`free_energy.total_correlation`) and $D_{\mathrm{KL}}(q\,\|\,\hat m(q))$ via direct $\sum_\pi q\log(q/\hat m)$ (`free_energy.kl_divergence`) — whose equivalence is [[THMREF:prop_6_3]] / [[THMREF:thm_4_1]]; the witness-conformance suite (`tests/test_witness_conformance.py`) supplies the complementary discriminating tests against wrong-$q$ inputs.
* The robustness layer adds [[VAR:robustness_scenario_count:.0f]] one-axis scenarios, [[VAR:coupling_ablation_variant_count]] fixed coupling ablations, and [[VAR:interaction_robustness_scenario_count:.0f]] targeted two-axis interaction scenarios.  These rows are supporting stress evidence: the largest two-axis decomposition residual is [[VAR:interaction_robustness_decomposition_residual_max:.2e]], and the null-variant interaction flatline remains at [[VAR:interaction_robustness_null_variant_tc_max:.2e]].
* Every numeric value above flows from a real run via the `[[VAR:<key>]]` token system rooted in [`src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py), with the no-hardcoded-vars CI gate enforced ([[SECREF:pymdp_validation]]).

The discussion claims therefore reduce to the following evidence-and-caveat ledger:

| Discussion claim | What the current artifact shows | Remaining caveat |
|---|---|---|
| $\lambda$ recovers strict mean-field at zero coupling | $\lambda=0$ outer-product tests pass in the pure NumPy layer and the pymdp harness | Continuous-state analogs are outside the current finite-state artifact |
| Coupling creates measurable joint structure | Total correlation rises from $[[VAR:pymdp_total_correlation_lam_0:.6f]]$ to $[[VAR:pymdp_total_correlation_lam_4:.4f]]$ nats on the pymdp sweep | This is a controlled Ising-style task, not a broad behavioral benchmark |
| Structured coupling scales beyond two streams | The configured $K \in \{[[VAR:multi_k_values_list]]\}$ sweeps report nonzero total correlation and bounded tensor-train ranks | Larger stream counts need sparse / tensor-network inference rather than dense enumeration |
| Long-horizon coupling can accumulate habit mass | The $T=[[VAR:long_horizon_steps]]$ rollout reaches tail KL $[[VAR:long_horizon_steady_state_kl:.4f]]$ and habit signal $[[VAR:long_horizon_habit_accumulation:.4f]]$ | The current rollout is deterministic and task-specific |
| Revertibility is operational, not rhetorical | The $m$-projection identity residual is $[[VAR:revertibility_max_kl_residual:.2e]]$ across the revertibility sweep; the witness-conformance suite discriminates against wrong-$q$ inputs separately | Both checks are restricted to the configured finite-policy task family |
| The Lean track is live | All [[VAR:theorem_registry_count]] boundary-fragment theorems ship as a typed API; the central identity is machine-checked in $\mathbb{R}$ by `MathlibProofs.free_energy_decomposition_full` | Typed-API rows on the boundary fragment delegate their analytic payload to the Mathlib4 layer (see [[SECREF:open_questions]] Q14) |
| Stress evidence is supporting, not headline-tuning | One-axis, ablation, two-axis, and seed-diagnostic sidecars expose sensitivity rather than hiding it | The stress suite remains a controlled binary policy task family |

## Alignment and Dysregulation Hypotheses

Beyond the regimes characterized in [[SECREF:phase]], we sketch two
interpretive hypotheses not developed as empirical claims in the
present manuscript.  **Both subsections below carry claim-strength
`hypothesis` per the legend at [[SECREF:app.claim_strength]] — they are
model-generated interpretive frames, not empirical results.  No row in
[[SECREF:app.aif_recovery]] currently promotes either to `empirical`.**

*[claim: hypothesis]* — First, on alignment: the framework
distinguishes *local* (per-stream) policy updates from *global*
(coupling-structure) updates — the distinction between "adjusting what
to do in one situation" and "rewiring how you coordinate across
situations."  Most existing AIF safety analysis focuses on the former.
*Coupling drift across temporal scales* — where $\lambda$ slowly
evolves on a longer timescale than the per-stream beliefs $q^k$ —
defines a candidate failure mode for multi-stream agents: an agent
whose $\lambda$ drifts toward over-coupling (rigid archetypal
behavior) or under-coupling (dissociated streams) would fail in a
different way than one whose per-stream priors are corrupted.  We do
not develop that learning rule in this artifact; we state only the
structural hypothesis and the measurements needed to test it.

*[claim: hypothesis]* — Second, on flourishing: the middle-regime
$\lambda \sim \lambda^*$ corresponds to the *flexibility*
characteristic of skilled, integrated behavior — a candidate
operationalization of distinctions between rigid habit, fragmented
attention, and integrated awareness.  The framework offers an analytic
handle; we do not push the analogy further here, flagging it as a
hypothesis for cross-disciplinary inquiry.  Clinical and consciousness-
science vocabulary in this paragraph is interpretive, not diagnostic:
no row in the variant-recovery ledger of [[SECREF:app.aif_recovery]]
asserts a clinical or phenomenological equivalence.

## Limitations

Limitations a critical reader should track:

- **Scope: finite policy spaces.** The analytical core ([[SECREF:lambda_deformation]]–[[SECREF:spectral]]) assumes finite $\Pi^k$. A Gaussian-copula analog is conjectured for the continuous case ([[SECREF:open_questions]] Q4).
- **Scope: empirical task family.** The [[VAR:pymdp_distribution_version]] grounding exercises the K=2 Ising ensemble plus the multi-K sweep $K \in \{[[VAR:multi_k_values_list]]\}$, $T=[[VAR:pymdp_rollout_steps]]$ and $T=[[VAR:long_horizon_steps]]$ rollouts, the $m$-projection revertibility witness, and the robustness sidecars. The head-to-head Branching-Time AIF baseline and the adversarial-perturbation sweep are now implemented, unit-tested, and run as pipeline stages ([[SECREF:empirical]]; [`../src/simulation/btai_baseline.py`](../src/simulation/btai_baseline.py), [`../src/simulation/adversarial.py`](../src/simulation/adversarial.py)), emitting auditable sidecars; the *full compute-matched BTAI hypothesis test* and a broader adversarial robustness analysis remain author-led future analysis rather than claims established here.
- **Identifiability gauge.** The gauge freedom in $J$ ([[SECREF:open_questions]] Q5) is characterised explicitly as the additive mean-field-decomposable subgroup; the identifiable coupling lives in the quotient. Multi-agent extensions ([[SECREF:open_questions]] Q15) compound the question.
- **Phase-diagram thresholds.** The values $(\lambda_c^{(1)}, \lambda_c^{(2)}) = ([[VAR:phase_lambda_c1:g]], [[VAR:phase_lambda_c2:g]])$ in [[SECREF:phase]] are illustrative; the analytic conditions that determine them (spectral-gap closing / opening on the $\lambda$ trace) are stated in [[SECREF:phase]].
- **Engagement with recent unification efforts.** The Millidge / Champion / de Vries / Nuijten line on EFE derivations and EFE-as-variational-inference is engaged in [[SECREF:connections]] at chapter granularity; a paper-by-paper systematic comparison is tracked as journal-format companion work [@millidge-2021; @champion-2024-reframing; @devries-2025; @nuijten-lukashchuk-2025].
- **Interpretive scope.** Biological, clinical, and alignment language in this manuscript is claim-strength `hypothesis` unless the text points to a formal row, generated artifact, primary citation, or explicit roadmap item; the empirical-status review serves as the cautionary reference [@hodson-2024].

Each item maps to a tractable extension in [[SECREF:open_questions]]. The four-track ledger — prose, Lean companion, Python witness, and test gate — is wired per registry row with `status:` and `faithfulness:` tiers (see [[SECREF:app.claim_strength]] and [`methods_and_assumptions.md`](../docs/reference/methods_and_assumptions.md)); not every row carries a substantive Python re-proof of its analytic payload.

## Threats to validity

The reviewer-facing threat model has five parts. The *numerical
threat* is finite precision: the pymdp/JAX path and the NumPy
analytical path use different floating formats, so residual claims
are tolerance-bounded and validated artifact-by-artifact; a verified
error-bounded Float$\leftrightarrow\mathbb{R}$ bridge linking the
    $\mathbb{R}$-level proofs to the Float pipeline (Flocq-style formal
    IEEE-754 [@ieee-754-2019; @boldo-melquiond-2011] or interval
    arithmetic) is the natural formal sibling of
the present dashboard-invariant binding, and remains the one open
verification-stack residual (route map and the specific Mathlib4
lemmas required: `docs/reference/methods_and_assumptions.md`). The
*implementation-link threat* is that the Python code is not extracted
from Lean: it is an independently implemented numerical companion
whose coherence with the theorem surface is enforced by registries,
token resolution, generated sidecars, and tests, not by a verified
compiler. The *package-version threat* is dependency drift:
`inferactively-pymdp==[[VAR:pymdp_distribution_version]]` (the package that provides the pymdp
import/API) and Lean [[VAR:lean_toolchain_version]] are part of the claim surface, and
release readiness depends on regenerating the sidecars, PNG metadata,
rendered manuscript, PDF, and regression reports under those pins. The
    *publication-metadata threat* is metadata drift: the public
    Zenodo DOI and public source archive at
    `https://github.com/ActiveInferenceInstitute/policy_entanglement` must
    stay aligned across `manuscript/config.yaml`, `CITATION.cff`, the
    manuscript citation entry, and rendered PDF front matter. The
    *interpretive threat*
is overextension: biological,
clinical, and alignment language is claim-strength `hypothesis` unless
the text points to a formal row, generated artifact, primary citation,
or explicit roadmap item.

## Verification ledger

Every load-bearing claim of the manuscript is established by one or
more of the following five substrates, with a per-claim assignment
that a reader can use to navigate from prose to evidence:

| Claim | Substrate | Where it lives |
|---|---|---|
| The free-energy decomposition identity ([[THMREF:thm_4_1]]) holds for the genuine entangled posterior | Lean $\mathbb{R}$-level proof | `MathlibProofs.free_energy_decomposition_full` (foundational-only `#print axioms`, two negative controls) |
| The multi-information $I(q) \geq 0$ with equality iff $q$ is mean-field | Lean $\mathbb{R}$-level proof | `MathlibProofs.entanglement_decomposition_generalK`; standalone-named form `MathlibProofs.multiInformation_nonneg_at_joint` |
| Per-stream marginals $q^k$ are strictly positive on a strictly-positive joint | Lean $\mathbb{R}$-level proof | `MathlibProofs.streamMarginal_pos` (the analytic precondition for the bridge identity above) |
| The $\lambda=0$ mean-field reduction ([[THMREF:cor_4_3]]) | Lean stock-Lean boundary fragment, `proved` substantive | `Decomposition.couplingLogWeight_pointwise_at_zero` |
| The coupling-verdict decision procedure ([[THMREF:cor_4_2]]) is sound | Lean stock-Lean boundary fragment, `proved` substantive | `Decomposition.couplingVerdict_correct` |
| The four-term decomposition shape locks the parameter-threading discipline | Lean typed-API contract | [[VAR:theorem_status_boundary_count]] boundary + [[VAR:theorem_status_witness_count]] witness-form rows in [[SECREF:lean_plan]] |
| The closed-form K=2 Bernoulli total correlation matches the finite-$N$ Monte-Carlo estimator within a $\sqrt{N}$ band | Python numerical witness | `tests/test_bernoulli_toy.py` |
| The $m$-projection revertibility identity holds across the configured sweep | Two-route Python computation + dashboard invariant | `free_energy.total_correlation` vs `free_energy.kl_divergence`; `decomposition_lhs_eq_rhs_max_residual` |
| Discrimination against wrong-$q$ inputs | Python witness-conformance suite | `tests/test_witness_conformance.py` |
| The pymdp harness emits the full free-energy bundle at every $\lambda$ | [[VAR:pymdp_distribution_version]] grounded run + token system | `[[VAR:<key>]]` injection through `src/simulation/hyperparameters.py` |
| The $O(\lambda^2)$ coupling-tax bound on heterogeneous ensembles ([[THMREF:thm_8_1]]) | Analytic prose proof + numerical envelope verification | [[SECREF:heterogeneous]] + [[SECREF:empirical]] $[[VAR:coupling_tax_grid_points]]$-point sweep |
| Every numeric value in the rendered manuscript comes from a real run | CI gate | `scripts/validate_manuscript.py` no-hardcoded-vars + `[[VAR:...]]` resolver |
| Every Lean source block in the rendered manuscript is a live extraction | CI gate | `src/manuscript/lean_extract.py` + dangling-token failure mode |
| Every registry theorem row has a Lean companion and a four-track wiring check | Per-row registry + four-track validator | `manuscript/refs/labels.yaml` + cross-reference tests; Python witnesses are faithfulness-tiered, not uniformly substantive re-proofs |
| dashboard invariants pass on every build | Numerical regeneration gate | `scripts/run_all.py` final stage |
| The alignment / dysregulation hypotheses do not assert clinical equivalence | Claim-strength tag `hypothesis` | [[SECREF:app.claim_strength]] legend; [[SECREF:app.aif_recovery]] promotion gate |

A referee who reads only this table can locate
the substrate of every assertion of the manuscript without
traversing the body chapter graph.

## Open directions

The verified $\mathbb{R}$ formal core and the four-track empirical artifact leave a small, explicitly-scoped set of open directions. Each is tracked in an existing section above or in the appendices rather than asserted as a commitment here; the head-to-head Branching-Time AIF baseline and the adversarial-perturbation sweep that were previously listed here are now implemented, unit-tested, and run as pipeline stages ([[SECREF:empirical]]). Likewise, the **Generalized Notation Notation (GNN) bridge** that was previously listed here as a `roadmap` direction now ships as a fifth, structural-and-numerical track ([[SECREF:app.gnn_extension]]): a project-owned parser, a shipped K=2 round-trip (an internal-consistency reduction that reproduces the closed-form mutual-information curve to [[VAR:gnn_roundtrip_max_residual:.2e]] nats — not an independent validation — with a non-vacuous zero-coupling negative control), a Lean typed-contract emitter, and a GNN-sourced manuscript variable, all run in the pipeline. The GNN track reproduces structure and numbers but proves no theorem, so it does **not** amend the four-track *proof* integration claim of [[SECREF:motivation]]; its genuine residuals (a first-class upstream coupling primitive; full-bundle pymdp regeneration) are scoped as open questions at [[SECREF:app.gnn_downstream]].

- **Mathlib4 analytic discharge for the typed-API rows.** Extending `MathlibProofs/` to discharge the analytic payloads behind the [[VAR:theorem_status_witness_count]] witness-tier rows of [[SECREF:lean_plan]] — finite KL / entropy chain rules ([[THMREF:prop_6_3]], [[THMREF:prop_6_5]], [[THMREF:prop_11_3]]); convexity / Taylor envelopes ([[THMREF:thm_4_3]], [[THMREF:prop_10_1]]); Bregman / quadratic envelope ([[THMREF:thm_8_1]], [[THMREF:cor_8_2]]); rank and spectral continuity ([[THMREF:prop_7_2]], [[THMREF:thm_7_3]]); concentration and recursive embedding ([[THMREF:thm_11_1]], [[THMREF:prop_11_2]]) — is open theoretical work, tracked at [[SECREF:open_questions]] and the claim-strength roadmap of [[SECREF:app.reference_tables]]. The central result ([[THMREF:thm_4_1]]) is already discharged in $\mathbb{R}$ by `MathlibProofs.free_energy_decomposition_full` (see the *Verification ledger* above); this direction extends that discharge to the remaining witness-tier analytic payloads.

- **Float$\leftrightarrow\mathbb{R}$ formal bridge.** The single open verification-stack residual — a Flocq-style IEEE-754 [@ieee-754-2019; @boldo-melquiond-2011] or interval-arithmetic bound linking the $\mathbb{R}$-level proofs to the Float pipeline — is stated under *Threats to validity* above, with the route map and the specific Mathlib4 lemmas at `docs/reference/methods_and_assumptions.md`.

- **Cross-repository reproducibility.** Aligning this project's `manuscript_variables.json` token schema with the registries used by sister projects would enable shared reproducibility audits across manuscripts; this is minor infrastructure, orthogonal to the framework's claims.

- **Community contribution and archival metadata.** The working citation
  entry [@friedman-2026-actinf-policy-entanglement] is the current
  citation target; the public Zenodo DOI and source repository are recorded
  in `manuscript/config.yaml` and `CITATION.cff`. The open questions of
  [[SECREF:open_questions]] each admit independent contribution.

---
