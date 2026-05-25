# JointDist — distributions on the policy space

Manuscript section:
[`../manuscript/2B_setup.md`](../../manuscript/2B_setup.md)
(§3.2 multi-stream extension, §3.3 mean-field baseline).

Lean source:
[`JointDist.lean`](../../lean/ActinfPolicyEntanglement/JointDist.lean).

## Role in the boundary fragment

`JointDist` is the Mathlib-free ground for every distribution-shaped
object in the project.  It encodes joint distributions on the
`PolicySpace`, the mean-field factorization as an existential
predicate, and the explicit recursive product that turns a tuple of
per-stream factors into a joint mass function.

It avoids `Mathlib.Probability.PMF` by using plain `Float`-valued
mass functions and a `List` support, so the boundary fragment
compiles on stock Lean 4 v4.29.0.

## Types

| Identifier | Type | Meaning |
|---|---|---|
| `JointDist K Pol` | `PolicySpace K Pol → Float` (abbrev) | Joint mass function on the policy space |
| `MFDist   K Pol` | `∀ k, Pol k → Float` (abbrev) | Per-stream factor: one mass function per stream |

`Float` is intentional — the boundary fragment only needs ring
identities and *evaluation*, not real-analytic continuity.  The
Mathlib refinement (see
[`MathlibRefinementRoadmap.md`](../../lean/ActinfPolicyEntanglement/MathlibRefinementRoadmap.md))
will swap `Float` for `ℝ` (`Mathlib.Real`) without changing the
public API.

## Predicates

```lean
def IsNonNeg (q : JointDist K Pol) : Prop :=
  ∀ π, 0.0 ≤ q π

def IsPMF    (q : JointDist K Pol) : Prop :=
  ∃ support : List (PolicySpace K Pol),
    support.foldr (fun π acc => acc + q π) 0.0 = 1.0
```

`IsPMF` records the (necessarily finite) support as a `List`, again
to dodge Mathlib's `Finset` machinery.  The Mathlib refinement maps
`support` onto a `Finset` and `foldr` onto `Finset.sum`.

## Mean-field embedding

```lean
def mfProductWeight (m : MFDist K Pol)
    (π : PolicySpace K Pol) : Float
  -- recursively folds m k (π k) over k ∈ [0, K)

def mfToJoint (m : MFDist K Pol) : JointDist K Pol :=
  fun π => mfProductWeight m π

def IsMeanField (q : JointDist K Pol) : Prop :=
  ∃ m : MFDist K Pol, ∀ π, q π = mfToJoint m π
```

`mfProductWeight` is defined by structural recursion on the
finite-`Nat` index, with an explicit `termination_by K - i`
clause; it elaborates to a total function (no `partial`,
no `noncomputable`).

`IsMeanField` is the predicate that the *baseline* policy
posterior in §3.3 satisfies.  The λ-deformation of `Coupling`
takes a mean-field starting point and bends it into a coupled
joint by adding the `λ · J` log-weight contribution.

## Where to look

* Lean: [`JointDist.lean`](../../lean/ActinfPolicyEntanglement/JointDist.lean) (63 lines).
* Imported by: `Coupling`, `FreeEnergy`, `Geometry`, `Spectral`,
  `Heterogeneous`, `Decomposition`, `Constructive`, `BernoulliToy`.
* Python mirror: [`src/lean/joint_dist.py`](../../src/lean/joint_dist.py)
  (`normalize`, `joint_marginals`, `is_pmf`, `is_mean_field` —
  numerical realizations using `numpy` arrays).
* Tests: [`tests/test_joint_dist.py`](../../tests/test_joint_dist.py).
