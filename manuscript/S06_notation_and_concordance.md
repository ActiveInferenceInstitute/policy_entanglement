# Notation Concordance: Symbol Registry Across Manuscript, LaTeX, Python, and Lean {- #sec:notation}

This appendix is the **single contract** between the manuscript prose,
the LaTeX preamble macros, the Python source under `src/`, and the
Lean boundary fragment under `lean/`.  Every symbol used in the body
appears here exactly once; columns trace the symbol across all four
tracks so a reader can navigate from prose → code → proof in one
hop.  Empty cells indicate that the symbol does not surface on that
track (e.g. a manuscript-only typographical convention).

The same identifiers also appear in
[`docs/reference/math_reference.md`](../docs/reference/math_reference.md)
and the Python-side identifier inventory in
[`docs/reference/python_api.md`](../docs/reference/python_api.md).

A **fifth, structural-and-numerical track** — Generalized Notation Notation
(GNN) — is shipped and documented in [[SECREF:app.gnn_extension]] and tabulated
in the *GNN fifth-track concordance* subsection at the end of this appendix.
GNN reproduces the framework's structure and numbers (a project-owned parser, a
verified K=2 round-trip, and a Lean typed-contract emitter), but it does **not**
prove theorems; the four-track *proof* contract documented above is therefore
unchanged, and the GNN track is tabulated separately so the two are never
conflated.

### How to read this concordance — one symbol, four tracks

Take the entangled posterior $q_\lambda$, the central object of the
framework.  The four tracks line up as follows:

* **Manuscript prose ([[SECREF:lambda_deformation]]).**
  $q_\lambda(\pi) \propto \prod_k E_k(\pi^k)\,
  \exp\big(\lambda J(\pi) - \gamma G_\lambda(\pi)\big)$.
* **LaTeX preamble ([`preamble.md`](preamble.md)).**  Either spell out
  `q_\lambda` or use the macro `\fe` for the matching VFE operator.
* **Python ([`src/lean/coupling.py`](../src/lean/coupling.py)).**
  ```python
  from lean.coupling import entangled_posterior
  q_lam = entangled_posterior(mf, G, J, Kc, gamma=1.0, lam=2.0)
  # q_lam.shape == (|Π¹|, |Π²|, …, |Π^K|);  q_lam.sum() == 1.0
  ```
* **Lean
  ([`lean/ActinfPolicyEntanglement/Coupling.lean`](../lean/ActinfPolicyEntanglement/Coupling.lean)).**
  ```lean
  def entangledPosteriorLogWeight {α : Type} [Add α] [Mul α] [Sub α] {K Pol}
      (logE : PolicySpace K Pol → α)
      (G : PolicySpace K Pol → α)
      (J K_c : CouplingPotential α K Pol)
      (gamma lam : α) : PolicySpace K Pol → α :=
    fun pi => logE pi - gamma * G pi + couplingLogWeight J K_c gamma lam pi
  ```
* **Numerical witness
  ([`tests/test_coupling.py`](../tests/test_coupling.py)).**  At
  $\lambda = 0$ with symmetric MF prior and zero coupling,
  `entangled_posterior(...) == mean_field_to_joint(mf)` to floating
  tolerance — the proved-form companion of [[THMREF:cor_4_3]].

Reading any row of the tables below in the same fashion lands a
reader on the exact construct on all four tracks.

## Sign conventions {#sec:notation.sign_conventions}

The framework spans variational free energy, expected free energy, KL,
multi-information, coupling, and Schmidt spectra; each carries a sign
convention that the rest of the manuscript silently adheres to.  An
editor or reader who is confused about a sign somewhere in the body
should consult this subsection first.  When the body says "negated $K$"
or "modulo a sign convention", it is invoking one of the conventions
below.

* **Variational free energy.**
  $F[q] = \mathbb{E}_q[\log q - \log \mathcal{E}] + \gamma\,\mathbb{E}_q[G]$.
  $F$ is *non-negative* on the natural domain (Gibbs inequality with
  fixed $\mathcal{E}$) and is the *quantity to be minimized*.  Every
  $F[q_\lambda]$, $F[q^k_\lambda]$, and $\sum_k F[q^k]$ in the
  manuscript follows this sign — *no inverted-sign "ELBO" form appears
  anywhere*; an apparent extra minus in a body equation is a typo, not
  a convention change.
* **Expected free energy.**  $G(\pi) \geq 0$ on the standard
  active-inference decomposition; both the epistemic value and the
  pragmatic value are reported as *negated* quantities so that
  minimizing $G$ corresponds to *maximizing* utility plus information
  gain.  When the body writes "epistemic value, negated" / "pragmatic
  value, negated" (as in [[SECREF:setup.pomdp]]), the negation is
  already absorbed into the sign of $G$ — no further sign-flip is
  needed downstream.
* **Kullback–Leibler divergence.**
  $D_{\mathrm{KL}}(q\,\|\,p) = \mathbb{E}_q[\log q - \log p] \geq 0$,
  *never* reversed.  The first argument is the distribution one is
  drawing from; the second is the reference.  When a derivation appears
  to "swap" the arguments (e.g.\ for variational vs.\ mean-field
  projections), the manuscript spells out the swap explicitly; an
  inferred swap is an error.
* **Multi-information / total correlation.**
  $I(q) = \sum_k H(q^k) - H(q) = D_{\mathrm{KL}}(q\,\|\,\prod_k q^k) \geq 0$.
  Appears with a **PLUS** sign in the decomposition theorem
  ([[EQREF:tc_decomp]]); the body never carries an inverted-sign $I$.
* **Coupling parameter $\lambda$.**  $\lambda \geq 0$ throughout the
  body of the paper.  Negative $\lambda$ would correspond to
  *anti-coupling* (the entangled posterior is pushed *away* from the
  modes of $J - \gamma K_c$) and is out of scope; figures show $\lambda
  \geq 0$ unless otherwise indicated.  In the symmetric K=2 Bernoulli
  toy of [[SECREF:examples.bernoulli]] the closed-form expressions are
  even in $\lambda$ so the sign restriction is harmless; in
  asymmetric cases the restriction is substantive and should be flagged
  if relaxed.
