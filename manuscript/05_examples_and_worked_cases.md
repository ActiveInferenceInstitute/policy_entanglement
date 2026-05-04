# Examples and Worked Cases

## The K=2 Bernoulli toy: full closed form

Two streams, each with two policies: $\Pi^1 = \Pi^2 = \{0,1\}$. Marginal priors $E_k = \mathrm{Unif}$. Marginal EFEs $G_k(0) = G_k(1) = 0$ (so the streams are EFE-degenerate; all action is in the coupling). Bilinear coupling $J(\pi^1, \pi^2) = J_0\,(2\pi^1 - 1)(2\pi^2 - 1)$ — i.e., $J = +J_0$ on aligned, $J = -J_0$ on anti-aligned. Set $\gamma K_c = 0$ for clarity.

Then

$$q_\lambda(\pi^1, \pi^2) = \frac{e^{\lambda J_0\, (2\pi^1-1)(2\pi^2-1)}}{Z(\lambda)}, \qquad Z(\lambda) = 2(e^{\lambda J_0} + e^{-\lambda J_0}) = 4\cosh(\lambda J_0).$$

Marginals: $q_\lambda^1(\pi^1) = q_\lambda^2(\pi^2) = 1/2$ (symmetry). Total correlation:

$$I(q_\lambda) = -\log 2 \cdot 0 + \log 2 + \frac{e^{\lambda J_0}\log e^{\lambda J_0} + e^{-\lambda J_0}\log e^{-\lambda J_0}}{2(e^{\lambda J_0}+e^{-\lambda J_0})} - \log Z(\lambda) + 2\log 2$$

Simplification using $\tanh$:

$$\boxed{\;I(q_\lambda) = \lambda J_0 \tanh(\lambda J_0) - \log\cosh(\lambda J_0)\;}$$

This is the well-known mutual information of an Ising pair at inverse temperature $\lambda J_0$. The free energy decomposition becomes:

$$F[q_\lambda] = 2 F_{\mathrm{marg}} - \lambda \cdot J_0 \tanh(\lambda J_0) - I(q_\lambda)$$

since $\langle J\rangle = J_0\tanh(\lambda J_0)$ for this toy.

**Optimal $\lambda^*$:** taking $dF/d\lambda = 0$,

$$\frac{dF}{d\lambda} = -J_0\tanh(\lambda J_0) - \lambda J_0^2 \mathrm{sech}^2(\lambda J_0) - \frac{dI}{d\lambda} = 0.$$

In the regime where marginal free energies are symmetric and the EFE term vanishes, $\lambda^* \to \infty$ (the system always benefits from more coupling) — a degeneracy that resolves once $G_k \neq 0$ or $K_c$ is reintroduced. This is the *Ising-like* limit.

The toy is genuinely instructive: it shows that with no preference coupling, an agent will couple its policies *as much as possible*. The role of $K_c$ is to act as the cost regulator that prevents runaway entanglement. This is the formal version of "habits are cheap; planning to satisfy preferences is expensive."

The closed-form mutual-information curve [[EQREF:ising_mi_closed_form]],
the empirical numerical realisation, and the joint posterior at a
representative $\lambda = 2$ are reproduced numerically by
[`scripts/parameter_sweep.py`](../scripts/parameter_sweep.py) and
visualised below; agreement with the closed form is to floating
tolerance ($10^{-6}$ over 121 grid points, see
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

A simulation (planned, [[SECREF:empirical]]) sweeps $\lambda$ and reports: (a) joint-action accuracy, (b) total correlation, (c) Schmidt entropy (next section), and (d) free energy. The expected curve shapes are: accuracy monotone increasing in $\lambda$ until a plateau; total correlation monotone increasing then saturating; Schmidt entropy peaks near $\lambda^*$ then collapses for very large $\lambda$ (when archetypes dominate); free energy U-shaped with minimum at $\lambda^*$.

The closed-form $\lambda^\star(\Delta_{\mathrm{util}})$ curve for the
symmetric K=2 toy (see [[EQREF:optimal_lambda]]) is plotted below; the
saturating monotone shape is recovered numerically by
[`src/lean/bernoulli_toy.py::optimal_lambda`](../src/lean/bernoulli_toy.py).
Numerical anchors: $\lambda^\star(0.5) = [[VAR:lambda_star_delta_05:.4f]]$,
$\lambda^\star(0.9) = [[VAR:lambda_star_delta_09:.4f]]$.

[[FIG:optimal_lambda]]

[[FIG:free_energy_curve]]

## Multi-timescale coupling

Stream 1 = fast attentional, $T_1 = 1$. Stream 2 = slow navigational, $T_2 = 10$. Sparse hierarchical $J$: only the first action of $\pi^2$ couples to $\pi^1$. This is exactly the structure of hierarchical AIF [@pezzulo-2018], and [[SECREF:connections.hierarchical]] proves the limit equivalence formally.

---
