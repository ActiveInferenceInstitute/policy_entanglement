# Entanglement Decomposition Theorem: Marginals, Coupling, and Total Correlation

## Statement {#sec:decomposition.statement}

The variational free energy under $q_\lambda$ admits a clean decomposition. Define

$$
F[q_\lambda] = \mathbb{E}_{q_\lambda}\!\left[\gamma\, G_\lambda(\pi) - \log \mathcal{E}_\lambda(\pi)\right] - H(q_\lambda).
$$

Let $q_\lambda^k$ denote the marginal of $q_\lambda$ on stream $k$, and $F[q_\lambda^k]$ the *marginal* free energy if stream $k$ were treated in isolation against its own $E_k, G_k$.

**[[THMREF:thm_4_1]] (Entanglement Decomposition).**

[[EQ:tc_decomp]]

where the total correlation [[EQ:total_correlation]] is non-negative
and vanishes iff $q_\lambda$ is mean-field.  (The sign on every term
follows [[SECREF:notation.sign_conventions]] in S06 — specifically the
**plus**-$I(q_\lambda)$ and the $+\gamma\lambda\langle K_c\rangle$
conventions.)

The Lean companion is a boundary statement auto-extracted from the live
source:

[[LEAN:thm_4_1]]

> **Honesty note.** The *Float* boundary companion above carries
> `status: boundary` in
> [`manuscript/refs/labels.yaml`](refs/labels.yaml), **not** `status:
> proved`: it type-checks under stock Lean [[VAR:lean_toolchain_version]] and locks the four-
> term algebraic skeleton, but its analytic content is supplied as a
> hypothesis. **The analytic content itself is now machine-checked in
> $\mathbb{R}$:** `MathlibProofs.entanglement_decomposition_generalK`
> proves, for general $K$ and a general entangled $q$ (positivity +
> normalization only; never assumed to factorize), the
> multi-information non-negativity, the KL chain-rule decomposition,
> and $m$-projection minimality — depending only on the three standard
> foundational axioms, with the previously-deferred
> product-marginalization core discharged from the standing
> positivity + normalization hypotheses without further structural
> assumptions, and negative-control-verified as non-vacuous. **The
> full S01 boxed identity itself**
> (`F=Σ F[qᵏ]+γλ⟨K_c⟩+log Z_E−λ⟨J⟩+I(q)`) is then machine-checked in
> $\mathbb{R}$ by `MathlibProofs.free_energy_decomposition_full` for
> the genuine entangled posterior (`log Z_E` the definitional
> normalizer, foundational-only axioms, two independent negative
> controls). The Float companion is the numerically-corroborated
> computational image of the $\mathbb{R}$ proof; closing the
> Float$\leftrightarrow\mathbb{R}$ formal bridge is the one
> *verification-stack interface* residual (the open residual discussed
> at [[SECREF:discussion]]; the remaining typed-API rows are the
> analytic-discharge follow-on tracked at [[SECREF:open_questions]], not
> a separate verification gap).
> See the *honest substantive / typed-API split* in
> [`docs/reference/veridical_status.md`](../docs/reference/veridical_status.md#round-4-round-trip-honesty-upgrades)
> for the round-by-round audit of which Lean theorems are *substantive
> machine-checked proofs* versus *typed-API contracts*.

## Proof sketch

Expand $F[q_\lambda] = \mathbb{E}_{q_\lambda}[\gamma\, G_\lambda - \log \mathcal{E}_\lambda] - H(q_\lambda)$ using

$$
\gamma G_\lambda(\pi) = \gamma \sum_k G_k(\pi^k) + \gamma\lambda K_c(\pi),
\qquad
\log \mathcal{E}_\lambda(\pi) = \sum_k \log E_k(\pi^k) + \lambda J(\pi) - \log Z_E(\lambda)
$$

for the normalized entangled prior $\mathcal{E}_\lambda \propto (\prod_k E_k)\,e^{\lambda J}$.  Linearity of expectation separates $\mathbb{E}[\gamma G_\lambda]$ and $\mathbb{E}[\log \mathcal{E}_\lambda]$ into per-stream pieces plus the $\gamma\lambda\langle K_c\rangle$, $\lambda\langle J\rangle$, and $\log Z_E(\lambda)$ terms.  The entropies $-H(q_\lambda)$ combine with $\sum_k \mathbb{E}_{q_\lambda^k}[\gamma G_k - \log E_k]$ into $\sum_k F[q_\lambda^k] + \big(\sum_k H(q_\lambda^k) - H(q_\lambda)\big)$; the parenthesis is multi-information [[EQ:total_correlation]], i.e.\ $I(q_\lambda)$.  Altogether this yields [[EQ:tc_decomp]].  Full line-by-line algebra is in [[SECREF:app.proof_decomp]]; the Python record `entanglement_decomposition_rhs` sums the same four grouped terms and matches the Gibbs definition of $F$ on random joints (see `tests/test_decomposition.py`).

## What the decomposition says

Three terms, three readings:

**(i) $\sum_k F[q_\lambda^k]$.** The free energy that would obtain if each stream were optimized in isolation against the *marginal* of $q_\lambda$. This is *not* the same as $\sum_k F[q_k^{\mathrm{MF}}]$, because the marginals $q_\lambda^k$ are themselves shaped by coupling — coupling deforms what a stream considers a-posteriori plausible even before we charge the multi-information cost.

**(ii) $\lambda(\gamma\langle K_c\rangle - \langle J\rangle)$.** The *coupling cost* — what it costs (or pays) the agent to maintain the joint structure encoded by the potentials. Sign depends on alignment between habit coupling $J$ (which the agent likes) and preference-side coupling $K_c$ (which contributes EFE). When $J$ and $K_c$ point in compatible directions — e.g., when habitual joint policies happen to also minimize joint EFE — this term can be net negative and pays for itself.

**(iii) $I(q_\lambda) \geq 0$.** The multi-information term appears **with a plus sign** in [[EQ:tc_decomp]]: holding the marginals fixed, any genuine cross-stream correlation raises the Gibbs variational objective by exactly $I(q_\lambda)$ nats.  *When* joint structure still *pays off* for the agent is a comparison with the coupling / EFE / log-partition bundle in the same identity — not literal subtraction of $I$ from “free energy” in isolation.  [[THMREF:cor_4_2]]--[[THMREF:cor_4_4]] formalize the sign bookkeeping of that trade-off.

Read together, the three terms expose the central trade-off of policy entanglement.  The marginal sum (i) tracks how each stream is faring on its own slice of the deformed posterior; the coupling bundle (ii) is the *price tag* of maintaining the structure encoded in $J$ and $K_c$, and can be paid in either direction depending on whether habit and preference are aligned or in tension; the multi-information (iii) is the *correlation surcharge* that any non-mean-field joint owes purely for being correlated.  Coupling pays for itself precisely when the bundle (ii) is sufficiently negative to absorb both the correlation surcharge (iii) and any worsening of per-stream marginals (i).  Stating it this way also clarifies why the framework refuses to call (iii) a "cost" in isolation: $I(q_\lambda)$ is the price of joint structure measured *against* mean-field, but (i) and (ii) measure how much that structure buys back, and only the sum across all three is a meaningful free-energy comparison.

The Lean companions for the three immediate corollaries are auto-extracted below.

[[THMREF:cor_4_2]] (the *coupling-pays-for-itself* verdict) is a
tri-state classifier from the sign of the bookkeeping, *now upgraded
to a proved theorem* (`status: proved`) whose Lean form discharges the
sign-soundness identity by direct case analysis on the bookkeeping
variable:

[[LEAN:cor_4_2]]

[[THMREF:cor_4_3]] (mean-field reduction at $\lambda = 0$) collapses
the four-summand bookkeeping to its sum-of-marginals + total-
correlation-gain pair:

[[LEAN:cor_4_3]]

[[THMREF:cor_4_4]] (strict gain when $q$ is non-mean-field) is the
sign companion of [[EQREF:total_correlation]]. Unlike the two proved
corollaries above, its Lean companion is a typed boundary witness
(`status: boundary`, `faithfulness: typed-witness`): the strict-gain
inequality is carried as a typed contract, with the analytic discharge
at the Mathlib layer.

[[LEAN:cor_4_4]]

## Optimal coupling: existence of lambda*

**[[THMREF:thm_4_2]] (Existence of optimal coupling).** For fixed
$J, K_c$ with bounded potentials, $F[q_\lambda]$ is real-analytic in
$\lambda$ on $[0,\infty)$ and admits the closed exponential-family
identity

[[EQ:closed_form_F]]

The Lean boundary companion threads the algebraic identity through
the coupling-log-weight skeleton so every parameter
$(J, K_c, \gamma, \lambda)$ is genuinely referenced:

[[LEAN:thm_4_2]]


where $Z(\lambda) = \sum_\pi E_{\mathrm{MF}}(\pi)\,e^{\lambda(J-\gamma K_c)(\pi) - \gamma G_{\mathrm{MF}}(\pi)}$
is the normalizer of $q_\lambda$ and
$Z_E(\lambda) = \sum_\pi E_{\mathrm{MF}}(\pi)\,e^{\lambda J(\pi)}$ is
the normalizer of the entangled prior.  Differentiating once gives

[[EQ:dF_dlambda]]

so $\lambda \mapsto F[q_\lambda]$ has at least one stationary point in
$(0, \infty)$ whenever the marginal slope is negative,

$$
\langle J\rangle_{q_0} \;-\; \gamma\,\langle K_c\rangle_{q_0}
  \;>\; \langle J\rangle_{E_{\mathrm{MF}}},
$$

i.e.\ when the *posterior* coupling alignment net of EFE cost exceeds
the *prior* coupling alignment.  Since $F$ is real-analytic and bounded
below on $[0,\infty)$ — boundedness follows from the compactness of the
simplex on a finite $\Pi$ and the boundedness of the potentials $J$,
$K_c$, $G_k$ standing-assumed in [[SECREF:setup.mf_baseline]], so
$\log Z_E(\lambda)$ and $\log Z(\lambda)$ are continuous bounded
functions of $\lambda$ — and $F'(0) < 0$ under the stated marginal-slope
condition, $F'(\lambda)$ achieves a zero in some open interval and a
stationary point $\lambda^\star \in (0, \infty)$ exists.  Since the multi-information $I$
attains its minimum at the mean-field surface, $\mathrm{d}I/\mathrm{d}\lambda|_0 = 0$
identically.  To see this in one line: by the chain rule along the
e-geodesic, the covariance form is

[[EQ:mi_derivative_covariance]]

A derivation along the e-geodesic from the closed identity
[[EQREF:e_geodesic]] is in [[SECREF:heterogeneous]]; at $\lambda = 0$,
$q_0 = q_{\mathrm{MF}} = \hat m(q_0)$ pointwise (here $\hat m(q) = \prod_k q^k$
is the *m-projection* of $q$ onto the mean-field submanifold
$\mathcal{M}_{\mathrm{MF}}$, defined in [[SECREF:geometry.dual_coords]]), so
$\log q_0 - \log \hat m(q_0) \equiv 0$ on $\Pi$ and the covariance vanishes.
The *Fisher* contribution to $F$ therefore lives at second order
([[EQREF:d2F_dlambda2]] and [[THMREF:prop_10_1]]; see also
[[SECREF:app.convexity]]).  Under the symmetric standing prior
$E_{\mathrm{MF}} = \mathrm{Unif}$ with $\langle J\rangle_{E_{\mathrm{MF}}} = 0$,
the first-order condition collapses to the simpler form
$\langle J\rangle_{q_0} > \gamma\langle K_c\rangle_{q_0}$ used
throughout [[SECREF:examples]] and [[SECREF:comparative]].

**[[THMREF:thm_4_3]] (Convexity of $F$ in $\lambda$ — witness-form).** If $J - \gamma K_c$ is log-concave on $\Pi$ (in the finite-simplex sense developed in [[SECREF:app.convexity]]), then $\lambda \mapsto F[q_\lambda]$ is convex on $[0,\infty)$ and $\lambda^*$ is unique. The boundary fragment ships the witness-consuming Lean companion `Convexity.freeEnergy_convex_in_lam_witness`; the analytic content is a structural witness that Mathlib4 can discharge from convex-analysis and log-partition facts without changing the boundary theorem.

**[[THMREF:thm_4_3]] says,** in cognitive terms: when habit coupling and preference coupling are coherent (no internal contradictions in what joint policies the agent prefers and habituates), the optimal entanglement strength is uniquely determined.

When they are incoherent, the framework predicts *multiple stable coupling regimes* — a point we develop into a phase-structure analysis in [[SECREF:phase]].

## Takeaways

> **1. The decomposition is exact, not an approximation.**
> Variational free energy under the entangled posterior is *identically* the sum of per-stream marginal free energies, a coupling/partition bundle, and a non-negative multi-information term — see [[EQREF:tc_decomp]].
>
> **2. Coupling pays for itself iff the surplus exceeds the
> multi-information cost.**
> The optimum $\lambda^\star$ is determined by a single first-order
> condition balancing $\langle J - \gamma K_c\rangle$ against the
> total-correlation slope.
>
> **3. Coherent potentials yield a unique optimum;
> incoherent potentials predict phase regimes.**
> Convexity of $F$ in $\lambda$ ([[THMREF:thm_4_3]]) is the
> theoretical hinge: when it holds, $\lambda^\star$ is uniquely
> determined; when it fails, multiple stable couplings co-exist (see
> [[SECREF:phase]]).

---
