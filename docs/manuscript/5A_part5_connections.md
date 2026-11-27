# Part V — Connections to Existing Frameworks {-}

The parametric-entanglement framework is not a replacement for active
inference or for the neighboring control and probabilistic-programming
literatures.  It is a relationship calculus for one object: the joint
policy posterior.  Some prior constructions are recovered exactly
inside this calculus (mean-field AIF at $\lambda = 0$, single-stream
KL control, product-of-experts, and copula VI after a CDF
change-of-variables).  Others are parametric embeddings that require
an explicit modeling choice, and others are only structural analogies:
they share a coupling skeleton but retain additional process-theoretic
content, such as temporal-scale separation, recursive
observation-conditioning, message-passing schedules, or state-space
Markov-blanket construction.  Three chapters map the territory:

* **[[SECREF:connections]]** — classical active-inference frameworks.
  Mean-field AIF as the $\lambda = 0$ slice (exact). Hierarchical /
  deep AIF as block-bidiagonal coupling (structural analog).
  Sophisticated inference as a tree-structured coupling with the
  recursive observation-conditioning discharged into $J$. Branching-
  time AIF as Bayesian filtering over a tensor-train-compressed
  policy tree, classified as an algorithmic analogy until a direct
  head-to-head construction is implemented.
* **[[SECREF:connections_control_rl]]** — control and RL.  KL /
  path-integral control as the single-stream $K = 1$, $\lambda = 1$
  case (the classical log-partition–value duality). Options
  frameworks as $K = 2$ with policy-matching $J$. Products and
  mixtures of experts as factorizations of $J$. Copula variational
  inference as the CDF-reparametrized continuous analog.
* **[[SECREF:connections_multi_agent_geometry]]** — multi-agent,
  geometry, worldview.  Interactive / multi-agent inference as
  inter-agent coupling potentials. Renormalization-group AIF as a
  structural analogy via tensor-train compression. Policy-space
  Markov-blanket leakage as a coupling identity (distinct from the
  state-space construction). CEREBRUM and case grammar as
  edge-weight asymmetry on the coupling graph.

Each connection is stated with the structural choice that relates it
to the $\lambda$-coupled posterior, the claim class (`exact`,
`parametric`, or `analogical`), and the specific content that remains
outside the present artifact.

---
