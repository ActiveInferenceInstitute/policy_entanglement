# Comparative Statics: Coupling Payoff, Two-Parameter Generalization, and Sensitivity Surfaces

This section answers: *given the structure of $J$ and $K_c$, what determines whether the optimal agent has $\lambda^* > 0$, and how large?*

## The pay-off structure

From the closed form [[EQREF:closed_form_F]]
([[SECREF:decomposition.optimal]] [[THMREF:thm_4_2]]) and the
first-derivative identity [[EQREF:dF_dlambda]], the marginal gain at
$\lambda = 0$ specializes to

$$
\frac{\partial F[q_\lambda]}{\partial \lambda}\Big|_0
  \;=\; \langle J\rangle_{E_{\mathrm{MF}}} \;-\; \langle J\rangle_{q_0}
  \;+\; \gamma\,\langle K_c\rangle_{q_0}.
$$

The total-correlation contribution $\partial I/\partial \lambda|_0$
vanishes identically because $I$ attains its minimum at the mean-field
submanifold ([[THMREF:prop_6_3]]); the multi-information's
$\lambda$-sensitivity is second-order Fisher information, not first
order ([[EQREF:d2F_dlambda2]]).  Under the standing assumption of a *centered* habit potential
under the bare prior, $\langle J\rangle_{E_{\mathrm{MF}}} = 0$ — true
by symmetry for every example in [[SECREF:examples]] and the standing
convention here onward — the marginal gain reduces to

$$
\frac{\partial F[q_\lambda]}{\partial \lambda}\Big|_0
  \;=\; \gamma\,\langle K_c\rangle_{q_0} \;-\; \langle J\rangle_{q_0},
$$

so coupling pays *in marginal terms* when

$$
\langle J\rangle_{q_0} \;>\; \gamma\,\langle K_c\rangle_{q_0}.
$$

In words: **coupling pays when the habitual cross-stream alignment is
more beneficial (under the current marginal posteriors) than the EFE
cost of cross-stream commitments.**  When the prior is asymmetric
($\langle J\rangle_{E_{\mathrm{MF}}} \ne 0$), the inequality picks up
the prior alignment $\langle J\rangle_{E_{\mathrm{MF}}}$ on the
right — habit coupling under the posterior must exceed *both* the EFE
cost and the prior alignment for first-order benefit.

## Two-parameter habit/EFE generalization

**The primary results in this paper use the single coupling parameter
$\lambda$ throughout** ([[SECREF:setup]], [[SECREF:lambda_deformation]],
[[SECREF:decomposition]]).  The two-parameter form below is recovered
from the single-$\lambda$ framework by the explicit substitution
$J \mapsto (\lambda_E/\lambda) \cdot J$ and
$K_c \mapsto (\lambda_G/\lambda) \cdot K_c$ — i.e., the dual-parameter
regime is *not a separate theory* but a re-parameterization in which
the habit and preference scales are absorbed into the coupling
potentials.  The corresponding structural statements (entanglement
decomposition [[THMREF:thm_4_1]], coupled-precision log-weight
geometry [[THMREF:thm_6_4]], and Schmidt-rank witness
[[THMREF:prop_7_1]]) carry through verbatim under this substitution.

Concretely, if we allow distinct precisions on habit-coupling vs.
preference-coupling:

$$
q_{\lambda_E,\lambda_G}(\pi) \propto \prod_k E_k(\pi^k)\exp(\lambda_E J(\pi))\exp(-\gamma\lambda_G K_c(\pi))\exp(-\gamma\sum_k G_k(\pi^k))
$$

then the open question is: under what conditions on $J, K_c$ does the
optimal $(\lambda_E^\star, \lambda_G^\star)$ lie on the diagonal
$\lambda_E = \lambda_G$? When it does not, the agent benefits from
**decoupling habit precision from preference-cost precision** —
habits can be maintained in a regime where preference penalties are
softened, or vice versa. This suggests a computational-psychiatry
modeling hypothesis rather than a validated diagnostic claim:
anxiety-like overconstraint would correspond to
$\lambda_G \gg \lambda_E$ (preference-cost dominates), while
habit-like automaticity would correspond to $\lambda_E \gg \lambda_G$.
The current manuscript validates the single-parameter coefficient
logic; the two-parameter locus remains a clearly marked follow-up
analysis.

## Sensitivity to potential structure

For sparse pairwise $J = \sum_{(i,j)\in\mathcal{C}} J_{ij}$, the optimal $\lambda^*$ is determined by the *spectral radius* of the Fisher matrix at the MF point, evaluated on the coupling support. Rigorously:

**[[THMREF:prop_10_1]] (witness-form; live Lean companion
`Convexity.freeEnergy_localConcavity_at_zero_witness`).** Differentiating
the closed form [[EQREF:closed_form_F]] twice and using the standard
exponential-family identity
$\mathrm{d}^2 \log Z/\mathrm{d}\lambda^2 = \mathrm{Var}(\text{stat})$
— with interchange of $\partial/\partial\lambda$ and $\mathbb{E}_q$
justified by finite-sum differentiation on the policy alphabet —
gives [[EQREF:d2F_dlambda2]], and at $\lambda = 0$ specifically

$$
\frac{\partial^2 F}{\partial \lambda^2}\Big|_0
  \;=\; \mathrm{Var}_{E_{\mathrm{MF}}}(J)
  \;-\; \mathrm{Var}_{q_0}(J - \gamma K_c).
$$

The right-hand side is negative — i.e.\ $F$ is locally *concave* at
$\lambda = 0$, and the mean-field baseline is a local saddle in the
joint-policy direction — whenever the *posterior* dispersion of the
combined coupling statistic exceeds the *prior* dispersion of the
habit coupling.  Two regimes make this fail:

* **Constant statistic.**  If $J - \gamma K_c$ is $q_0$-a.s.\ constant,
  the right variance vanishes and $\partial^2 F / \partial \lambda^2|_0 \geq 0$ —
  the coupling has no first-order effect.
* **Strongly habit-anchored prior.**  If the bare prior $E_{\mathrm{MF}}$
  already concentrates $J$ tightly (large $\mathrm{Var}_{E_{\mathrm{MF}}}(J)$)
  while the per-stream EFE damps the posterior dispersion of
  $J - \gamma K_c$, the saddle property weakens.

In every other case — including all the worked examples of
[[SECREF:examples]], where $E_{\mathrm{MF}}$ is uniform so
$\mathrm{Var}_{E_{\mathrm{MF}}}(J) = \langle J^2\rangle$ is small
relative to the posterior-amplified statistic — the mean-field
baseline is a genuine saddle and *some* coupling pays for itself.
The interesting question is therefore not whether to couple but *how
much*, governed by the higher-order structure of $F$ in $\lambda$.

The locus of $\lambda^\star(\Delta_{\mathrm{util}}, \gamma)$ for the
K=2 Ising toy is shown below ([[FIGREF:lambda_star_locus]]); it sweeps
sigmoidally in the utility surplus and is amplified by larger EFE
precision $\gamma$.

[[FIG:lambda_star_locus]]

---
