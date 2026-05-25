import Lake
open Lake DSL

package «ActinfPolicyEntanglement»

/--
Lean 4 package for *Policy Entanglement in Active Inference* — the
λ-deformation framework that interpolates between strict mean-field
( λ = 0 ) and arbitrary joint policy structure ( λ → ∞ ).

The package is intentionally **Mathlib-free** at the boundary layer so
the core entanglement-decomposition skeleton compiles on a stock
Lean 4 toolchain (pinned to leanprover/lean4:v4.29.0 to match the
`fep_lean` release pin used in sibling template manuscripts).

**Hygiene state:** zero `sorry`, zero `axiom`, zero
`unsafe`/`partial`/`noncomputable`. Algebraic theorems that would
otherwise depend on Mathlib's ring tactics are stated polymorphically
over a small in-house `CommScalar α` typeclass (defined in
`Scalar.lean`); existence-style theorems (Schmidt rank,
heterogeneous-tax bound) are stated as **witness-consuming** boundary
forms that the caller (or a separate MathlibProofs layer) supplies. This
gives a strict improvement over `sorry`-based boundary fragments — the
algebraic content is genuinely proven on `[CommScalar α]` and on the
shipped `Int` instance, and the witness form makes the external
analytic payload explicit at the type signature.

Submodules:

* `ActinfPolicyEntanglement.Basic`        — verdicts, policy factor types,
                                            shared inductives, stream-mode
                                            classification trichotomy.
* `ActinfPolicyEntanglement.Scalar`       — abstract `CommScalar α`
                                            typeclass with derived
                                            algebraic lemmas
                                            (`affine_diff`,
                                            `affine_at_zero`, `mul_sub`,
                                            `sub_self`); ships an
                                            `Int` instance.
* `ActinfPolicyEntanglement.JointDist`    — joint and mean-field
                                            distributions, marginals,
                                            product embedding.
* `ActinfPolicyEntanglement.Coupling`     — coupling potentials J, K_c
                                            and the λ-entangled prior;
                                            polymorphic over the
                                            `CommScalar` scalar type.
* `ActinfPolicyEntanglement.FreeEnergy`   — variational and marginal
                                            free energies, total
                                            correlation, KL divergence.
* `ActinfPolicyEntanglement.Geometry`     — e/m-flatness, m-projection,
                                            Pythagorean witness form.
* `ActinfPolicyEntanglement.Spectral`     — bipartite mean-field
                                            factorization
                                            (Proposition 7.1 forward +
                                            converse).
* `ActinfPolicyEntanglement.Heterogeneous`— O(λ²) coupling-tax envelope
                                            (`BoundedQuadraticTax` /
                                            `SmallLambdaTolerance`
                                            witness structures);
                                            Theorem 9.1, Corollary 9.2.
* `ActinfPolicyEntanglement.BernoulliToy` — closed-form K=2 Bernoulli /
                                            Ising MI, free-energy curve.
* `ActinfPolicyEntanglement.Decomposition`— **Theorem 5.1** (`thm_4_1`) witness-form
                                            decomposition threading
                                            `(J, K_c, γ, λ)` through
                                            `couplingExpectationSkeleton`.
* `ActinfPolicyEntanglement.Monotonicity` — constructive Nat / Or /
                                            List / Fin lemmas.
* `ActinfPolicyEntanglement.Constructive` — `CommScalar`-polymorphic
                                            boundary lemmas
                                            (λ = 0 collapse,
                                            trivial-coupling vanishing).
* `FepSketches.PolicyEntanglementBoundary`— `fep_lean`-compatible re-export hook.
-/
@[default_target]
lean_lib «ActinfPolicyEntanglement» where
  -- The main library plus the FepSketches re-export following the
  -- fep_lean convention so downstream agents can import either path.
  globs := #[
    .andSubmodules `ActinfPolicyEntanglement,
    .andSubmodules `FepSketches
  ]
