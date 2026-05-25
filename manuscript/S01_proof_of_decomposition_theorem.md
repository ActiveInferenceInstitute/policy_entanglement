```{=latex}
\appendix
```

# Proof of the Entanglement Decomposition

We prove the decomposition identity stated in [[SECREF:decomposition.statement]]
([[THMREF:thm_4_1]], *entanglement decomposition theorem*), namely
[[EQ:tc_decomp]].

The Lean type-level statement is in
[`lean/ActinfPolicyEntanglement/Decomposition.lean`](../lean/ActinfPolicyEntanglement/Decomposition.lean)
(`entanglement_decomposition`); the numerical realization lives in
[`src/lean/decomposition.py`](../src/lean/decomposition.py) and is exercised by
[`tests/test_decomposition.py`](../tests/test_decomposition.py).

## Definitions

$$
F[q_\lambda] \;\equiv\; \mathbb{E}_{q_\lambda}[\gamma G_\lambda] - \mathbb{E}_{q_\lambda}[\log \mathcal{E}_\lambda] - H(q_\lambda),
$$

$$
F[q_\lambda^k] \;\equiv\; \mathbb{E}_{q_\lambda^k}[\gamma G_k] - \mathbb{E}_{q_\lambda^k}[\log E_k] - H(q_\lambda^k),
$$

with $G_\lambda(\pi)=\sum_k G_k(\pi^k)+\lambda K_c(\pi)$ and, for the
**normalized** entangled prior $\mathcal{E}_\lambda \propto \big(\prod_k E_k\big)\,e^{\lambda J}$,

$$
\log \mathcal{E}_\lambda(\pi) \;=\; \sum_k \log E_k(\pi^k) + \lambda J(\pi) - \log Z_E(\lambda).
$$

## Expanding the EFE expectation

$$
\gamma G_\lambda(\pi) \;=\; \gamma\sum_k G_k(\pi^k) + \gamma\lambda K_c(\pi),
$$

so

$$
\mathbb{E}_{q_\lambda}[\gamma G_\lambda] \;=\; \gamma\sum_k \mathbb{E}_{q_\lambda^k}[G_k] + \gamma\lambda\langle K_c\rangle_{q_\lambda}.
$$

## Expanding the prior log-expectation

$$
\mathbb{E}_{q_\lambda}[\log \mathcal{E}_\lambda] \;=\; \sum_k \mathbb{E}_{q_\lambda^k}[\log E_k] + \lambda\langle J\rangle_{q_\lambda} - \log Z_E(\lambda).
$$

## Combining

Substitute both expansions into the definition of $F[q_\lambda]$:

$$
\begin{aligned}
F[q_\lambda] &= \sum_k \Big(\gamma \mathbb{E}_{q_\lambda^k}[G_k] - \mathbb{E}_{q_\lambda^k}[\log E_k]\Big) - H(q_\lambda) + \gamma\lambda\langle K_c\rangle_{q_\lambda} - \lambda\langle J\rangle_{q_\lambda} + \log Z_E(\lambda) \\
             &= \sum_k F[q_\lambda^k] + \sum_k H(q_\lambda^k) - H(q_\lambda) + \gamma\lambda\langle K_c\rangle_{q_\lambda} - \lambda\langle J\rangle_{q_\lambda} + \log Z_E(\lambda).
\end{aligned}
$$

Finally, using the multi-information identity $\sum_k H(q_\lambda^k) - H(q_\lambda) = I(q_\lambda)$ and [[EQ:total_correlation]],

$$
\boxed{\;F[q_\lambda] \;=\; \sum_k F[q_\lambda^k] \;+\; \gamma\lambda\langle K_c\rangle_{q_\lambda} \;+\; \log Z_E(\lambda) \;-\; \lambda\langle J\rangle_{q_\lambda} \;+\; I(q_\lambda).\;}
$$

This is exactly the registry equation [[EQ:tc_decomp]].  The Python helper
`entanglement_decomposition_rhs` sums the same four grouped pieces:
$\sum_k F[q^k]$,
`coupling_cost_term` $=\gamma\lambda\mathbb{E}[K_c]$,
`coupling_prior_term` $=\log Z_E(\lambda)-\lambda\mathbb{E}[J]$,
`total_correlation_gain` $=I(q)$.

Numeric agreement with the Gibbs definition of $F[q_\lambda]$ is checked in
`tests/test_decomposition.py` (identity on random joints).

## Interpretation (sign of $I$)

The multi-information $I(q_\lambda)$ is **non-negative** and vanishes iff
$q_\lambda$ is mean-field.  In the displayed Gibbs expansion it appears with a
**plus** sign: departures from factorization incur an entropy surplus
relative to independent streams holding the same marginals.  Trade-offs with
the coupling and EFE terms determine whether $\lambda>0$ is *optimal* for a
given agent — [[SECREF:examples]] and [[THMREF:cor_4_2]] make that comparison
explicit.

## Closed exponential-family form (collapsed identity)

The same expansion admits a strikingly compact closed form that the
body uses to differentiate $F$ with respect to $\lambda$ in
[[THMREF:thm_4_2]] and [[THMREF:prop_10_1]].  Let
$Z_E(\lambda) = \sum_\pi E_{\mathrm{MF}}(\pi)\,e^{\lambda J(\pi)}$ be
the entangled-prior normalizer and
$Z(\lambda) = \sum_\pi E_{\mathrm{MF}}(\pi)\,e^{\lambda(J - \gamma K_c)(\pi) - \gamma G_{\mathrm{MF}}(\pi)}$
the joint posterior normalizer.  Substituting
$\log q_\lambda(\pi) = \log E_{\mathrm{MF}}(\pi) - \gamma G_{\mathrm{MF}}(\pi)
                       + \lambda(J(\pi) - \gamma K_c(\pi)) - \log Z(\lambda)$
into $F[q_\lambda] = \mathbb{E}_{q_\lambda}[\gamma G_\lambda - \log \mathcal{E}_\lambda] - H(q_\lambda)$
(with $H(q_\lambda) = -\mathbb{E}_{q_\lambda}[\log q_\lambda]$) cancels every
expectation term and leaves the registered identity
[[EQREF:closed_form_F]]:

[[EQ:closed_form_F]]

The Gibbs decomposition above and this closed identity are the same
fact; one is *additive over streams*, the other *multiplicative
through normalizers*.  The closed form makes derivatives in $\lambda$
trivial via standard exponential-family identities,

$$
\frac{\mathrm{d}}{\mathrm{d}\lambda}\log Z_E(\lambda)
  = \langle J\rangle_{\mathcal{E}_\lambda},
\qquad
\frac{\mathrm{d}}{\mathrm{d}\lambda}\log Z(\lambda)
  = \langle J - \gamma K_c\rangle_{q_\lambda},
$$

so the registered first- and second-derivative forms
[[EQREF:dF_dlambda]] and [[EQREF:d2F_dlambda2]] follow:

[[EQ:dF_dlambda]]

[[EQ:d2F_dlambda2]]

These are the formulas that [[THMREF:thm_4_2]] (existence of
$\lambda^\star$) and [[THMREF:prop_10_1]] (sign of the second
derivative at $\lambda = 0$) consume; [[SECREF:app.convexity]] uses
the same identity to characterize convexity of $F$ in $\lambda$.
