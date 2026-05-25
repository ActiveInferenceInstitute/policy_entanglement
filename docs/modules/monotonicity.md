# Monotonicity — constructive Nat / List / Fin lemmas

Manuscript section:
no direct manuscript counterpart — `Monotonicity` is a
*constructive* helper module that supports boundary statements in
[`Coupling`](coupling.md), [`FreeEnergy`](decomposition_theorem.md),
[`Geometry`](information_geometry.md), and
[`Heterogeneous`](heterogeneous_ensembles.md).

Lean source:
[`Monotonicity.lean`](../../lean/ActinfPolicyEntanglement/Monotonicity.lean).

## Role in the boundary fragment

`Monotonicity` collects every elementary order / fold lemma that
the substantive submodules need but cannot pull from Mathlib.  The
goal is to keep the dependency graph *Mathlib-free*: anything as
basic as `nat_le_trans` or `list_length_append` lives here so the
substantive modules can `import ActinfPolicyEntanglement.Monotonicity`
and proceed without `import Mathlib`.

Every lemma is fully proven — zero `sorry`, zero `axiom`, zero
`unsafe`/`partial`/`noncomputable`.  Most reduce to one-line
applications of stock-Lean theorems on `Nat` and `List`.

## Lemma inventory

### `Nat` order helpers

| Lemma | Signature |
|---|---|
| `nat_le_refl` | `n ≤ n` |
| `nat_le_trans` | `a ≤ b → b ≤ c → a ≤ c` |
| `nat_succ_pos` | `0 < n + 1` |
| `nat_zero_le` | `0 ≤ n` |
| `nat_le_succ` | `n ≤ n + 1` |
| `nat_lt_succ_self` | `n < n + 1` |

### `Or` / `And` decidability

| Lemma | Signature |
|---|---|
| `or_self_iff` | `P ∨ P ↔ P` |
| `or_comm_iff` | `P ∨ Q ↔ Q ∨ P` |
| `and_self_iff` | `P ∧ P ↔ P` |

These are the boundary tools `Heterogeneous` uses to phrase the
planning-vs-reflexive trichotomy without invoking `Classical.em`.

### `List` length and append

| Lemma | Signature |
|---|---|
| `list_length_nonneg` | `0 ≤ l.length` |
| `list_length_cons` | `(x :: l).length = l.length + 1` |
| `list_length_append` | `(l₁ ++ l₂).length = l₁.length + l₂.length` |
| `list_append_nil` | `l ++ [] = l` |
| `list_nil_append` | `[] ++ l = l` |

`list_length_append` is proven by structural induction on `l₁`
(`omega` discharges the arithmetic step); the others follow by
`rfl` or one-line `induction`.

### `Fin` reasoning

| Lemma | Signature |
|---|---|
| `fin_lt_size` | `(k : Fin K).val < K` |
| `fin_zero_lt` | `0 < K → (⟨0, h⟩ : Fin K).val = 0` |

These let downstream modules iterate over a stream index without
re-deriving the bound proof every time.

## Where to look

* Lean: [`Monotonicity.lean`](../../lean/ActinfPolicyEntanglement/Monotonicity.lean) (74 lines).
* Imports: `Basic`.
* Imported by: substantive modules use these via the root
  `ActinfPolicyEntanglement` import; the namespace
  `ActinfPolicyEntanglement.Monotonicity` keeps these helpers from
  cluttering the main namespace.
* No Python mirror — these are stock-Lean structural lemmas with
  no numerical content.
