# Module: `MarkovBlanket`

Boundary witness-form definition and theorem for the Markov-blanket
separation diagnostic `sep(q) = 1 − I(q) / H(q)` on a finite
support.  Manuscript anchor:
[`../manuscript/5D_connections_multi_agent.md`](../../manuscript/5D_connections_multi_agent.md)
§19.3 (`connections.markov` — Proposition 19.3, *Markov-blanket
separation as `1 − I/H`*).

## Overview

`MarkovBlanket` packages **Proposition 19.3** (`prop_11_3`) as a
current `witness` status theorem with a **Mathlib-free,
witness-consuming boundary theorem**.  The diagnostic

$$
\operatorname{sep}(q) \;=\; 1 \;-\; \frac{I(q)}{H(q)}
$$

quantifies how *separated* the internal and external states of a
multi-stream policy posterior `q` are: when `q` is mean-field,
`I(q) = 0` and `sep(q) = 1` (perfect separation, full Markov blanket);
as `λ` increases and the joint becomes more entangled, `I(q)` grows
and `sep(q)` shrinks toward `0` (the blanket leaks).

The caller supplies `Hq = shannonEntropy q s`, the per-stream entropy
sum `sumStreamEntropies = Σ_k H(q^k)`, `Iq = totalCorrelation q s
sumStreamEntropies`, the separation value `sep`, the positivity
condition `Hq > 0`, and the algebraic identity `sep = 1 − Iq / Hq` on
a finite support `s`.  The boundary fragment certifies the identity in
one line by extracting the witness fields.  Three **tie-in**
identities (`Hq_eq`, `Iq_eq`, and `Iq_nonneg`) ensure that the
witness's `Hq` equals `shannonEntropy q s`, that `Iq` equals
`totalCorrelation q s sumStreamEntropies`, and that `Iq ≥ 0` (the
analytic content discharged by the separate MathlibProofs layer via
KL-non-negativity) — not floating witness parameters but the real
quantities.

The module is `Mathlib`-free, `sorry`-free, and `axiom`-free.  It
follows the *witness-structure idiom* introduced in
[`Heterogeneous.lean`](../../lean/ActinfPolicyEntanglement/Heterogeneous.lean).

## Definitions provided

| Lean name | Kind | Purpose |
|---|---|---|
| `MarkovBlanketSeparationWitness` | `structure` | Carries `(Hq, sumStreamEntropies, Iq, sep)`, the strict-positivity `Hq_pos : Hq > 0`, three **tie-in** identities `Hq_eq : Hq = shannonEntropy q s`, `Iq_eq : Iq = totalCorrelation q s sumStreamEntropies`, and `Iq_nonneg : 0.0 ≤ Iq` (analytic discharge from KL ≥ 0), plus the algebraic identity `sep_eq : sep = 1 − Iq / Hq`.  Nine fields (`Hq, sumStreamEntropies, Iq, sep, Hq_pos, Hq_eq, Iq_eq, Iq_nonneg, sep_eq`). |
| `markovBlanket_separation_identity_witness` | `theorem` | Boundary witness form of Proposition 19.3. |

## Key theorem

### `markovBlanket_separation_identity_witness` (Proposition 19.3 — `prop_11_3`)

```lean
theorem markovBlanket_separation_identity_witness {K Pol}
    (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (witness : MarkovBlanketSeparationWitness q s) :
    0.0 < witness.Hq
      ∧ witness.Hq = shannonEntropy q s
      ∧ witness.Iq = totalCorrelation q s witness.sumStreamEntropies
      ∧ 0.0 ≤ witness.Iq
      ∧ witness.sep = 1.0 - witness.Iq / witness.Hq :=
  ⟨witness.Hq_pos, witness.Hq_eq, witness.Iq_eq,
   witness.Iq_nonneg, witness.sep_eq⟩
```

The conjunction packages the five load-bearing facts of the
Markov-blanket separation identity: well-definedness (`Hq > 0`),
the boundary-fragment tie-in for `Hq`, the tie-in for `Iq` to
`totalCorrelation q s witness.sumStreamEntropies`, the non-negativity
`0.0 ≤ Iq` (analytic discharge from KL ≥ 0), and the algebraic
identity itself.  The proof is a single anonymous constructor —
exactly the witness-form pattern.

## Note on the `η(q) = I(q)/H(q)` overload