* **Schmidt singular values.**  $s_\alpha \geq 0$ (singular values of a
  real matrix are non-negative).  The spectral distribution
  $p_\alpha = s_\alpha^2/\sum_\beta s_\beta^2$ is obtained by *squaring*
  the singular values and normalizing by their sum-of-squares; this is
  the same normalization used in the quantum-entanglement dictionary
  but applied to the SVD of a *classical-probability* joint, not to
  amplitudes of a state vector.  The analogy with bipartite quantum
  entanglement entropy is *structural*, not literal (see the
  clarification at [[SECREF:spectral.archetypes]] / [@eisert-2010]).
* **Convention on "negated $K$".**  Phrases such as "negated $K$" or
  "modulo a sign convention" elsewhere in the manuscript refer
  collectively to the conventions in this subsection — almost always
  to the EFE-side sign of $K_c$ (which enters $G_\lambda$ with a *plus*
  $\lambda K_c$, contributing $+\gamma\lambda\langle K_c\rangle$ to $F$
  via the $\gamma G_\lambda$ expectation; the *minus*-sign convention
  in some derivations of related work corresponds to a re-definition
  $K_c \to -K_c$).

## Sets, indices, and basic objects

| Symbol | Meaning | LaTeX | Python | Lean |
|---|---|---|---|---|
| $K \in \mathbb{N}$ | Number of policy streams | `K` | `K` (int) | `K : Nat` |
| $k \in \{1,\ldots,K\}$ | Stream index | `k` | `k` (int) | `k : StreamIdx K` |
| $\Pi^k$ | Per-stream policy factor (finite type) | `\Pi^k` (or `\policySpace^k`) | (implicit via array shape) | `Pol k` (in `PolicyFactor K := StreamIdx K → Type`) |
| $\Pi = \prod_k \Pi^k$ | Joint policy space | `\Pi` (or `\policySpace`) | (implicit) | `PolicySpace K Pol` (`∀ k, Pol k`) |
| $\pi = (\pi^1,\ldots,\pi^K) \in \Pi$ | Joint policy | `\pi` (or `\policy`) | flat ndarray index | `pi : PolicySpace K Pol` |
| $\pi^k \in \Pi^k$ | Per-stream policy | `\pi^k` | `pi[k]` | `pi k` |
| $\pi^{-k}$ | Tuple of all policies *other* than stream $k$ | `\pi^{-k}` | (sum-axis param) | (implicit in marginalization) |
| $T_k$ | Planning horizon attached to stream $k$ | `T_k` | per-stream horizon in `StreamSpec` / rollout sidecars | `horizon k` when a `HorizonProfile K` witness is in scope |
| $L$ | Number of hierarchy levels in the hierarchical-AIF structural analogy | `L` | (manuscript-level; no dedicated runtime object) | (witness payload supplied to `ConnectionsWitnesses`) |
| $\ell$ | Hierarchy-level index, used in adjacent-level pairs $(\pi^\ell,\pi^{\ell+1})$ | `\ell` | (manuscript-level; no dedicated runtime object) | (witness payload supplied to `ConnectionsWitnesses`) |
| $d$ | Lookahead depth for sophisticated-inference / branching-style policy stacks | `d` | `lookahead_depth` when an experiment supplies one | (witness payload supplied to `ConnectionsWitnesses`) |
| $\mathcal{V} \subseteq \{1,\ldots,K\}$ | VFE (reflexive) stream indices | `\mathcal{V}` | `[m for m,_ in enumerate(modes) if m == InferenceMode.VFE]` | (implicit via `horizon : HorizonProfile K`) |
| $\mathcal{P} = \{1,\ldots,K\}\setminus\mathcal{V}$ | EFE / planning stream indices | `\mathcal{P}` | (complement) | (implicit) |

## POMDP generative-model symbols

The single-stream POMDP recap of [[SECREF:setup.pomdp]] uses the
classical pymdp / SPM symbols.  These are the inputs to the
`pymdp.agent.Agent` constructor in
[`src/simulation/agents.py`](../src/simulation/agents.py) and the
fields of [`StreamSpec`](../src/simulation/specs.py).

| Symbol | Meaning | LaTeX | Python (`StreamSpec`) | pymdp keyword |
|---|---|---|---|---|
| $A$ | Likelihood matrix (`num_obs × num_states`) | `A` | `spec.A` | `A=` |
| $B$ | Transition tensor (`num_states × num_states × num_controls`) | `B` | `spec.B` | `B=` |
| $C$ | Log-preference vector (`num_obs`) | `C` | `spec.C` | `C=` |
| $D$ | Prior over hidden states (`num_states`) | `D` | `spec.D` | `D=` |
| $o$ | Observation | `o` | `observations[k]` | passed to `infer_states` |
| $s$ | Hidden state | `s` | `states[k]` (in `Rollout`) | output of `infer_states` |
| $u$ | Control / action | `u` | `sampled_actions[k]` | output of policy sampling |
| $T$ | Rollout horizon | `T` | `H.PYMDP_ROLLOUT_STEPS` | (script-level) |
| $P(\cdot)$ | Generic generative-model law in active-inference prose | `P` | stored concretely as `A`, `B`, `C`, `D`, `E` arrays / factors | (not a boundary primitive) |
| $Q(\cdot)$ | Generic variational posterior notation in active-inference prose | `Q` | normalized `q` arrays; `Agent.qs` / `Agent.q_pi` in pymdp contexts | (not a boundary primitive; boundary uses `JointDist`) |

## Distributions

