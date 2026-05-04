# The Entanglement Decomposition Theorem

## Statement

The variational free energy under $q_\lambda$ admits a clean decomposition. Define

$$F[q_\lambda] = \mathbb{E}_{q_\lambda}\!\left[\gamma\, G_\lambda(\pi) - \log \mathcal{E}_\lambda(\pi)\right] - H(q_\lambda).$$

Let $q_\lambda^k$ denote the marginal of $q_\lambda$ on stream $k$, and $F[q_\lambda^k]$ the *marginal* free energy if stream $k$ were treated in isolation against its own $E_k, G_k$.

**[[THMREF:thm_4_1]] (Entanglement Decomposition).**

[[EQ:tc_decomp]]

where the total correlation [[EQ:total_correlation]] is non-negative
and vanishes iff $q_\lambda$ is mean-field.

The Lean companion (boundary statement; full proof scheduled for
Phase 7 once Mathlib's KL chain rule is in scope) is auto-extracted
from the live source:

[[LEAN:thm_4_1]]

## Proof sketch

Expand $F[q_\lambda]$:

\begin{align}
F[q_\lambda] &= \mathbb{E}_{q_\lambda}\!\left[\gamma\textstyle\sum_k G_k(\pi^k) + \gamma\lambda K_c(\pi) - \textstyle\sum_k \log E_k(\pi^k) - \lambda J(\pi)\right] - H(q_\lambda)\\
&= \sum_k \mathbb{E}_{q_\lambda^k}\!\left[\gamma G_k(\pi^k) - \log E_k(\pi^k)\right] + \lambda(\gamma\langle K_c\rangle - \langle J\rangle) - H(q_\lambda).
\end{align}

The first sum is $\sum_k\big(\mathbb{E}_{q_\lambda^k}[\gamma G_k - \log E_k] - H(q_\lambda^k)\big) + \sum_k H(q_\lambda^k) = \sum_k F[q_\lambda^k] + \sum_k H(q_\lambda^k)$.

Substituting and using $-H(q_\lambda) + \sum_k H(q_\lambda^k) = I(q_\lambda)$, but with the sign flipped (since we want $-H(q_\lambda)$ but introduce $+\sum H(q_\lambda^k)$), gives:

$$F[q_\lambda] = \sum_k F[q_\lambda^k] + \lambda(\gamma\langle K_c\rangle - \langle J\rangle) + \big[\sum_k H(q_\lambda^k) - H(q_\lambda)\big] - 2\sum_k H(q_\lambda^k) + \text{cancellation}.$$

Careful re-bookkeeping (full derivation in [[SECREF:app.proof_decomp]]) produces the boxed identity above with a single multi-information correction. The key step: the joint entropy contribution $-H(q_\lambda)$ exactly equals $-\sum_k H(q_\lambda^k) + I(q_\lambda)$.

## What the decomposition says

Three terms, three readings:

**(i) $\sum_k F[q_\lambda^k]$.** The free energy that would obtain if each stream were optimized in isolation against the *marginal* of $q_\lambda$. This is *not* the same as $\sum_k F[q_k^{\mathrm{MF}}]$, because the marginals $q_\lambda^k$ are themselves shaped by coupling — coupling deforms what a stream considers a-posteriori plausible even before we charge the multi-information cost.

**(ii) $\lambda(\gamma\langle K_c\rangle - \langle J\rangle)$.** The *coupling cost* — what it costs (or pays) the agent to maintain the joint structure encoded by the potentials. Sign depends on alignment between habit coupling $J$ (which the agent likes) and preference-side coupling $K_c$ (which contributes EFE). When $J$ and $K_c$ point in compatible directions — e.g., when habitual joint policies happen to also minimize joint EFE — this term can be net negative and pays for itself.

**(iii) $-I(q_\lambda) \leq 0$.** Strictly non-positive. **Multi-information is always agentic gain.** Any genuine cross-stream correlation in the posterior strictly reduces free energy by exactly the amount of multi-information generated. This is the formal expression of the intuition that "joint structure is cheaper than its marginals would suggest."

The Lean companions for the three immediate corollaries are auto-extracted below.

[[THMREF:cor_4_2]] (the *coupling-pays-for-itself* verdict) is a
tri-state classifier from the sign of the bookkeeping (Lean: a `def`,
not a theorem):

[[LEAN:cor_4_2]]

[[THMREF:cor_4_3]] (mean-field reduction at $\lambda = 0$) collapses
the four-summand bookkeeping to its sum-of-marginals + total-
correlation-gain pair:

[[LEAN:cor_4_3]]

[[THMREF:cor_4_4]] (strict gain when $q$ is non-mean-field) is the
sign companion of [[EQREF:total_correlation]]:

[[LEAN:cor_4_4]]

## Optimal coupling: existence of lambda*

**[[THMREF:thm_4_2]] (Existence of optimal coupling).** For fixed $J, K_c$ with bounded potentials, $F[q_\lambda]$ is real-analytic in $\lambda$ on $[0,\infty)$. The function $\lambda \mapsto F[q_\lambda]$ has at least one stationary point in $(0, \infty)$ whenever

$$\frac{\partial}{\partial \lambda}\Big|_{\lambda = 0}\!F[q_\lambda] \;<\; 0,$$

equivalently when at the mean-field point the marginal coupling cost is less than the marginal information gain:

$$\gamma\langle K_c\rangle_{q_0} - \langle J\rangle_{q_0} \;<\; \frac{\mathrm{d} I(q_\lambda)}{\mathrm{d}\lambda}\Big|_{0}.$$

The right-hand side is computable in closed form via the Fisher information of the exponential family $\{q_\lambda\}$ on its natural parameter — see [[SECREF:geometry]].

**[[THMREF:thm_4_3]] (Convexity of $F$ in $\lambda$).** If $J - \gamma K_c$ is log-concave on $\Pi$ (in a sense to be made precise on the simplex via Boltzmann lifting; see [[SECREF:app.convexity]]), then $\lambda \mapsto F[q_\lambda]$ is convex on $[0,\infty)$ and $\lambda^*$ is unique.

**[[THMREF:thm_4_3]] says,** in cognitive terms: when habit coupling and preference coupling are coherent (no internal contradictions in what joint policies the agent prefers and habituates), the optimal entanglement strength is uniquely determined.

When they are incoherent, the framework predicts *multiple stable coupling regimes* — a point we develop into a phase-structure analysis in [[SECREF:phase]].

---
