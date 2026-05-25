# Heterogeneous ensembles and Theorem 9.1

Manuscript section:
[`../manuscript/2H_heterogeneous.md`](../../manuscript/2H_heterogeneous.md).

## The setting

Real agents are *mixed*: some streams use one-step VFE descent
(reflexive controllers); others plan via expected free energy
(EFE / sophisticated inference).  Let

* $\mathcal{V} \subseteq \{1,\ldots,K\}$ index VFE streams,
* $\mathcal{P} = \{1,\ldots,K\}\setminus\mathcal{V}$ index planning
  streams.

A *heterogeneous* ensemble has both classes non-empty.  The question
of interest:

> How reflexive can my low-level controllers be while still benefiting
> from the planning surplus on the coupled streams?

## The coupling tax

Consider holding the VFE streams *pinned* at their λ = 0 marginals
while letting the planning streams adapt to the λ-entangled
posterior.  The resulting joint, $q_{\mathrm{pinned}}$, is suboptimal
relative to the fully-adaptive $q_\lambda$.  Define:

$$
\mathrm{tax}(\lambda) \;=\; D_{\mathrm{KL}}(q_\lambda \,\|\, q_{\mathrm{pinned}}).
$$

* Lean: `couplingTax (taxFunction : Float → Float) (lam : Float)`
  — boundary form parameterized by an abstract `taxFunction`; the
  numerical content lives on the Python side.
* Python: `coupling_tax(mf, G, J, K_c, γ, λ, modes)`.

For purely reflexive (`mode ≡ VFE`) or purely planning ensembles, the
tax is identically 0 (the boundary lemmas in `Constructive.lean`
discharge `taxFunction 0.0 - taxFunction 0.0 = 0.0`-shape equalities
by `rfl`).

## Theorem 9.1 — O(λ²) bound

For any heterogeneous ensemble, there is a structural constant $C \geq 0$
(depending on Fisher information of the marginals at λ = 0) such that

$$
\mathrm{tax}(\lambda) \;\leq\; C \cdot \lambda^2 \cdot \|K_c\|^2.
$$

* Lean: `couplingTax_quadratic_bound` (boundary; the genuine proof
  uses Bregman / KL Taylor expansion around λ = 0).
* Python: `coupling_tax_within_quadratic_bound(...)` empirically
  verifies the bound for a chosen safety factor.

## Corollary 9.2 — reflexive-stream tolerance

For any tolerance $\varepsilon > 0$, there is a maximum
$\lambda_{\max}$ such that

$$
\lambda \in [0, \lambda_{\max}] \;\Rightarrow\; \mathrm{tax}(\lambda) \leq \varepsilon.
$$

This formalizes "how reflexive can my controllers be while riding
along with planners": they are safe to keep pinned as long as the
coupling stays below the threshold determined by their marginal
curvatures.

## Mathlib refinement plan

The full proof uses:

1. Mathlib's `Real.log` and `Probability.Entropy.Basic` to lift the
   `Float` boundary forms.
2. Taylor expansion of KL around the m-projection at λ = 0.
3. Cauchy–Schwarz on the inner product
   $\langle K_c, q_0 - q_\lambda \rangle$.

As the witness payload is discharged in MathlibProofs, the Lean theorem
is expected to close through these three steps.  See
[`../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md)
for the full payload-discharge roadmap.

## Numerical example

The figure
[`../output/figures/coupling_tax_quadratic.png`](../../output/figures/coupling_tax_quadratic.png)
shows the actual coupling tax for a K = 2 heterogeneous ensemble
(`[VFE, EFE]`) with the Ising habit and a small symmetric
`K_c`.  The quadratic envelope (dashed) is fitted from the small-λ
slope and bounds the actual tax across the entire λ range tested.

## Where to look

* Lean: [`Heterogeneous.lean`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean).
* Python: [`heterogeneous.py`](../../src/lean/heterogeneous.py).
* Tests: [`test_heterogeneous.py`](../../tests/test_heterogeneous.py).
* Figure: [`../output/figures/coupling_tax_quadratic.png`](../../output/figures/coupling_tax_quadratic.png).

**Pattern reuse note:** The witness-structure idiom introduced in this
module (`BoundedQuadraticTax`, `SmallLambdaTolerance`) is reused in
[`docs/modules/convexity.md`](convexity.md)
(`FreeEnergyConvexityWitness`, `LocalConcavityAtZero`) and
[`docs/modules/markov_blanket.md`](markov_blanket.md)
(`MarkovBlanketSeparationWitness`) for additional witness theorems
graduated in round 2.