| Symbol | Meaning | LaTeX | Python | Lean |
|---|---|---|---|---|
| $E_k(\pi^k)$ | Per-stream policy prior (habit) | `E_k` | `mf_prior[k]` (per-stream marginal supplied to `entangled_prior` / `mean_field_to_joint`) — **distinct from `StreamSpec.D`, which is the hidden-*state* prior; see the hidden-state-prior row above** | `E : MFDist K Pol` |
| $E_{\mathrm{MF}}(\pi) = \prod_k E_k(\pi^k)$ | Mean-field prior | `E_{\mathrm{MF}}` | `mean_field_to_joint(mf_prior)` | `mfProductWeight` |
| $\mathcal{E}_\lambda(\pi)$ | $\lambda$-entangled prior | `\mathcal{E}_\lambda` | `entangled_prior(...)` | (no Lean — boundary fragment carries only the log-weight via `entangledPosteriorLogWeight`) |
| $G_k(\pi^k)$ | Per-stream expected free energy (EFE) | `G_k` (or `\efe_k`) | `per_stream_efe(spec, obs)[k]` | (consumed as data via `MFDist K Pol`) |
| $G_{\mathrm{MF}}(\pi) = \sum_k G_k(\pi^k)$ | Mean-field EFE | `G_{\mathrm{MF}}` | `sum(per_stream_efe(...))` | (no top-level Lean def; consumed as `MFDist K Pol` argument) |
| $G_\lambda(\pi) = G_{\mathrm{MF}}(\pi) + \lambda K_c(\pi)$ | $\lambda$-coupled total EFE (per-stream EFEs plus preference-side coupling) | `G_\lambda` | (inlined) | (inlined; appears inside `entangledPosteriorLogWeight`) |
| $q(\pi)$ | Joint policy posterior | `q` | `q : ndarray` (joint shape) | `q : JointDist K Pol` |
| $q^k(\pi^k) = \sum_{\pi^{-k}} q(\pi)$ | Per-stream marginal | `q^k` | `joint_marginal(q, k)` | (no Lean — marginalization is inline in `mfToJoint`) |
| $q_\lambda(\pi)$ | $\lambda$-entangled posterior | `q_\lambda` | `entangled_posterior(mf, G, J, K_c, gamma, lam)` / `coupled_policy_posterior(spec, obs, lam)` | `entangledPosterior` / `LogWeight` |
| $q_{\mathrm{MF}}(\pi) = \prod_k q^k(\pi^k)$ | Product of marginals (m-projection of $q$) | `q_{\mathrm{MF}}` | `m_projection(q)` | `mfToJoint` (direction: MF → joint; joint-to-marginal projection is Python-only in the current boundary) |
| $q_t^k$ | Per-stream marginal at rollout time $t$ | `q_t^k` | `rollout.steps[t].mean_field_marginals[k]` | (no Lean) |

## Coupling potentials and parameters

