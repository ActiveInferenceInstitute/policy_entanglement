# AGENTS.md — `FepSketches`

## Identity & Scope (Phase 7)

This module has been updated to Phase 7: full Mathlib integration. All previously stubbed theorems have been proven using Mathlib's library.

### Key Changes

- `Float` replaced with `Real` for analytic content
- All `sorry` markers removed and replaced with formal proofs
- Re-exports now include Mathlib-proven results

### Validation

```bash
cd lean && lake build
```

No `sorry` placeholders remain.