# Part II — Theory {-}

The mathematical core of the manuscript.  Each chapter introduces the
objects, states the load-bearing theorems about them, and immediately
gives the proof or proof sketch (full proofs in the supplements).
The chain proceeds:

1. **[[SECREF:setup]]** — discrete-time POMDP active inference and
   the mean-field baseline against which everything is measured.
2. **[[SECREF:lambda_deformation]]** — the parametric coupling
   construction: $J$ (habit) and $K_c$ (preference) potentials, and
   the $\lambda$-entangled posterior they define.
3. **[[SECREF:decomposition]]** — the load-bearing identity
   ([[THMREF:thm_4_1]]) splitting free energy into marginals,
   coupling, and a non-negative multi-information term.
4. **[[SECREF:examples]]** — three worked cases (Bernoulli closed
   form, motor-attention, multi-timescale) that make the abstract
   machinery concrete.
5. **[[SECREF:geometry]]** — dual e/m information geometry; the
   $\lambda$-family is an e-geodesic ([[THMREF:thm_6_4]]); Pythagorean
   decomposition ([[THMREF:prop_6_5]]).
6. **[[SECREF:spectral]]** — Schmidt rank ([[THMREF:prop_7_1]]),
   archetypal eigenvectors, tensor-train bond dimensions
   ([[THMREF:thm_7_3]]).
7. **[[SECREF:heterogeneous]]** — VFE/EFE mixed ensembles and the
   $O(\lambda^2)$ coupling-tax bound ([[THMREF:thm_8_1]]).
8. **[[SECREF:phase]]** — disordered / mixed / frozen coupling
   regimes and their behavioral signatures.
9. **[[SECREF:comparative]]** — sensitivity, two-parameter
   generalization, potential-structure dependence.

Every theorem in this part carries a Lean companion (see the per-row
status in [`docs/reference/veridical_status.md`](../docs/reference/veridical_status.md))
and a Python numerical witness (see [`docs/reference/_theorem_map.md`](../docs/reference/_theorem_map.md)).
The supplements ([[SECREF:app.proof_decomp]],
[[SECREF:app.convexity]], [[SECREF:app.bernoulli]],
[[SECREF:app.tt_inference]]) carry the full derivations.

---
