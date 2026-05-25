# Convexity of Free Energy in Lambda: Conditions and Counter-Example

The free-energy curve along the λ-deformation has a clean
exponential-family structure that delivers convexity in $\lambda$ on
the natural side.  We sketch the proof here; the closed-form K = 2
case is verified numerically by
[`scripts/generate_figures.py`](../scripts/generate_figures.py)
(see [`output/figures/free_energy_curve.png`](../output/figures/free_energy_curve.png)).

## The closed exponential-family form

[[SECREF:app.proof_decomp]] establishes the closed identity

$$
F[q_\lambda] \;=\; \log Z_E(\lambda) \;-\; \log Z(\lambda),
$$

where the two normalizers are the entangled prior $\mathcal{E}_\lambda$
and the entangled posterior $q_\lambda$ respectively.  Each is the
log-partition of an exponential family in $\lambda$ — natural
parameter $\lambda$, sufficient statistic $J$ (for the prior side)
and $J - \gamma K_c$ (for the posterior side).  Standard
exponential-family identities give

$$
\frac{\mathrm{d}}{\mathrm{d}\lambda}\log Z_E(\lambda)
  = \langle J\rangle_{\mathcal{E}_\lambda},
\qquad
\frac{\mathrm{d}^2}{\mathrm{d}\lambda^2}\log Z_E(\lambda)
  = \mathrm{Var}_{\mathcal{E}_\lambda}(J),
$$

and analogously for $\log Z(\lambda)$ with statistic $J - \gamma K_c$
and reference distribution $q_\lambda$.  Both log-partitions are
*convex* in $\lambda$; their *difference* is a question of which
side is "more convex" in $\lambda$.

## The convexity ledger

Differentiating the closed identity once more:

$$
\frac{\mathrm{d}^2 F[q_\lambda]}{\mathrm{d}\lambda^2}
  \;=\; \mathrm{Var}_{\mathcal{E}_\lambda}(J)
  \;-\; \mathrm{Var}_{q_\lambda}(J - \gamma K_c).
$$

Hence:

* **Convex regime** — $F''(\lambda) \geq 0$ on an interval iff the
  *prior* dispersion of $J$ exceeds the *posterior* dispersion of
  $J - \gamma K_c$ throughout that interval.  This holds, e.g.,
  whenever the posterior concentrates much faster than the prior in
  the natural-parameter direction (large $\gamma$, sharply peaked
  $G_k$).
* **Concave / saddle regime** — $F''(\lambda) \leq 0$ when the
  posterior dispersion dominates.  This is the regime in which
  raising $\lambda$ pays for itself first-order: every example in
  [[SECREF:examples]] starts here at $\lambda = 0$ ([[THMREF:prop_10_1]]).
* **Inflection / mixed regime** — $F''$ may change sign exactly once
  along $[0, \infty)$, locating an *inflection coupling*
  $\lambda_{\mathrm{infl}}$ that separates the two regimes.  Below
  $\lambda_{\mathrm{infl}}$ the agent benefits from *more* coupling;
  above, marginal returns reverse — the location of the optimal
  $\lambda^\star$ ([[SECREF:decomposition.optimal]]).

## Sufficient condition for global convexity on $[0, \infty)$

If for every $\lambda \geq 0$ the prior dispersion of the habit
coupling dominates the posterior dispersion of the combined
statistic,

$$
\mathrm{Var}_{\mathcal{E}_\lambda}(J)
  \;\geq\; \mathrm{Var}_{q_\lambda}(J - \gamma K_c)
\qquad \text{for all } \lambda \geq 0,
$$

then $F[q_\lambda]$ is convex on $[0, \infty)$ and $\lambda^\star$ is
unique.  This is the crisp form of [[THMREF:thm_4_3]] in the language
of dispersion comparison; the original "log-concavity of $J - \gamma K_c$"
sufficient condition implies this dispersion inequality on the natural
domain via Brascamp–Lieb (we omit the standard argument).

## K = 2 Symmetric Ising specialization

In the symmetric K = 2 Ising example with uniform $E_{\mathrm{MF}}$,
zero per-stream EFE, and bilinear $J = J_0(2\pi^1 - 1)(2\pi^2 - 1)$:

$$
\log Z_E(\lambda) = \log\cosh(\lambda J_0),
\qquad
\log Z(\lambda) = \log\cosh(\lambda J_0)
$$

(both partition functions agree because $\gamma K_c \equiv 0$ here),
so $F[q_\lambda] \equiv 0$ — the toy is *flat* in $\lambda$ when no
preference coupling is present.  Adding a utility-driven $G$ shifts
$\log Z(\lambda)$ but leaves $\log Z_E$ invariant; the resulting
$F[q_\lambda] = \log\cosh(\lambda J_0) - \log Z(\lambda)$ is convex
in $\lambda$ on $[0, \infty)$ for any utility level (verified
numerically across $u \in \{0, 0.5, 1, 2\}$ in
[`output/figures/free_energy_curve.png`](../output/figures/free_energy_curve.png)).

## Numerical verification

The K = 2 Ising free-energy curve at four utility values is plotted
in [`output/figures/free_energy_curve.png`](../output/figures/free_energy_curve.png).
The curve is monotonically decreasing in $|\lambda|$ for any
$u \geq 0$, consistent with convexity (and with the closed-form
expression in [[SECREF:app.bernoulli]]).
