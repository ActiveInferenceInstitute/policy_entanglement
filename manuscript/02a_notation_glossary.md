# Notation Glossary {-}

This section consolidates every symbol used in the manuscript.  Symbols
introduced informally elsewhere are made precise here; the same Lean /
Python identifiers appear in [`docs/reference/math_reference.md`](../docs/reference/math_reference.md).

## Sets, indices, and basic objects

| Symbol | Meaning |
|---|---|
| $K \in \mathbb{N}$ | Number of policy streams in the ensemble |
| $k \in \{1,\ldots,K\}$ | Stream index |
| $\Pi^k$ | Per-stream policy factor (finite type) |
| $\Pi = \prod_k \Pi^k$ | Joint policy space |
| $\pi = (\pi^1,\ldots,\pi^K) \in \Pi$ | Joint policy |
| $\pi^k \in \Pi^k$ | Per-stream policy |
| $\pi^{-k}$ | The tuple of all policies *other* than stream $k$ |
| $\mathcal{V} \subseteq \{1,\ldots,K\}$ | VFE (reflexive) stream indices |
| $\mathcal{P} = \{1,\ldots,K\}\setminus\mathcal{V}$ | EFE / planning stream indices |

## Distributions

| Symbol | Meaning |
|---|---|
| $E_k(\pi^k)$ | Per-stream policy prior (habit), a probability mass function on $\Pi^k$ |
| $E_{\mathrm{MF}}(\pi) = \prod_k E_k(\pi^k)$ | Mean-field prior |
| $E_\lambda(\pi)$ | $\lambda$-entangled prior (manuscript [[SECREF:lambda_deformation.entangled_posterior]]) |
| $G_k(\pi^k)$ | Per-stream expected free energy (EFE) |
| $G_{\mathrm{MF}}(\pi) = \sum_k G_k(\pi^k)$ | Mean-field EFE |
| $q(\pi)$ | Joint policy posterior |
| $q^k(\pi^k) = \sum_{\pi^{-k}} q(\pi)$ | Per-stream marginal of $q$ |
| $q_\lambda(\pi)$ | $\lambda$-entangled posterior |
| $q_{\mathrm{MF}}(\pi) = \prod_k q^k(\pi^k)$ | Product of marginals (m-projection of $q$) |

## Coupling potentials and parameters

| Symbol | Meaning |
|---|---|
| $J(\pi)$ | *Habit* coupling potential — prior side |
| $K_c(\pi)$ | *Preference* coupling potential — EFE side |
| $\lambda \in [0,\infty)$ | Coupling parameter |
| $\gamma > 0$ | Policy precision (inverse-temperature on EFE) |
| $\Delta \in [-\Delta_{\max}, \Delta_{\max}]$ | Utility surplus for aligned outcomes (Bernoulli toy, [[SECREF:examples.bernoulli]]) |
| $\Delta_{\max} = 1$ | Saturation point of the utility surplus (Bernoulli toy) |
| $\lambda^*(\Delta)$ | Optimal coupling for a given utility surplus |
| $\lambda_c^{(1)},\,\lambda_c^{(2)}$ | Critical couplings at the disordered–mixed and mixed–frozen phase boundaries ([[SECREF:phase]]) |

## Information-theoretic quantities

| Symbol | Definition |
|---|---|
| $H(p) = -\sum p\log p$ | Shannon entropy (natural log throughout) |
| $H_b(p) = -p\log p - (1-p)\log(1-p)$ | Binary entropy |
| $D_{\mathrm{KL}}(q\,\|\,p) = \sum q\log(q/p)$ | Kullback–Leibler divergence |
| $I(q) = \sum_k H(q^k) - H(q)$ | Total correlation (multi-information) |
| $\mathrm{Var}_q[X]$ | Variance under $q$ |
| $\sigma(x) = 1/(1+e^{-x})$ | Logistic sigmoid |

## Free energies

