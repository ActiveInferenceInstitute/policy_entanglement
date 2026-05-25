"""Manuscript validation — report model."""

from __future__ import annotations

from dataclasses import dataclass, field

VARIABLE_PROVENANCE_CLASSES = (
    "hyperparameter-derived",
    "source-scan-derived",
    "registry-derived",
    "analytic-computation",
    "sidecar-derived",
    "uncategorized",
)


_HYPERPARAMETER_LIST_KEYS = frozenset(
    {
        "bernoulli_verification_lambdas",
        "bernoulli_verification_lambdas_count",
        "coupling_ablation_variants_list",
        "ising_alignment_sentinel_lambdas",
        "ising_mi_saturation_lambda",
        "ising_mi_sentinel_lambdas",
        "ising_mi_sentinel_lambdas_count",
        "long_horizon_diagnostic_thresholds_list",
        "long_horizon_replicate_seeds_list",
        "motor_attention_sentinel_lambdas",
        "multi_k_values_list",
        "optimal_lambda_sentinel_deltas",
        "pymdp_total_correlation_sentinel_lambdas",
        "pymdp_total_correlation_sentinel_lambdas_count",
        "robustness_interaction_families_list",
        "spectral_sentinel_lambdas",
        "tt_rank_stream_counts",
    }
)


@dataclass
class ManuscriptValidationReport:
    section_files: list[str]
    undefined_tokens: dict[str, list[tuple[str, str]]] = field(default_factory=dict)
    broken_links: dict[str, list[str]] = field(default_factory=dict)
    missing_figure_files: dict[str, list[str]] = field(default_factory=dict)
    out_of_range_variables: dict[str, str] = field(default_factory=dict)
    missing_headings: list[str] = field(default_factory=list)
    empty_captions: list[str] = field(default_factory=list)
    bad_section_refs: dict[str, list[str]] = field(default_factory=dict)
    hardcoded_refs: dict[str, list[str]] = field(default_factory=dict)
    hardcoded_numeric_literals: dict[str, list[str]] = field(default_factory=dict)
    hardcoded_rendered_source_fields: dict[str, list[str]] = field(default_factory=dict)
    tokens_in_code_fences: dict[str, list[str]] = field(default_factory=dict)
    # Four-track wiring: theorems whose registered ``lean_module`` /
    # ``lean_name`` does not actually resolve to a declaration in the
    # boundary fragment.  Empty when wiring is coherent.
    broken_lean_wiring: dict[str, str] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return not (
            self.undefined_tokens
            or self.broken_links
            or self.missing_figure_files
            or self.out_of_range_variables
            or self.missing_headings
            or self.empty_captions
            or self.bad_section_refs
            or self.hardcoded_refs
            or self.hardcoded_numeric_literals
            or self.hardcoded_rendered_source_fields
            or self.tokens_in_code_fences
            or self.broken_lean_wiring
        )
