import Lake
open Lake DSL

package «ActinfPolicyEntanglement»

/--
Lean 4 package for *Policy Entanglement in Active Inference* — the
λ-deformation framework that interpolates between strict mean-field
( λ = 0 ) and arbitrary joint policy structure ( λ → ∞ ).

The package is intentionally **Mathlib-free** at the boundary layer so the
core entanglement-decomposition skeleton compiles on a stock Lean 4
toolchain (pinned to leanprover/lean4:v4.29.0 to match the FEP_Lean
release environment used elsewhere in this monorepo). Theorems requiring
KL divergence, Shannon entropy, or matrix SVD are expressed as
Mathlib-ready statements with `sorry` placeholders so the dependency can
be added incrementally without disturbing the boundary fragment.

Submodules:

* `ActinfPolicyEntanglement.Basic`        — verdicts, policy factor types,
                                            shared inductives.
* `ActinfPolicyEntanglement.JointDist`    — joint and mean-field
                                            distributions, marginals,
                                            product embedding.
* `ActinfPolicyEntanglement.Coupling`     — coupling potentials J, K_c
                                            and the λ-entangled prior.
* `ActinfPolicyEntanglement.FreeEnergy`   — variational and marginal
                                            free energies, total
                                            correlation, expectations.
* `ActinfPolicyEntanglement.Geometry`     — e/m-flatness, m-projection
                                            via marginalization,
                                            Pythagorean structure.
* `ActinfPolicyEntanglement.Spectral`     — Schmidt rank for K=2,
                                            tensor-network ranks for K>2,
                                            archetypal modes.
* `ActinfPolicyEntanglement.Heterogeneous`— O(λ²) coupling tax bound
                                            for mixed VFE/EFE ensembles
                                            (Theorem 8.1).
* `ActinfPolicyEntanglement.BernoulliToy` — closed-form K=2 Bernoulli /
                                            Ising MI, free-energy curve.
* `ActinfPolicyEntanglement.Decomposition`— **Theorem 4.1** statement
                                            and proof scaffold.
* `FepSketches.PolicyEntanglementBoundary`— FEP_Lean re-export hook.
-/
@[default_target]
lean_lib «ActinfPolicyEntanglement» where
  -- The main library plus the FepSketches re-export following the
  -- fep_lean / trsc convention so downstream agents can import either.
  globs := #[
    .andSubmodules `ActinfPolicyEntanglement,
    .andSubmodules `FepSketches
  ]
