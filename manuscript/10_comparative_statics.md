# Comparative Statics: When Does Coupling Pay?

This section answers: *given the structure of $J$ and $K_c$, what determines whether the optimal agent has $\lambda^* > 0$, and how large?*

## The pay-off structure

From [[SECREF:decomposition.optimal]], the marginal gain at $\lambda = 0$ is:

$$\frac{\partial F[q_\lambda]}{\partial \lambda}\Big|_0 = -\langle J\rangle_{q_0} + \gamma \langle K_c\rangle_{q_0}.$$

(The total-correlation term $-\partial I/\partial \lambda|_0 = 0$ because $I$ is at a minimum at $\lambda = 0$.) Coupling pays in marginal terms when:

$$\langle J\rangle_{q_0} > \gamma \langle K_c\rangle_{q_0}.$$

In words: **coupling pays when the habitual cross-stream alignment is more beneficial (under the current marginal posteriors) than the EFE cost of cross-stream commitments.**

## Two-parameter (lambda_E, lambda_G) generalization

If we allow distinct precisions on habit-coupling vs. preference-coupling:

$$q_{\lambda_E,\lambda_G}(\pi) \propto \prod_k E_k(\pi^k)\exp(\lambda_E J(\pi))\exp(-\gamma\lambda_G K_c(\pi))\exp(-\gamma\sum_k G_k(\pi^k))$$

we get an open question: under what conditions on $J, K_c$ does the optimal $(\lambda_E^*, \lambda_G^*)$ lie on the diagonal $\lambda_E = \lambda_G$? When it does not, the agent benefits from **decoupling habit precision from preference-cost precision** — habits can be maintained in a regime where preference penalties are softened, or vice versa. This is computational psychiatry territory: *anxious* phenotypes plausibly correspond to $\lambda_G \gg \lambda_E$ (preference-cost dominates), *automatic/habitual* to $\lambda_E \gg \lambda_G$.

## Sensitivity to potential structure

For sparse pairwise $J = \sum_{(i,j)\in\mathcal{C}} J_{ij}$, the optimal $\lambda^*$ is determined by the *spectral radius* of the Fisher matrix at the MF point, evaluated on the coupling support. Rigorously:

**[[THMREF:prop_10_1]].** At $\lambda = 0$, the second derivative of $F$ with respect to $\lambda$ is:

$$\frac{\partial^2 F}{\partial \lambda^2}\Big|_0 = -\mathrm{Var}_{q_0}(J - \gamma K_c).$$

This is negative — i.e., $F$ is locally *concave* near $\lambda = 0$. Therefore *any* $J - \gamma K_c$ that is non-trivially a function of $\pi$ (i.e., not constant) gives an immediate decrease in $F$ for small $\lambda > 0$. **Mean-field is generically a local saddle of free energy in the joint policy direction.**

This is a striking result: *if you can couple at all, you should*. The mean-field baseline is never a free-energy minimum in directions of non-trivial coupling. The interesting question is therefore not whether to couple but *how much*, governed by the higher-order structure of $F$ in $\lambda$.

The locus of $\lambda^\star(\Delta_{\mathrm{util}}, \gamma)$ for the
K=2 Ising toy is shown below; it sweeps sigmoidally in the utility
surplus and is amplified by larger EFE precision $\gamma$.

[[FIG:lambda_star_locus]]

---