| Symbol | Meaning | LaTeX | Python | Lean |
|---|---|---|---|---|
| $J(\pi)$ | *Habit* coupling potential — prior side | `J` (or `\coupJ`) | `coupling_j` (in `CoupledEnsembleSpec`) | `J : CouplingPotential α K Pol` |
| $K_c(\pi)$ | *Preference* coupling potential — EFE side | `K_c` (or `\coupK`) | `coupling_kc` | `Kc : CouplingPotential α K Pol` |
| $\lambda \in [0,\infty)$ | Coupling parameter | `\lambda` | `lam` (parameter) | `lam : α` |
| $\gamma > 0$ | Policy precision (inverse-temperature on EFE) | `\gamma` | `gamma` (in `CoupledEnsembleSpec`) | `gamma : α` |
| $\gamma_k > 0$ | Per-stream policy precision; collapses to scalar $\gamma$ in homogeneous examples | `\gamma_k` | per-stream `gamma` when a helper supports heterogeneous precision; scalar `gamma` otherwise | (not a separate boundary primitive) |
| $\Delta_{\mathrm{util}} \in [-\Delta_{\max}, \Delta_{\max}]$ | Utility surplus for aligned outcomes (a *substantive payoff* parameter; not a target on the alignment axis) | `\Delta_{\mathrm{util}}` | `delta` argument to `optimal_lambda` | `delta : Float` |
| $\Delta_{\mathrm{align}} \in [-\Delta_{\max}, \Delta_{\max}]$ | Target alignment for the alignment-inversion formula $\lambda^\star(\Delta_{\mathrm{align}}) = 2\,\operatorname{arctanh}(\Delta_{\mathrm{align}}/\Delta_{\max})$; equals $\alpha(\lambda) = \tanh(\lambda/2)$ at the realizing $\lambda$ ([[EQREF:optimal_lambda]]). **Distinct from $\Delta_{\mathrm{util}}$** — alignment-inversion is not the VFE first-order condition. | `\Delta_{\mathrm{align}}` | `delta` argument to `optimal_lambda` (same code path; semantics is alignment, not utility) | `delta : Float` |
| $\Delta_{\max}$ | Saturation point of $\Delta_{\mathrm{util}}$ / $\Delta_{\mathrm{align}}$ (Bernoulli toy: $1$) | `\Delta_{\max}` | `delta_max` argument (default `1.0`) | `delta_max : Float` |
| $\Delta_{\mathrm{spec}}(\lambda) = s_1 - s_2$ | Spectral gap (largest minus second-largest singular value of the bipartite reshape of $q_\lambda$); **distinct from utility surplus and target alignment** | `\Delta_{\mathrm{spec}}` | `schmidt_decomposition(q)[0].weight - schmidt_decomposition(q)[1].weight` (composition form) | (no current Lean SVD companion; Python computes the spectrum) |
| $\lambda^\star(\Delta_{\mathrm{align}})$ | **Alignment-inversion coupling** $= 2\,\operatorname{arctanh}(\Delta_{\mathrm{align}}/\Delta_{\max})$; inverse of the alignment correspondence in the K=2 Bernoulli toy. *Not* a VFE optimum. | `\lambda^\star` (or `\lambda^*`) | `optimal_lambda(delta)` | `optimalLambda` |
| $\lambda^\star_{\mathrm{VFE}}(u)$ | True VFE-optimal coupling under utility scalar $u$; equals $2u$ in the symmetric K=2 Bernoulli toy (see [[SECREF:app.bernoulli]]). Coincides with $\lambda^\star(\Delta_{\mathrm{align}} = u)$ only at small $u$. | (inline) | (derived analytically) | (no Lean) |
| $\lambda_{\mathrm{infl}}$ | **Inflection coupling**: the point in $[0,\infty)$ where $F''$ changes sign exactly once, separating the regime where the agent benefits from *more* coupling (below) from the regime where marginal returns reverse (above) — see [[SECREF:app.convexity]] | `\lambda_{\mathrm{infl}}` | (inline; located where $F''$ changes sign) | (no Lean) |
| $\lambda_c^{(1)},\,\lambda_c^{(2)}$ | Phase-band thresholds (default $([[VAR:phase_lambda_c1:g]], [[VAR:phase_lambda_c2:g]])$) | `\lambda_c^{(1)},\lambda_c^{(2)}` | `H.PHASE_LAMBDA_C1`, `H.PHASE_LAMBDA_C2` | `lambdaC1`, `lambdaC2` |
| $\lambda_{\mathrm{probe}}$ | Small-λ probe for the coupling-tax curvature fit | `\lambda_{\mathrm{probe}}` | `H.COUPLING_TAX_PROBE_LAMBDA` | (no Lean) |
| $J_0$ | Bernoulli / Ising coupling strength (scalar prefactor of the $K=2$ aligned-indicator coupling $J$) | `J_0` | `j0` (closed-form scalar in `bernoulli_toy`) | (no Lean — Bernoulli toy uses `BinaryCoupling`) |
| $\lambda_E,\,\lambda_G$ | Decoupled-parameter form: two-parameter generalization in which the habit-side and EFE-side coupling strengths are independent ($\lambda$ in the body is the symmetric $\lambda_E = \lambda_G$ restriction) | `\lambda_E,\,\lambda_G` | `lam_e`, `lam_g` (parameter overrides) | (no Lean — symmetric `lam : α` only) |
| $\lambda_{1/2}$ | Half-saturation coupling: $\lambda$ at which the alignment correspondence reaches $\Delta_{\max}/2$ | `\lambda_{1/2}` | `manuscript_variables.json[pymdp_summary_lambda_at_half_saturation]` | (no Lean) |
| $\lambda_{\max}$ | Max admissible coupling under small-$\lambda$ tolerance $\varepsilon$ ([[THMREF:thm_8_1]]) | `\lambda_{\max}` | (derived from `SmallLambdaTolerance`) | `SmallLambdaTolerance` / `lambda_max` |
| $\Phi_{kj}$ | Per-pair coupling factor: entry $(k,j)$ of $\Phi$ (the sup-norm $\|\Phi\|_\infty$ already has a row) | `\Phi_{kj}` | (entry of coupling-log-weight matrix) | (no Lean — magnitude consumed via `couplingNormSq_of_trivialCoupling`) |
| $\mathcal{C}$ | Interaction graph: set of coupled stream pairs $(k,j)$ with $\Phi_{kj} \neq 0$ | `\mathcal{C}` | (set / sparsity pattern of coupling) | (no Lean — implicit support of `CouplingPotential`) |
| $J_e$ | Per-clique additive component of $J$ in the tensor-train decomposition (indexed by edge $e \in \mathcal{C}$) | `J_e` | (clique components in `coupling_decomposition`) | (no Lean) |
| $Z(\lambda)$ | Unnormalized posterior partition function; see normalizer note below | `Z(\lambda)` | (implicit in `entangled_posterior`) | (implicit in `entangledPosteriorLogWeight`) |
| $Z_E(\lambda)$ | Normalizing constant of the entangled prior $\mathcal{E}_\lambda \propto (\prod_k E_k)\,e^{\lambda J}$ | `Z_E(\lambda)` | (implicit; sourced from `entangled_prior`) | (no top-level Lean def; implicit in `entangledPosteriorLogWeight`) |
| $\psi(\lambda) = \log Z(\lambda)$ | Posterior log-partition function | `\psi(\lambda)` | (implicit) | (no top-level Lean def; implicit in `entangledPosteriorLogWeight`) |
| $\psi_E(\lambda) = \log Z_E(\lambda)$ | Prior log-partition function | `\psi_E(\lambda)` | (implicit) | (no top-level Lean def; implicit in `entangledPosteriorLogWeight`) |
| $F[q_\lambda] = \log Z_E(\lambda) - \log Z(\lambda)$ | Closed exponential-family form of the entangled VFE (see [[THMREF:thm_4_2]]) | (inline) | `entanglement_decomposition_rhs(...)` (Gibbs form) | (boundary; Lean companion is the algebraic skeleton in `Decomposition.lean`) |
| $\mathrm{mode}_k$ | Inference mode of stream $k$ | `\mathrm{mode}_k` | `InferenceMode.VFE / EFE / SOPHISTICATED` | (manuscript label; no Lean inductive in current boundary fragment — see [Status notes](#status-notes)) |

**Normalizer note.**  $Z(\lambda)$ normalizes the unnormalized
exponential
$E_{\mathrm{MF}}(\pi)\,e^{\lambda(J-\gamma K_c)(\pi)-\gamma G_{\mathrm{MF}}(\pi)}$,
so $q_\lambda(\pi)$ is that numerator divided by $Z(\lambda)$.
It is not $\sum_\pi q_\lambda(\pi)$, which is $1$ by definition. It
is the partition function that appears in the closed identity
$F = \log Z_E - \log Z$ ([[EQREF:closed_form_F]]).

## Information-theoretic quantities

| Symbol | Definition | LaTeX | Python | Lean |
|---|---|---|---|---|
| $H(p) = -\sum p\log p$ | Shannon entropy (natural log) | `H(p)` (or `\Hent(p)`) | `shannon_entropy(p)` | `shannonEntropy` |
| $H_b(p)$ | Binary entropy $-p\log p - (1-p)\log(1-p)$ | `H_b(p)` | (inline) | `binaryEntropy` |
| $D_{\mathrm{KL}}(q \,\|\, p)$ | KL divergence | `D_{\mathrm{KL}}` (or `\KL{q}{p}`) | `kl_divergence(q, p)` | `kl` |
| $I(q) = \sum_k H(q^k) - H(q)$ | Total correlation (multi-information) | `I(q)` (or `\MI(q)`) | `total_correlation(q)` | `totalCorrelation` |
| $\eta(q)$ | Normalized multi-information / *policy-blanket leakage* — $I(q)/H(q) \in [0,1]$; $0$ at strict mean-field, $1$ at maximally entangled. **Distinct from $\eta$ as m-coordinates** (see Pitfalls). | `\eta(q)` | composition of `total_correlation(q)` and `shannon_entropy(q)` | (no direct Lean; derivable from `totalCorrelation` and `shannonEntropy`) |
| $\mathrm{Var}_q[X]$ | Variance under $q$ | `\mathrm{Var}_q` (or `\Var{q}{X}`) | `np.var(...)` (ad-hoc) | (no Lean) |
| $\mathrm{Cov}_q[X, Y]$ | Covariance under $q$ | `\mathrm{Cov}_q` | (ad-hoc) | (no Lean) |
| $\sigma(x) = 1/(1+e^{-x})$ | Logistic sigmoid | `\sigma(x)` | `scipy.special.expit` (ad-hoc) | `floatLogistic` |
| $\langle X \rangle_q = \mathbb{E}_q[X]$ | Expectation operator under joint $q$ | `\langle X \rangle_q` (or `\E{q}{X}`) | `expected_value(q, X)` | (inline finite sum over `q_i * X_i`) |
| $\langle X \rangle_{q_\lambda}$ | Expectation under the entangled *posterior* $q_\lambda$ | `\langle X \rangle_{q_\lambda}` | `expected_value(entangled_posterior(...), X)` | (inline) |
| $\langle X \rangle_{\mathcal{E}_\lambda}$ | Expectation under the entangled *prior* $\mathcal{E}_\lambda$ — distinct from posterior expectation when $G \not\equiv 0$ | `\langle X \rangle_{\mathcal{E}_\lambda}` | `expected_value(entangled_prior(...), X)` | (inline) |
| $\mathrm{d}\log Z_E/\mathrm{d}\lambda = \langle J \rangle_{\mathcal{E}_\lambda}$ | Standard exponential-family identity for the prior log-partition derivative — used in [[THMREF:thm_4_2]] / [[THMREF:prop_10_1]] | (inline) | (analytical) | (analytical) |

## Free energies

| Symbol | Definition | LaTeX | Python | Lean |
|---|---|---|---|---|
| $F[q]$ | Variational free energy of $q$ | `F` (or `\fe`) | `free_energy(q, prior, G, gamma)` | `variationalFreeEnergy` |
| $F[q^k]$ | Per-stream marginal free energy | `F[q^k]` | `marginal_free_energy(q, prior, G, gamma, k)` | `marginalFreeEnergy` |
| $\sum_k F[q^k_\lambda]$ | Sum of per-stream VFEs (the mean-field free-energy baseline) | (sum) | `free_energy_bundle(spec, obs, lam).vfe_total` (`FreeEnergyBundle.vfe_total`) | `marginalFreeEnergy` (aggregated over `StreamIdx K`) |
| $\langle G_k \rangle_{q^k_\lambda}$ | Expected EFE under coupled posterior | `\langle G_k\rangle_{q^k_\lambda}` | `expected_free_energy_under_posterior(spec, obs, lam)[k]` / `FreeEnergyBundle.efe_under_posterior[k]` | (numerical) |
| $\lambda \langle J \rangle_{q_\lambda}$ | Coupling-energy contribution to $F$ | `\lambda \langle J\rangle` | `coupling_energy(spec, obs, lam)` / `FreeEnergyBundle.coupling_term` | `couplingExpectation` / `Skeleton` |

## Manifolds, projections, and dual coordinates

| Symbol | Meaning | LaTeX | Python | Lean |
|---|---|---|---|---|
| $\mathcal{M}$ | Simplex of strictly-positive joint distributions on $\Pi$ | `\mathcal{M}` (or `\Mfd`) | (implicit ambient) | (implicit) |
| $\mathcal{M}_{\mathrm{MF}} \subset \mathcal{M}$ | Mean-field submanifold (product distributions) | `\mathcal{M}_{\mathrm{MF}}` (or `\MFsubmfd`) | `is_mean_field(q, atol)` (membership predicate) | `IsMeanField` |
| $\hat{m}(q) = \prod_k q^k$ | m-projection of $q$ onto $\mathcal{M}_{\mathrm{MF}}$ | `\hat{m}(q)` | `m_projection(q)` | `mfToJoint` (direction: MF → joint; Python computes the joint → MF marginals before rejoining) |
| $\theta = \log q$ | e-coordinates (natural parameters) | `\theta` | `np.log(q)` (ad-hoc) | (no Lean) |
| $\eta = \mathbb{E}_q[\cdot]$ | m-coordinates (expectation parameters of an exponential family). **Distinct from $\eta(q)$ policy-blanket leakage** (see Pitfalls). | `\eta` | (ad-hoc) | (no Lean) |
| Pythagorean residual | $D_{\mathrm{KL}}(q \,\|\, q_0^*) - I(q) - D_{\mathrm{KL}}(\hat m(q) \,\|\, q_0^*)$ | (inline) | `pythagorean_residual(q, mf_reference)` | `dualFlat_pythagorean_witness` |

## Spectral and tensor-network symbols

| Symbol | Meaning | LaTeX | Python | Lean |
|---|---|---|---|---|
| $r$ | Schmidt rank of bipartite (K=2) joint | `r` | `schmidt_rank(q, atol)` | (boundary witness) |
| $s_\alpha$ | $\alpha$-th singular value | `s_\alpha` | `Archetype.weight` (in `schmidt_decomposition`) | (numerical) |
| $u_\alpha,\,v_\alpha$ | Left / right singular vectors (archetype marginals) | `u_\alpha,\,v_\alpha` | `Archetype.u`, `Archetype.v` | (numerical) |
| $S_E(q)$ | Policy entanglement entropy of bipartite cut | `S_E(q)` | `entanglement_entropy(q, atol)` | (numerical) |
| $r_{\mathrm{eff}}(\lambda) = e^{S_E(q_\lambda)}$ | **Effective rank** — smooth phase order parameter (continuous proxy for the integer Schmidt rank) used in [[SECREF:phase]] | `r_{\mathrm{eff}}` | `np.exp(entanglement_entropy(q))` (composition) | (no Lean — numerical) |
| $r_k$ | Tensor-train bond dimension across $k$-th cut | `r_k` | `tensor_train_ranks(q, atol)[k]` | (numerical) |
| $(r_1,\ldots,r_{K-1})$ | Tensor-train rank profile | `(r_1,\ldots,r_{K-1})` | `entanglement_spectrum(q)` | (numerical) |
| $A^{(k)}$ | MPS / tensor-train tensor at site $k$ (factor of the matrix-product factorization of $q_\lambda$); see [[SECREF:spectral.multistream_tt]] | `A^{(k)}` | `mps_decomposition(q)[k]` (canonical left-orthogonal TT-SVD; reconstruction-verified in `tests/test_spectral.py`) | (no Lean) |
| $S_k(q_\lambda)$ | Per-cut bond entropy: entanglement entropy across the bipartition splitting streams $\{1,\ldots,k\}$ from $\{k+1,\ldots,K\}$ | `S_k(q_\lambda)` | `entanglement_entropy_per_cut(q, k)` (composition of `entanglement_entropy` with the per-cut bipartite reshape) | (no Lean) |
| $S_k^{\max} = \log r_k$ | Maximum bond entropy across cut $k$ (achieved by the uniform spectrum on $r_k$ singular values) | `S_k^{\max}` | `np.log(tensor_train_ranks(q)[k])` | (no Lean) |
| $\mathrm{Cov}_{q_\lambda}(J-\gamma K_c,\ \log q_\lambda - \log\hat m(q_\lambda))$ | Covariance identity for the derivative $dI/d\lambda$ of total correlation along the entangled family ([[SECREF:lambda_deformation]]) | (inline) | (numerical; from `entangled_posterior` outputs) | (no Lean) |

## Heterogeneous-ensemble quantities

| Symbol | Meaning | LaTeX | Python | Lean |
|---|---|---|---|---|
| $\mathrm{tax}(\lambda)$ | Coupling tax (KL between fully-adaptive and pinned posteriors) | `\mathrm{tax}(\lambda)` | `coupling_tax(mf, G, J, K_c, gamma, lam, modes)` | `couplingTax` (witness form) |
| $\|\Phi\|_\infty$ | Coupling magnitude (sup-norm) | `norm_inf(Phi)` | (sup over coupling-log-weight) | `couplingNormSq` |
| $C \geq 0$ | Structural curvature constant in [[THMREF:thm_8_1]]. Live rendered value: `manuscript_variables.json[coupling_tax_curvature_C]`. | `C` | `quadratic_bound_curvature(...)` | (boundary witness) |

## KL-control, copula, and product-of-experts symbols

These symbols appear in [[SECREF:connections.kl_control]] (KL-control /
path-integral correspondence) and the copula / product-of-experts
extensions of [[SECREF:lambda_deformation]] and [[SECREF:connections.copula]].  They are documented here
so the reader can disambiguate against the main coupling notation
(particularly the trajectory cost $C(\tau)$, renamed from $J$ to avoid
collision with the habit coupling potential).

| Symbol | Meaning | LaTeX | Python | Lean |
|---|---|---|---|---|
| $V(x)$ | KL-control / path-integral value function (cost-to-go) | `V(x)` | (no Python — symbol only) | (no Lean) |
| $p_{\mathrm{free}}$ | Uncontrolled / free dynamics distribution (reference law in the KL-control correspondence) | `p_{\mathrm{free}}` | (no Python — symbol only) | (no Lean) |
| $\rho$ | Risk-sensitivity parameter in KL-control (inverse-temperature on the trajectory cost) | `\rho` | (no Python — symbol only) | (no Lean) |
| $C(\tau)$ | Trajectory cost in KL-control. **Renamed from $J$** to avoid clash with the habit coupling potential $J(\pi)$. | `C(\tau)` | (no Python — symbol only) | (no Lean) |
| $u^k = F_{E_k}(\pi^k)$ | Copula CDF reparameterization of per-stream policy: $u^k$ is the CDF transform of $\pi^k$ under $E_k$, mapping each stream onto $[0,1]$ for copula-based coupling | `u^k = F_{E_k}(\pi^k)` | (no Python — symbol only; copula extension is outside the present implementation) | (no Lean) |
| $f_j$ | Product-of-experts factor (one of the multiplicative experts in $q(\pi) \propto \prod_j f_j(\pi)$) | `f_j` | (no Python — symbol only) | (no Lean) |
| $G_{\mathrm{soph}}(\pi)$ | Sophisticated-inference expected free energy (recursive EFE over future belief updates) | `G_{\mathrm{soph}}` | `per_stream_efe(..., SOPHISTICATED)` | `ConnectionsWitnesses` / sophisticated-inference witness |
| $J_{\mathrm{soph}}$ | Source-supplied coupling carrying recursive observation-conditioning for sophisticated inference; not generated by $\lambda$ alone | `J_soph` | witness payload | SI embedding payload |

## Relationship classes and claim-strength labels

Part V and [[SECREF:app.aif_recovery]] use two small
controlled vocabularies.  They are not mathematical variables, but
they are notation in the audit sense: they determine how strongly a
sentence is allowed to identify this framework with an external
active-inference variant.

| Label | Meaning | Where enforced |
|---|---|---|
| `exact` | Literal specialization of the posterior family or a single-stream log-partition dual after all factors are specified | Active-inference recovery ledger; relationship-guard tests |
| `parametric` | Realized only after the modeler adds an explicit factor, change of variables, agent boundary, or structural parameter | Active-inference recovery ledger; relationship-guard tests |
| `analogical` | Shares a structural motif, while temporal, recursive, state-space, or message-passing content remains outside the $\lambda$-deformation | Active-inference recovery ledger; relationship-guard tests |
| `out-of-scope` | Related background whose geometry or modeling object is not represented by the current posterior family | Active-inference recovery ledger |
| `proved` / `witness` / `empirical` / `hypothesis` / `roadmap` | Claim-strength labels used to separate stock-Lean proofs, witness-consuming theorem rows, generated numerical evidence, interpretation, and future proof discharge | [[SECREF:app.claim_strength]]; claim-provenance tests |

## Hyperparameters (figure / sweep / simulation)

The constants below live in
[`src/simulation/hyperparameters.py`](../src/simulation/hyperparameters.py)
and are mirrored into `output/data/manuscript_variables.json`; they
reach the prose via `[[VAR:<key>]]` substitutions.

| Symbol | Source-of-truth constant | JSON key | Default |
|---|---|---|---|
| Param-sweep grid count | `PARAMETER_SWEEP_LAMBDAS.num` | `param_sweep_grid_points` | $[[VAR:param_sweep_grid_points]]$ |
| Param-sweep range | `PARAMETER_SWEEP_LAMBDAS.[start,stop]` | `param_sweep_lambda_min/max` | $[0, [[VAR:param_sweep_lambda_max:g]]]$ |
| Coupling-tax grid | `COUPLING_TAX_LAMBDAS.num` | `coupling_tax_grid_points` | $[[VAR:coupling_tax_grid_points]]$ |
| Phase-diagram grid | `PHASE_DIAGRAM_LAMBDAS.num` | `phase_diagram_grid_points` | $[[VAR:phase_diagram_grid_points]]$ |
| pymdp sweep grid | `PYMDP_SWEEP_LAMBDAS.num` | `pymdp_sweep_grid_points` | $[[VAR:pymdp_sweep_grid_points]]$ |
| pymdp rollout horizon $T$ | `PYMDP_ROLLOUT_STEPS` | `pymdp_rollout_steps` | $[[VAR:pymdp_rollout_steps]]$ |
| pymdp rollout seed | `PYMDP_ROLLOUT_SEED` | `pymdp_rollout_seed` | $[[VAR:pymdp_rollout_seed]]$ |
| Figure-script global RNG seed | `FIGURE_GLOBAL_SEED` | `figure_global_seed` | $[[VAR:figure_global_seed]]$ |
| Param-sweep agreement tolerance | `PARAMETER_SWEEP_AGREEMENT_TOLERANCE` | `param_sweep_agreement_tolerance` | $[[VAR:param_sweep_agreement_tolerance:.0e]]$ |

## LaTeX preamble macros

*Reserved LaTeX macros (currently unused in the body; available for
future expansion): see [`manuscript/preamble.md`](preamble.md) for the
canonical definitions (`\KL`, `\E`, `\Var`, `\policy`,
`\policySpace`, `\Mfd`, `\MFsubmfd`, `\MI`, `\Hent`, `\efe`, `\fe`,
`\coupJ`, `\coupK`). Each glossary row above cross-references the
spelled-out form which is the one actually used throughout the
manuscript.*

## Lean type abbreviations

The Lean boundary fragment uses lower-case ASCII identifiers as
substitutes for reserved binder tokens (`λ` → `lam`, `π` → `pi`,
`Π` → `Pol`).

| Lean abbrev | Meaning | Defined in |
|---|---|---|
| `α : Type` | Generic scalar type satisfying `CommScalar α` | `Scalar.lean` |
| `CommScalar α` | In-house typeclass over a commutative scalar | `Scalar.lean` |
| `K : Nat` | Stream count | `Basic.lean` |
| `StreamIdx K` | `Fin K` — stream index | `Basic.lean` |
| `PolicyFactor K` | `StreamIdx K → Type` — per-stream policy type | `Basic.lean` |
| `PolicySpace K Pol` | `∀ k, Pol k` — joint policy type | `Basic.lean` |
| `JointDist K Pol` | `PolicySpace K Pol → α` — joint PMF | `JointDist.lean` |
| `MFDist K Pol` | `∀ k, Pol k → α` — mean-field PMF | `JointDist.lean` |
| `CouplingPotential α K Pol` | `PolicySpace K Pol → α` — $J$ / $K_c$ shape | `Coupling.lean` |
| `BinaryCoupling` | `Bool → Bool → Float` — K=2 closed-form coupling | `BernoulliToy.lean` |
| `HorizonProfile K` | `StreamIdx K → Nat` — temporal horizon per stream | `Basic.lean` |
| `pi : PolicySpace K Pol` | A joint policy | (use sites) |
| `lam : α` | Coupling parameter | (use sites) |
| `q_lam : JointDist K Pol` | Entangled posterior at coupling `lam` | (use sites) |

## Phase / verdict labels (manuscript-level)

Three discrete classifiers used in the body of the manuscript.

| Label | Values | Where defined | Manuscript role |
|---|---|---|---|
| `InferenceMode` | `VFE` / `EFE` / `SOPHISTICATED` | Python `enum` in [`src/lean/heterogeneous.py`](../src/lean/heterogeneous.py) | Stream-mode label ([[SECREF:setup.multistream]], [[SECREF:heterogeneous]]) |
| `CouplingPhase` | `disordered` / `mixed` / `frozen` (string) | Returned by `bernoulli_toy.coupling_phase_at(lam)` | Cognitive phase ([[SECREF:phase]]) |
| `CouplingRole` | `habit` ($J$) / `preference` ($K_c$) | Manuscript convention; not a Python or Lean type | Side of the coupling potential |
| `CouplingVerdict` | `pays` / `neutral` / `does_not_pay` | Manuscript convention; manifests as the Lean theorem `couplingVerdict` (in `Decomposition.lean`) | Coupling-pays-for-itself outcome ([[SECREF:comparative]]) |

### Status notes {#status-notes}

* **`InferenceMode`** is presently a Python-only `Enum`; the
  Lean boundary fragment treats stream mode as a witness consumed by
  `IsPlanningStream` / `IsReflexiveStream` predicates
  (`Heterogeneous.lean`).  The current Lean source therefore uses the
  predicates directly rather than an `InferenceMode` inductive.
* **`CouplingPhase`** is a string-returning Python predicate
  (`coupling_phase_at`) plus the Lean function
  `couplingPhaseAt : Float → Nat` (returning `0`/`1`/`2`); the
  inductive form is documented in
  [`lean/ActinfPolicyEntanglement/README.md`](../lean/ActinfPolicyEntanglement/README.md)
  but has not been promoted into the boundary source.
* **`CouplingRole`** has no Python or Lean type — it is
  manuscript-level convention to disambiguate the two coupling
  potentials in prose.

## Conventions

* **Natural log** is used throughout; numeric values therefore have
  units of *nats*.  Where binary log is needed it is written $\log_2$.
* **Joint vs marginal**: distributions on $\Pi$ are *joints*; per-stream
  distributions on $\Pi^k$ are *marginals*.
* **Vector / tensor**: bold $\mathbf{x}$ when shape matters, plain $x$
  otherwise.
* **Equations vs definitions**: an equation set off as
  $X \equiv Y$ is a definition; $X = Y$ is a derivable identity.
* **Probability conventions**: every distribution is normalized to
  $1$ unless explicitly *unnormalized*; KL is always
  $D_{\mathrm{KL}}(q \,\|\, p)$ (not the reverse).
* **Information geometry**: dually-flat structure on the simplex
  follows the standard development [@amari-nagaoka-2000; @amari-2016;
  @nielsen-2020]; non-extensive / $\phi$-deformed analogs use the
  framework of [@naudts-2011].
* **Active-inference background**: the single-stream POMDP recap
  follows [@friston-2010; @dacosta-2020; @smith-2022], with EFE
  conventions per [@friston-2017].
* **Determinism**: all numerical figures are bit-reproducible under
  fixed seeds; see the full determinism contract in
  [`docs/reference/statistics_reference.md`](../docs/reference/statistics_reference.md).

## Common pitfalls when editing across tracks

The four-track contract permits a few notation hazards that have
bitten earlier drafts and that automated validation does not catch.
They are listed here so an editor can recognise them by name.

* **Prior vs posterior expectation.**  The symbol
  $\langle X\rangle_\lambda$ is ambiguous; the manuscript uses
  $\langle X\rangle_{\mathcal{E}_\lambda}$ for *prior* expectations
  (used in the log-partition derivative
  $\mathrm{d}\log Z_E/\mathrm{d}\lambda = \langle J\rangle_{\mathcal{E}_\lambda}$)
  and $\langle X\rangle_{q_\lambda}$ for *posterior* expectations.
  Mixing them silently introduces a sign error in convex / concavity
  arguments (see [[SECREF:app.convexity]]).
* **$\lambda$ as parameter vs $\lambda$ as Lean keyword.**  In Lean,
  `λ` is reserved for anonymous-function syntax; the manuscript
  parameter $\lambda$ becomes the identifier `lam` on the Lean side.
  Every `lam : α` in `.lean` files is the coupling parameter, not a
  closure binder.
* **$K$ vs $K_c$.**  $K$ (stream count) and $K_c$ (preference
  coupling potential) collide at one ASCII letter.  Use `Kc` (Python,
  Lean) or `K_c` (LaTeX); never bare `K` in a context that could be
  read as either.
* **MF prior $E_{\mathrm{MF}}$ vs $\lambda$-entangled prior
  $\mathcal{E}_\lambda$.**  Both pieces of notation use the letter
  "E", and `e_lambda` / `mf_prior` are the disambiguating Python
  names; never write `E` in code or prose without the appropriate
  subscript or qualifier.
* **Total correlation vs per-stream entropy sum.**
  $I(q) = \sum_k H(q^k) - H(q) \ge 0$, *not*
  $\sum_k H(q^k)$ alone.  The Python `total_correlation(q)` returns
  the difference; an editor importing `sum_marginal_entropies` and
  calling it "total correlation" by mistake will introduce a
  manuscript-vs-code divergence the validator cannot detect.
* **Natural log everywhere.**  Information-theoretic quantities are
  in *nats*.  When citing a $\log_2$-convention source in the
  bibliography, convert before quoting numeric values.
* **Floating tolerance.**  `atol=1e-9` is the project-wide default
  for spectral / SVD-based predicates; `atol=1e-12` is the default for
  conservation laws / sum-to-one checks; tests under
  `tests/test_*.py` adopt either explicitly.  Don't change the
  default in one place without checking the others.
* **$\eta$ is overloaded.**  In [[SECREF:geometry]] (information
  geometry) it denotes *m-coordinates* (expectation parameters of an
  exponential family); in
  [[SECREF:connections_multi_agent_geometry]] (policy-blanket leakage)
  it denotes the normalized multi-information $\eta(q) = I(q)/H(q)$.
  Subscripts and context disambiguate; we keep both usages because
  each is standard in its parent literature (Amari / Nagaoka for the
  geometric $\eta$; Friston / Pellet-Massini for the leakage $\eta$).

---

### GNN fifth-track concordance (structural-and-numerical) {#sec:notation.gnn}

The fifth track maps each standing symbol of the K=2 toy to its declaration in
the shipped GNN source `gnn/bernoulli_toy.gnn.md` (parser: `src/gnn/parser.py`;
round-trip: `scripts/simulate_gnn.py`; parity test: `tests/test_gnn_concordance.py`).
This track is **structural-and-numerical**, not a proof track, and the round-trip
is an **internal-consistency reduction** — the general machinery reduces to the
closed form for this toy — **not an independent corroboration**: it reproduces the
model's structure and the K=2 mutual-information curve to
[[VAR:gnn_roundtrip_max_residual:.2e]] nats, but promotes no theorem row in
[[SECREF:app.reference_tables]]. See [[SECREF:app.gnn_extension]].

| Symbol | GNN variable | Active Inference Ontology term |
|---|---|---|
| $\pi^1$ (stream-1 policy) | `pi1` | `Stream1PolicyVector` |
| $\pi^2$ (stream-2 policy) | `pi2` | `Stream2PolicyVector` |
| $E^1$ (stream-1 habit prior) | `E1` | `Stream1HabitPrior` |
| $E^2$ (stream-2 habit prior) | `E2` | `Stream2HabitPrior` |
| $J$ (cross-stream coupling) | `J` (joint var on the policy product) | `CrossStreamCouplingPotential` |
| $\lambda$ (deformation) | `lam` | `EntanglementDeformationParameter` |
| $\gamma$ (sophistication) | `gamma` | `SophisticationWeight` |
| $q_\lambda$ (entangled joint posterior) | `q_joint` | `EntangledJointPosterior` |
