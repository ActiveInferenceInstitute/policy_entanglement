# Worked Examples: Bernoulli Toy, Motor-Attention Coupling, and Multi-Timescale Coupling

## The K=2 Bernoulli toy: full closed form

In the symmetric $K=2$ Bernoulli toy (defined just below) the closed-form
multi-information has the body-scaling identity
$$
I(\lambda) \;=\; \lambda J_0\,\tanh(\lambda J_0) \;-\; \log\cosh(\lambda J_0)
              \;=\; \log 2 \;-\; H_b\!\big(\sigma(2\lambda J_0)\big),
$$
where $H_b$ is binary entropy and $\sigma$ is the logistic; the
appendix-scaling form ($J \in \{\pm\tfrac12\}$) is derived line-by-line
in [[SECREF:app.bernoulli]].  *Not* $I(\lambda) = \log\cosh\lambda$, which
would be an algebra error.

Two streams, each with two policies: $\Pi^1 = \Pi^2 = \{0,1\}$. Marginal priors $E_k = \mathrm{Unif}$. Marginal EFEs $G_k(0) = G_k(1) = 0$ (so the streams are EFE-degenerate; all action is in the coupling). Bilinear coupling $J(\pi^1, \pi^2) = J_0\,(2\pi^1 - 1)(2\pi^2 - 1)$ — i.e., $J = +J_0$ on aligned, $J = -J_0$ on anti-aligned. Set $\gamma K_c = 0$ for clarity.

The joint posterior is
$$
q_\lambda(\pi^1, \pi^2) \;=\; E_{\mathrm{MF}}(\pi)\,\frac{e^{\lambda J(\pi)}}{Z(\lambda)}
\;=\; \frac{e^{\lambda J_0\,(2\pi^1-1)(2\pi^2-1)}}{4\cosh(\lambda J_0)},
$$
with the **normalized-joint partition** (using the normalized mean-field
prior $E_{\mathrm{MF}}(\pi) = 1/4$ on each of the four atoms)

$$
Z(\lambda) \;=\; \sum_\pi E_{\mathrm{MF}}(\pi)\,e^{\lambda J(\pi)}
\;=\; \tfrac{1}{4}\big(2 e^{\lambda J_0} + 2 e^{-\lambda J_0}\big)
\;=\; \cosh(\lambda J_0).
$$

(The factor $1/4$ comes from $E_{\mathrm{MF}}$; the unnormalized atom-sum
$2 e^{\lambda J_0} + 2 e^{-\lambda J_0} = 4\cosh(\lambda J_0)$ is *four*
times $Z(\lambda)$.) So $q_\lambda(\pi) = E_{\mathrm{MF}}(\pi)\,e^{\lambda J(\pi)}/Z(\lambda) = e^{\lambda J(\pi)}/(4\cosh(\lambda J_0))$, as displayed above.

Marginals: $q_\lambda^1(\pi^1) = q_\lambda^2(\pi^2) = 1/2$ (symmetry,
so $H(q_\lambda^k) = \log 2$).  For the joint, the four atoms have
masses $\sigma(2\lambda J_0)/2$ on the two aligned configurations and
$(1 - \sigma(2\lambda J_0))/2$ on the two anti-aligned, where
$\sigma(x) = 1/(1+e^{-x})$ is the logistic.  Direct computation gives
the joint entropy
$H(q_\lambda) = \log 2 + H_b(\sigma(2\lambda J_0))$ with binary
entropy $H_b(p) = -p\log p - (1-p)\log(1-p)$.  The total
correlation is then

$$
I(q_\lambda) \;=\; \sum_k H(q_\lambda^k) - H(q_\lambda)
              \;=\; 2\log 2 - \log 2 - H_b(\sigma(2\lambda J_0))
              \;=\; \log 2 - H_b(\sigma(2\lambda J_0)).
$$

Equivalently, in $\tanh$ form (the algebraic identity
$\log 2 - H_b(\sigma(x)) = \tfrac{x}{2}\tanh(x/2) - \log\cosh(x/2)$):

[[EQ:ising_mi_closed_form]]

This is the well-known mutual information of an Ising pair at inverse
temperature $\lambda J_0$.  See [[SECREF:app.bernoulli]] for the line-by-line
derivation; the body uses the bilinear scaling $J = J_0(2\pi^1-1)(2\pi^2-1)$
while the appendix uses the swing-$\tfrac12$ form $J \in \{\pm\tfrac12\}$,
related by $\lambda_{\mathrm{body}} \cdot J_0 = \lambda_{\mathrm{app}}/2$.

The free energy decomposition [[EQ:tc_decomp]], applied with $K_c = 0$ and both marginal free energies $F[q_\lambda^k] = 0$ (symmetric priors, zero per-stream EFE), gives:

$$
F[q_\lambda] = \log\cosh(\lambda J_0) - \lambda J_0 \tanh(\lambda J_0) + I(q_\lambda) = 0,
$$

since $\log Z_E(\lambda) = \log\cosh(\lambda J_0)$, $\lambda\langle J\rangle_{q_\lambda} = \lambda J_0\tanh(\lambda J_0)$, and $I(q_\lambda) = \lambda J_0\tanh(\lambda J_0) - \log\cosh(\lambda J_0)$ — these three terms cancel identically.  The result $F[q_\lambda] \equiv 0$ is expected: when $G_k = K_c = 0$ the posterior equals the prior ($q_\lambda = \mathcal{E}_\lambda$) and the Gibbs variational objective is zero by construction.

