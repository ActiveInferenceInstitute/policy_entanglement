# Coupled Updates and Heterogeneous Inference

## Three-level update hierarchy

The framework induces a natural three-level hierarchy of online updates:

1. **Level 1 (within-stream).** Update $q^k_\lambda$ for each stream, holding $J, K_c, \lambda$ fixed.
2. **Level 2 (coupling structure).** Update $J, K_c$ as parameters of a generative model (e.g., Dirichlet-coupling for $J$, gradient on free energy of free energy for $K_c$).
3. **Level 3 (coupling precision).** Update $\lambda$ by gradient on $F[q_\lambda]$.

Each level has a clean interpretation:
- Level 1: ordinary perception/policy inference. Time scale: per-step.
- Level 2: habit/preference learning. Time scale: trials to days.
- Level 3: precision learning on the *coupling* itself — *meta-cognitive flexibility*. Time scale: phases of engagement / arousal / context.

## Coupled marginal updates

For stream $k \in \mathcal{P}$ (planning), the coordinate-descent update on $q^k_\lambda$ is the standard fixed-point:

$$q^k_\lambda(\pi^k) \;\propto\; \exp\!\Big(\!\!\!\!\!\!\!\!\!\!\underbrace{\log E_k(\pi^k) - \gamma G_k(\pi^k)}_{\text{single-stream EFE term}}\!\!\!\!\!\!\!\!\!\!\;+\!\!\!\!\!\!\underbrace{\sum_{j\neq k}\langle \log\Phi_{kj}(\pi^k,\pi^j)\rangle_{q^j}}_{\text{coupling messages from other streams}}\!\!\!\!\!\!\!\!\Big)$$

where $\Phi_{kj}(\pi^k,\pi^j) = \exp(\lambda J_{kj}(\pi^k,\pi^j) - \gamma\lambda K_{c,kj}(\pi^k,\pi^j))$. This is exactly *belief propagation on a coupled factor graph* with the coupling potentials $\Phi_{kj}$ as factors.

This recovers `pymdp`-style factorized inference [@heins-2022] as the $\lambda = 0$ limit, and generalizes it to coupled structure.

## The VFE-only suboptimality bound

For $k \in \mathcal{V}$ (VFE-only, reflexive), the stream takes a one-step gradient on its marginal free energy without iterative message passing. We compare to the coordinate-descent step taken by the full coupled inference.

**[[THMREF:thm_8_1]] (Heterogeneous coupling tax).** Let $q^k_*$ be the coordinate-descent step for stream $k$ in the coupled ensemble at coupling $\lambda$, and $q^k_\circ$ be the one-step VFE gradient step ignoring couplings. Define the coupling magnitude $\|\Phi\|_\infty = \max_{j,k,\pi^k,\pi^j}|\log \Phi_{kj}(\pi^k,\pi^j)|$. Then:

$$D_{\mathrm{KL}}(q^k_*\,\|\,q^k_\circ) \;\leq\; C \cdot \lambda^2 \|\Phi\|_\infty^2 + O(\lambda^3)$$

for a constant $C$ depending only on $|\Pi^k|$ and the curvature of $G_k$.

**Proof sketch.** Taylor-expand the coordinate-descent fixed-point equation in $\lambda$. The zeroth-order term is the single-stream MF posterior; the first-order correction is the linear coupling-message contribution; the second-order term involves cross-coupling between messages from different streams. KL divergence is locally quadratic, giving the $\lambda^2$ leading term.

**Cognitive interpretation.** Reflexive controllers can sit inside a coupled ensemble and pay only a *quadratic* cost (in coupling strength) for not running the full message-passing inference. For small-to-moderate $\lambda$, this is a negligible tax; for large $\lambda$, the reflexive controller becomes systematically suboptimal. This gives a quantitative answer to the engineering question: *how reactive can my low-level controllers be without losing the benefits of higher-level planning?* Answer: reactive is fine until $\lambda^2 \|\Phi\|_\infty^2$ becomes comparable to the per-step free-energy budget.

The $O(\lambda^2)$ envelope (see [[EQREF:coupling_tax_bound]]) is
verified empirically by the companion code in
[`src/lean/heterogeneous.py`](../src/lean/heterogeneous.py)
(`coupling_tax_within_quadratic_bound`) and visualised below; for
the symmetric K=2 Ising toy with the standard `(J, K_c, γ, modes)`
of `make_ising_ensemble` the fitted curvature is
$C \approx [[VAR:coupling_tax_curvature_C:.4f]]$.

[[FIG:coupling_tax_quadratic]]

The Lean companion (boundary statement; the genuine quadratic bound
discharges via Bregman / KL Taylor expansion in Phase 7):

[[LEAN:thm_8_1]]

The reflexive-stream tolerance corollary [[THMREF:cor_8_2]] then
inverts the bound to deliver a tolerance-explicit `lam_max`:

[[LEAN:cor_8_2]]

## Updating lambda: precision learning on coupling

Treat $\lambda$ as a free parameter and minimize $F[q_\lambda]$ via gradient:

$$\frac{\partial F[q_\lambda]}{\partial \lambda} = -\langle J\rangle_{q_\lambda} + \gamma\langle K_c\rangle_{q_\lambda} - \frac{\partial I(q_\lambda)}{\partial \lambda}.$$

The third term is computable via the Fisher information of the natural-parameter family — the same calculation that drives standard precision updates. Indeed:

$$\frac{\partial I(q_\lambda)}{\partial \lambda} = \mathrm{Cov}_{q_\lambda}(J - \gamma K_c, \log q_\lambda - \log\hat m(q_\lambda)).$$

This makes $\lambda$ updating a **precision-on-coupling** mechanism, formally analogous to dopaminergic precision [@friston-2014; @schwartenbeck-2015] but operating at a higher level: not "how confident am I in my policy?" but "how strongly should my different policies be entangled right now?" Cognitive analogue: arousal, vigilance, context-dependent flexibility.

## Habit accumulation and revertibility

Habit learning under coupled $E$ is straightforward Bayesian updating on $J$ as a Dirichlet-distributed parameter [@friston-2017]:

$$E_{\lambda,\mathrm{new}}(\pi) \propto \exp\!\Big(\sum_k \log E_k(\pi^k) + \lambda J_{\mathrm{new}}(\pi)\Big), \qquad J_{\mathrm{new}}(\pi) = J(\pi) + \alpha \cdot q_\lambda(\pi) \cdot \mathrm{success\_signal}.$$

Over learning, $J$ accumulates structure shaped by which joint policy regions repeatedly minimize $G_\lambda$. This is exactly habit formation in standard AIF [@friston-2017], generalized to joint structure.

**Revertibility.** The framework distinguishes *coupling-rich* habit from *coupling-poor* (mean-field) habit. To revert a coupling-rich habit to its mean-field component, take the m-projection: $E_k^{\mathrm{MF}}(\pi^k) = \sum_{\pi^{-k}} E(\pi)$. The coupling structure $J$ is recoverable via $J = \log E - \sum_k \log E_k^{\mathrm{MF}}$ (up to the normalizer). This gives an analytic decomposition of any habit into its marginal and coupled components, directly addressing DAF's emphasis on the revertibility of the framework.

---
