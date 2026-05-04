```{=latex}
\appendix
```

# Full Proof of the Entanglement Decomposition Theorem

We prove the decomposition identity stated in the body
(*entanglement decomposition theorem*), namely

$$
F[q_\lambda] \;=\; \sum_k F[q_\lambda^k] \;+\; \lambda\big(\gamma\langle K_c\rangle - \langle J\rangle\big) \;+\; \log Z_E(\lambda) \;+\; I(q_\lambda).
$$

The Lean type-level statement is in
[`lean/ActinfPolicyEntanglement/Decomposition.lean`](../lean/ActinfPolicyEntanglement/Decomposition.lean)
(`entanglement_decomposition`); the numerical realisation lives in
[`src/lean/decomposition.py`](../src/lean/decomposition.py) and is exercised by
[`tests/test_decomposition.py`](../tests/test_decomposition.py).

## Definitions

$$
F[q_\lambda] \;\equiv\; \mathbb{E}_{q_\lambda}[\gamma G_\lambda] - \mathbb{E}_{q_\lambda}[\log \mathcal{E}_\lambda] - H(q_\lambda),
$$

$$
F[q_\lambda^k] \;\equiv\; \mathbb{E}_{q_\lambda^k}[\gamma G_k] - \mathbb{E}_{q_\lambda^k}[\log E_k] - H(q_\lambda^k).
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
\log \mathcal{E}_\lambda(\pi) \;=\; \sum_k \log E_k(\pi^k) + \lambda J(\pi) - \log Z_E(\lambda),
$$

so

$$
\mathbb{E}_{q_\lambda}[\log \mathcal{E}_\lambda] \;=\; \sum_k \mathbb{E}_{q_\lambda^k}[\log E_k] + \lambda\langle J\rangle_{q_\lambda} - \log Z_E(\lambda).
$$

## Combining

Substitute both expansions into the definition of $F[q_\lambda]$ and group:

$$
\begin{aligned}
F[q_\lambda] &= \gamma\sum_k \mathbb{E}_{q_\lambda^k}[G_k] + \gamma\lambda\langle K_c\rangle - \sum_k \mathbb{E}_{q_\lambda^k}[\log E_k] - \lambda\langle J\rangle + \log Z_E(\lambda) - H(q_\lambda) \\
             &= \sum_k\Big(\gamma \mathbb{E}_{q_\lambda^k}[G_k] - \mathbb{E}_{q_\lambda^k}[\log E_k]\Big) + \lambda\big(\gamma\langle K_c\rangle - \langle J\rangle\big) + \log Z_E(\lambda) - H(q_\lambda).
\end{aligned}
$$

Using $\sum_k F[q_\lambda^k] = \sum_k\big(\gamma\mathbb{E}[G_k] - \mathbb{E}[\log E_k]\big) - \sum_k H(q_\lambda^k)$,

$$
\sum_k\Big(\gamma \mathbb{E}_{q_\lambda^k}[G_k] - \mathbb{E}_{q_\lambda^k}[\log E_k]\Big) \;=\; \sum_k F[q_\lambda^k] + \sum_k H(q_\lambda^k),
$$

so substituting,

$$
F[q_\lambda] \;=\; \sum_k F[q_\lambda^k] + \sum_k H(q_\lambda^k) + \lambda\big(\gamma\langle K_c\rangle - \langle J\rangle\big) + \log Z_E(\lambda) - H(q_\lambda).
$$

Finally, using the multi-information identity $\sum_k H(q_\lambda^k) - H(q_\lambda) = I(q_\lambda)$:

$$
\boxed{\;F[q_\lambda] \;=\; \sum_k F[q_\lambda^k] \;+\; \lambda\big(\gamma\langle K_c\rangle - \langle J\rangle\big) \;+\; \log Z_E(\lambda) \;+\; I(q_\lambda).\;}
$$

This is the full identity.

## Sign convention

The body section sometimes writes the decomposition in a compact form where
$\log Z_E(\lambda)$ is absorbed into the definition of the per-stream
free energies (so the cross term carries the un-normalised entangled
prior).  The $-I(q_\lambda)$ form quoted in the body therefore
corresponds to the simplified bookkeeping with the un-normalised
entangled prior; the full bookkeeping above is the one to formalise
in Lean.

The cognitive interpretation is unchanged: coupling generates
multi-information $I(q_\lambda)$, the *agentic gain*; and the partition
function $\log Z_E(\lambda)$ represents the *evidence under the coupled
prior*, which absorbs the structural cost.  When $\lambda \to 0$, both
terms vanish and the decomposition reduces to the mean-field
$F = \sum_k F^k$.