**Optimal $\lambda^*$:** Because $F[q_\lambda] = 0$ for all $\lambda$, the VFE landscape is *flat* — there is no free-energy gradient to set $\lambda$.  This is the *degenerate Ising limit*, and it resolves the moment $G_k \neq 0$ or $K_c \neq 0$, whereupon a well-defined finite $\lambda^\star$ appears (see [[SECREF:examples.motor_attention]]).

The toy is genuinely instructive: it isolates the pure role of the habit potential $J$.  Without a preference coupling $K_c$, free energy places no penalty on entanglement — all coupling levels are equally consistent with the model.  The role of $K_c$ is to create the free-energy gradient that controls $\lambda^\star$; this is the formal version of "habits are cheap; planning to satisfy preferences is expensive."

The closed-form mutual-information curve [[EQREF:ising_mi_closed_form]],
the empirical numerical realization, and the joint posterior at a
representative $\lambda = 2$ are reproduced numerically by
[`scripts/parameter_sweep.py`](../scripts/parameter_sweep.py) and
visualized below; agreement with the closed form is to floating
tolerance ($\leq [[VAR:param_sweep_agreement_tolerance:.0e]]$ over
$[[VAR:param_sweep_grid_points]]$ grid points spanning
$\lambda \in [[[VAR:param_sweep_lambda_min:g]],
[[VAR:param_sweep_lambda_max:g]]]$, see
[`output/data/parameter_sweep.csv`](../output/data/parameter_sweep.csv)).
Sentinel values:
$I(\lambda=1) = [[VAR:ising_mi_at_lam_1:.4f]]$ nats,
$I(\lambda=2) = [[VAR:ising_mi_at_lam_2:.4f]]$ nats.

[[FIG:joint_heatmap_lambda2]]

[[FIG:ising_mi_curve]]

## Two-stream motor + attention with realistic EFE

Stream 1 = motor (reach left vs. reach right). Stream 2 = attention (look left vs. look right). Per-stream EFEs: $G_1$ depends on a hidden target location; $G_2$ depends on epistemic value of foveation. Habit coupling $J$ = strong positive on aligned (look-where-you-reach) and slightly negative on anti-aligned. $K_c$ = mild positive penalty on simultaneous-novel-action ("don't change two things at once").

This recovers a familiar pattern: optimal $\lambda^*$ is finite and
positive; the agent learns to align gaze and reach habitually, but the
EFE cost of doubling novelty prevents over-rigidity.  Empirically (see
[`scripts/manuscript_variables.py::_motor_attention_facts`](../scripts/manuscript_variables.py)),
the joint probability of an *aligned* (look-where-you-reach) outcome
grows from $P_{\mathrm{align}}(\lambda=0) = [[VAR:motor_attention_aligned_prob_lam_0:.4f]]$
to $P_{\mathrm{align}}(\lambda=1) = [[VAR:motor_attention_aligned_prob_lam_1:.4f]]$
to $P_{\mathrm{align}}(\lambda=2) = [[VAR:motor_attention_aligned_prob_lam_2:.4f]]$.

The empirical suite in [[SECREF:empirical]] already sweeps $\lambda$ and
renders the relevant observables rather than leaving them as a schematic:
total correlation, Schmidt entropy ([[SECREF:spectral]]), free-energy
surfaces, aligned-policy mass, and tensor-train rank profiles.  In the
two-stream worked example, the show-not-tell pattern is visible in
[[FIGREF:ising_mi_curve]], [[FIGREF:schmidt_entropy_surface]], and
[[FIGREF:free_energy_curve]]: total correlation grows and saturates,
Schmidt entropy rises away from the mean-field boundary and then bends
toward the archetypal regime, and the free-energy surface identifies the
coupling range where the utility surplus pays for the information cost.

The closed-form **alignment-inversion** map
$\lambda^\star(\Delta_{\mathrm{align}})$ for the symmetric K=2 toy — i.e.
the coupling that *realizes* a given target alignment
$\Delta_{\mathrm{align}} = \alpha(\lambda) = \tanh(\lambda/2)$ — is

[[EQ:optimal_lambda]]

(see [[EQREF:optimal_lambda]]; this is target-alignment inversion, *not*
the free-energy first-order condition, which is treated as a separate
VFE-optimization problem in [[SECREF:app.bernoulli]] and reduces to
$\lambda^\star = 2u$ in the small-utility limit).  The saturating
monotone shape is recovered numerically by
[`src/lean/bernoulli_toy.py::optimal_lambda`](../src/lean/bernoulli_toy.py).
Numerical anchors: $\lambda^\star(0.5) = [[VAR:lambda_star_delta_05:.4f]]$,
$\lambda^\star(0.9) = [[VAR:lambda_star_delta_09:.4f]]$.

[[FIG:optimal_lambda]]

[[FIG:free_energy_curve]]

## Multi-timescale coupling

One stream can be read as fast attentional control and another as a
slower navigational plan.  A sparse hierarchical $J$ that couples the
fast policy to the first decision point of the slower policy illustrates
the *coupling shadow* of hierarchical AIF [@pezzulo-2018]: the posterior
records cross-level compatibility without claiming to reproduce the full
directed message-passing schedule or temporal-scale separation of the
source process theory.  [[SECREF:connections.hierarchical]] states the
corresponding witness-form concentration claim and its limitations.

---