The ratio `I(q)/H(q)` appearing inside the separation identity is the
*Markov-blanket leakage coefficient* in `S06`'s manuscript-side
notation: a *function-valued* diagnostic on the joint `q`, taking
values in `[0, 1]`.  This is **distinct** from the `η` notation used
in §7 (`information_geometry.md`), where `η = E_q[·]` denotes the
**m-coordinate** of the dually-flat manifold.  Both notations are
established in their respective communities; the manuscript carefully
disambiguates them, and the Lean module identifiers (`Iq`, `Hq`, `sep`)
are deliberately chosen to avoid collision with the m-coordinate
notation.  When reading [`S06_notation_and_concordance.md`](../../manuscript/S06_notation_and_concordance.md),
the policy-blanket leakage row corresponds to `Iq / Hq` here, not to
the §7 `η` coordinate.

## Wiring

| Track | Resolves to |
|---|---|
| Manuscript section | [`§19.3 Markov blankets and Bayesian mechanics`](../../manuscript/5D_connections_multi_agent.md) (`connections.markov`). |
| Lean module | [`MarkovBlanket.lean`](../../lean/ActinfPolicyEntanglement/MarkovBlanket.lean) (1 structure, 1 theorem, zero `sorry`, zero `axiom`). |
| Registry label | `prop_11_3` in [`manuscript/refs/labels.yaml`](../../manuscript/refs/labels.yaml); current `status: witness`. |
| Python sanity rail | [`src/lean/free_energy`](../../src/lean/free_energy.py) (`shannon_entropy`, `total_correlation`) — the separation ratio `1 − I/H` is computed directly from these primitives. |
| Tests | [`tests/test_free_energy.py`](../../tests/test_free_energy.py) — exercises `shannon_entropy` / `total_correlation` against analytic ground truths; the separation ratio is a one-line composition. |

## Examples / use-cases (witness construction)

A Mathlib-side caller that wishes to certify Proposition 19.3 on a
specific joint `q` with support `s` constructs the witness by computing
the two primitives directly:

```lean
def mySeparationWitness (q : JointDist K Pol) (s : List (PolicySpace K Pol))
    (sumHs : Float)
    (hH : 0.0 < shannonEntropy q s)
    (hI : 0.0 ≤ totalCorrelation q s sumHs) :
    MarkovBlanketSeparationWitness q s where
  Hq                 := shannonEntropy q s
  sumStreamEntropies := sumHs
  Iq                 := totalCorrelation q s sumHs
  sep                := 1.0 - totalCorrelation q s sumHs / shannonEntropy q s
  Hq_pos             := hH
  Hq_eq              := rfl
  Iq_eq              := rfl
  Iq_nonneg          := hI
  sep_eq             := rfl
```

and then invokes

```lean
example : ... := markovBlanket_separation_identity_witness
                   q s (mySeparationWitness q s sumHs hH hI)
```

to discharge the separation identity claim.  Numerically, the
separation ratio is a one-line composition in the Python mirror:

```python
from lean.free_energy import shannon_entropy, total_correlation

def markov_separation(q):
    H = shannon_entropy(q)
    I = total_correlation(q)
    return 1.0 - I / H
```

For a mean-field `q`, `total_correlation(q) ≈ 0` and the separation
saturates near `1.0`; for a correlated joint, `total_correlation(q) > 0`
and the separation falls below `1.0`.

## Cross-references

* [`free_energy.md`](free_energy.md) — `shannonEntropy` and
  `totalCorrelation` are the boundary-fragment primitives that the
  witness ties in to.
* [`information_geometry.md`](information_geometry.md) — §7 uses `η` to
  denote the m-coordinate, **distinct** from the `Iq/Hq` ratio here;
  Proposition 7.3 (`totalCorrelation_eq_kl_to_mprojection`) gives the
  KL reading of `I(q)` that this module composes with `H(q)` to form
  the separation diagnostic.
* [`joint_dist.md`](joint_dist.md) — `JointDist` / `PolicySpace` are
  the carrier types over which the witness is stated.
* [`convexity.md`](convexity.md) — additional witness-form theorems
  (Theorem 5.6 and Proposition 11.1) graduated in the same round.
* [`heterogeneous_ensembles.md`](heterogeneous_ensembles.md) — the
  witness-structure idiom (`BoundedQuadraticTax`,
  `SmallLambdaTolerance`) reused here as
  `MarkovBlanketSeparationWitness`.
* Manuscript [`§5D Connections to multi-agent geometry`](../../manuscript/5D_connections_multi_agent.md)
  and the policy-blanket leakage row of
  [`S06 Notation and concordance`](../../manuscript/S06_notation_and_concordance.md)
  — the prose context for this diagnostic.