| Symbol | Definition |
|---|---|
| $F[q]$ | Variational free energy of $q$ against the relevant prior and EFE |
| $F[q^k]$ | Per-stream marginal free energy |
| $\psi(\lambda) = \log Z(\lambda)$ | Log-partition function of the $\lambda$-entangled family |

## Manifolds and projections

| Symbol | Meaning |
|---|---|
| $\mathcal{M}$ | Manifold of strictly-positive joint distributions on $\Pi$ |
| $\mathcal{M}_{\mathrm{MF}} \subset \mathcal{M}$ | Mean-field submanifold (product distributions) |
| $\Pi_{\mathrm{MF}}(q) = \prod_k q^k$ | m-projection of $q$ onto $\mathcal{M}_{\mathrm{MF}}$ |
| $\theta = \log q$ | e-coordinates (natural parameters) |
| $\eta = \mathbb{E}_q[\cdot]$ | m-coordinates (expectation parameters) |

## Spectral / tensor-network

| Symbol | Meaning |
|---|---|
| $r$ | Schmidt rank of a bipartite (K=2) joint policy posterior |
| $s_\alpha$ | $\alpha$-th singular value of the bipartite joint matrix |
| $u_\alpha,\,v_\alpha$ | Left / right singular vectors (archetype marginals) |
| $S_E(q)$ | Policy entanglement entropy of a bipartite cut |
| $r_k$ | Tensor-train bond dimension across the $k$-th cut |

## Heterogeneous-ensemble quantities

| Symbol | Meaning |
|---|---|
| $\mathrm{mode}_k \in \{\mathrm{VFE}, \mathrm{EFE}, \mathrm{Sophisticated}\}$ | Inference mode of stream $k$ |
| $\mathrm{tax}(\lambda)$ | Coupling tax (KL between fully-adaptive and pinned posteriors) |
| $\|K_c\|^2 = \sum_\pi K_c(\pi)^2$ | Squared $\ell^2$-norm of the preference potential |
| $C \geq 0$ | Structural curvature constant in [[THMREF:thm_8_1]] |

## Verdicts and inductive types

The Lean boundary fragment names three discrete classifiers used in
the body:

| Inductive | Constructors | Manuscript role |
|---|---|---|
| `InferenceMode` | `vfe`, `efe`, `sophisticated` | Stream-mode label ([[SECREF:setup.multistream]], [[SECREF:heterogeneous]]) |
| `CouplingPhase` | `disordered`, `mixed`, `frozen` | Cognitive phase ([[SECREF:phase]]) |
| `CouplingRole` | `habit` (J), `preference` (K_c) | Side of the coupling potential |
| `CouplingVerdict` | `pays`, `neutral`, `does_not_pay` | Coupling-pays-for-itself outcome ([[SECREF:comparative]]) |

## Conventions

* **Natural log** is used throughout; numeric values therefore have
  units of *nats*.  Where binary log is needed it is written $\log_2$.
* **Joint vs marginal**: distributions on $\Pi$ are *joints*; per-stream
  distributions on $\Pi^k$ are *marginals*.
* **Vector / tensor**: bold $\mathbf{x}$ when shape matters, plain $x$
  otherwise.
* **Equations vs definitions**: an equation set off as
  $X \equiv Y$ is a definition; $X = Y$ is a derivable identity.
* **Probability conventions**: every distribution is normalised to
  $1$ unless explicitly *unnormalised*; KL is always
  $D_{\mathrm{KL}}(q \,\|\, p)$ (not the reverse).
* **Information geometry**: dually-flat structure on the simplex
  follows the standard development [@amari-nagaoka-2000; @amari-2016;
  @nielsen-2020]; non-extensive / $\phi$-deformed analogues use the
  framework of [@naudts-2011].
* **Active-inference background**: the single-stream POMDP recap
  follows [@friston-2010; @dacosta-2020; @smith-2022], with EFE
  conventions per [@friston-2017].

---
