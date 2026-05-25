"""H1 signposting durability gate (RedTeam 2026-05-18 F6 / AR-3).

The 0A/1A/3A abstract/intro headlines inline the registry status split
via generated `[[VAR:theorem_status_*_count]]` tokens. Prior to this
test the *correctness* of "all numbered theorems carry a live Lean
companion — N proved / M witness / ..." rode on an UNGUARDED arithmetic
coincidence: token-resolution tests only checked the keys *exist*, not
that the four headlined buckets actually partition every registry
theorem with none `deferred`/`sketch`. A future theorem added with
`status: sketch` (a counted-but-not-headlined bucket) would make the
abstract silently false-by-omission while every token still resolved.

This test enforces the invariant the headline depends on, keyed off the
generated `manuscript_variables.json` (same registry source the prose
tokens render from), so the H1 fix is durable, not cosmetic.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
VAR_JSON = PROJECT / "output" / "data" / "manuscript_variables.json"
LABELS_YAML = PROJECT / "manuscript" / "refs" / "labels.yaml"
MANUSCRIPT_DIR = PROJECT / "manuscript"

_VALID_FAITHFULNESS = {"substantive", "definitional", "statement-restricted"}
# Full vocab incl. the witness/boundary/forwarder tier (RedTeam Cat-3b).
_VALID_FAITHFULNESS_ALL = _VALID_FAITHFULNESS | {
    "typed-witness",
    "forwarder",
    "numerical_corroboration_only",
}

_HEADLINED = (
    "theorem_status_proved_count",
    "theorem_status_witness_count",
    "theorem_status_boundary_count",
    "theorem_status_forwarder_count",
)
_NON_HEADLINED = (
    "theorem_status_deferred_count",
    "theorem_status_sketch_count",
    "theorem_status_roadmap_count",
)


def _vars() -> dict[str, int]:
    assert VAR_JSON.exists(), (
        f"{VAR_JSON} missing — conftest bootstrap must regenerate it before "
        "this gate can run (do not let an absent file silently pass)."
    )
    return json.loads(VAR_JSON.read_text(encoding="utf-8"))


def test_headline_buckets_partition_the_registry() -> None:
    """proved+witness+boundary+forwarder (+deferred+sketch+roadmap) == every
    registry theorem. If a theorem exists outside the seven status buckets
    the headline's "all theorems" claim is false-by-omission."""
    v = _vars()
    total = int(v["theorem_registry_count"])
    counted = sum(int(v[k]) for k in _HEADLINED + _NON_HEADLINED)
    assert counted == total, (
        f"registry has {total} theorems but the 7 status buckets sum to "
        f"{counted}: {{**{ {k: v.get(k) for k in _HEADLINED + _NON_HEADLINED} } }}. "
        "The 0A/1A/3A 'all theorems carry a live Lean companion (split …)' "
        "headline is no longer arithmetically true — re-derive the split."
    )


def test_no_deferred_or_sketch_theorems_behind_the_headline() -> None:
    """The headlines assert 'none remain deferred' and only show the four
    proved/witness/boundary/forwarder buckets. If deferred/sketch becomes
    nonzero the headline is misleading even though every VAR still
    resolves."""
    v = _vars()
    deferred = int(v["theorem_status_deferred_count"])
    sketch = int(v["theorem_status_sketch_count"])
    assert deferred == 0 and sketch == 0, (
        f"deferred={deferred}, sketch={sketch} (expected 0/0). A "
        "non-headlined-bucket theorem exists; the abstract's "
        "'all theorems carry a live Lean companion / none remain deferred' "
        "claim is now misleading — update the headline disclosure."
    )


def _theorems() -> dict:
    data = yaml.safe_load(LABELS_YAML.read_text(encoding="utf-8")) or {}
    return data.get("theorems") or {}


def test_every_proved_row_declares_statement_faithfulness() -> None:
    """`status: proved` only means machine-checked in stock Lean — it does
    NOT assert the Lean statement IS the named manuscript proposition.
    Three rows (prop_6_1, prop_6_2, prop_7_1) prove a strictly weaker
    statement than their name; only cor_4_2/cor_4_3 are substantive. Every
    proved row must carry an explicit `faithfulness:` so the headline cannot
    silently over-claim. A future proved row that omits it fails HERE, not
    in the reader's head."""
    offenders = {
        lab: row.get("faithfulness")
        for lab, row in _theorems().items()
        if isinstance(row, dict)
        and str(row.get("status", "")) == "proved"
        and str(row.get("faithfulness", "")) not in _VALID_FAITHFULNESS
    }
    assert not offenders, (
        f"status: proved rows with missing/invalid faithfulness: {offenders}. "
        f"Each must be one of {sorted(_VALID_FAITHFULNESS)} "
        "(see docs/reference/veridical_status.md §1)."
    )


def test_every_registry_row_declares_faithfulness() -> None:
    """RedTeam 2026-05-19 Cat-3b structural close. The *absence* of a
    `faithfulness:` field on the witness/boundary/forwarder tier WAS the
    laundering — "witness" read stronger than the hypothesis-reexport
    Lean body delivers, with no machine-checked qualifier, while the
    proved tier carried one. Now EVERY registry row must declare a valid
    faithfulness (`typed-witness` for witness/boundary = analytic content
    is an assumed structure/hypothesis, not proved; `forwarder`;
    `substantive`/`definitional`/`statement-restricted` for proved). A
    future row that omits it fails HERE — the absence cannot recur."""
    offenders = {
        lab: row.get("faithfulness", "<MISSING>")
        for lab, row in _theorems().items()
        if isinstance(row, dict) and str(row.get("faithfulness", "")) not in _VALID_FAITHFULNESS_ALL
    }
    assert not offenders, (
        f"registry rows with missing/invalid faithfulness: {offenders}. "
        f"Every row must declare one of {sorted(_VALID_FAITHFULNESS_ALL)}. "
        "The absence on the witness tier was the Cat-3b over-claim — see "
        "docs/reference/methods_and_assumptions.md."
    )


def test_proved_faithfulness_split_partitions_the_proved_bucket() -> None:
    """substantive + definitional + statement-restricted == proved count.
    If this fails the abstract/Part III faithful decomposition is
    arithmetically false even though every token still resolves."""
    v = _vars()
    proved = int(v["theorem_status_proved_count"])
    parts = (
        int(v["theorem_proved_substantive_count"])
        + int(v["theorem_proved_definitional_count"])
        + int(v["theorem_proved_restricted_count"])
    )
    assert parts == proved, (
        f"proved={proved} but substantive+definitional+statement-restricted"
        f"={parts}. The headline's faithful split no longer partitions the "
        "proved bucket — re-derive it."
    )


# Ground truth, pinned to the primary Lean source (RedTeam 2026-05-18).
# A future agent flipping any of these to `substantive` re-inflates the
# headline while every arithmetic/partition test stays green — that is
# the recurrence-#7 path. This test anchors the split's *truth*, not its
# shape. Each citation is the actual Lean body proving a weaker statement
# than the row's manuscript name.
_PINNED_FAITHFULNESS = {
    # substantive: genuine machine-checked proof of the named proposition
    "cor_4_2": "substantive",  # couplingVerdict_correct: decide_eq_true_iff
    "cor_4_3": "substantive",  # couplingLogWeight_pointwise_at_zero → affine_at_zero
    # statement-restricted: Lean statement strictly weaker than the name
    "prop_6_1": "statement-restricted",  # mfImage_isMeanField: rfl IsMeanField, NOT e-flatness
    "prop_6_2": "statement-restricted",  # mProjection_kl_eq_self_when_meanfield: eq only if q=m̂q, NOT minimality
    "prop_7_1": "statement-restricted",  # isBipartiteMeanField_factors: Iff.rfl, NOT Schmidt-rank equiv
}


def test_known_proved_rows_faithfulness_is_pinned() -> None:
    """The decisive lock. Every other faithfulness test only checks the
    split's *shape* (valid value present, counts partition) — all of which
    a future agent satisfies by flipping prop_6_1/6_2/7_1 to `substantive`,
    re-inflating the abstract while the suite stays green (the recurrence-#7
    path RedTeam found). This pins the split's *truth* to the primary Lean:
    the two genuine proofs and the three statement-restricted rows are
    named explicitly, with the Lean lemma cited. Changing a row's real
    faithfulness requires changing this test, deliberately and visibly."""
    thms = _theorems()
    drift = {
        lab: {"registry": thms.get(lab, {}).get("faithfulness"), "pinned": want}
        for lab, want in _PINNED_FAITHFULNESS.items()
        if str(thms.get(lab, {}).get("faithfulness", "")) != want
    }
    assert not drift, (
        "faithfulness of a known proved row drifted from the RedTeam-"
        f"pinned ground truth: {drift}. These tags encode what the Lean "
        "body actually proves vs. its manuscript name (see the per-row "
        "Lean citations in _PINNED_FAITHFULNESS and "
        "docs/reference/veridical_status.md). If a Lean body genuinely "
        "changed, update the pin AND the ledger deliberately — do not "
        "relabel to silence this."
    )


def _blocks(text: str) -> list[str]:
    """Paragraph blocks (split on blank lines). A carve-out must sit in
    the SAME or an ADJACENT block as the proved-count mention — a marker
    200 lines away is the exact gerrymander this lock exists to kill."""
    return re.split(r"\n\s*\n", text)


def test_no_reader_surface_states_proved_count_without_faithfulness() -> None:
    """Discovered, NOT curated, and *locally* scoped. Any reader-facing
    surface that states the Lean proved-count must co-locate the
    statement-faithfulness carve-out IN THE SAME OR ADJACENT PARAGRAPH —
    not merely somewhere in the file. This is the structural lock that
    closes the recurring review loop: 'done' == the plain reading is true,
    enforced repo-wide and per-paragraph. Reverting any headline rewrite
    re-introduces a bare count here and fails this test — a buried ledger,
    even in the same file, is disclosure, not remediation."""
    # Scope = surfaces where a *reader forms the scientific belief* about
    # the Lean track: the manuscript itself, the repo READMEs, the agent
    # contracts, and the one public docs aggregate RedTeam flagged
    # (four_track_coherence). Deliberately NOT all of docs/**: the audit
    # home (veridical_status.md) IS the carve-out; docs/CHANGELOG.md is a
    # deliberately-frozen historical revision log (rewriting it to satisfy
    # a gate is itself the dishonesty pattern); internal styleguide /
    # mechanism / per-row reference docs document the counter, not a
    # scientific claim. This is a principled scope tied to where the
    # over-claim reaches a reader, not a convenience exemption — extend it
    # the moment a NEW reader-facing scientific surface appears.
    surfaces = sorted(MANUSCRIPT_DIR.glob("*.md")) + [
        PROJECT / "README.md",
        PROJECT / "AGENTS.md",
        MANUSCRIPT_DIR / "AGENTS.md",
        PROJECT / "docs" / "reference" / "four_track_coherence.md",
    ]
    # AGGREGATE proved-count detector only: the token, `N (algebraically)
    # proved`, and spelled-out "five proved". Deliberately does NOT match a
    # per-row audit-table cell (`| `prop_6_1` | … | proved |`) — those have
    # no digit adjacent to "proved" and are the legitimate audit surface,
    # not the headline over-claim. Asymmetry favours the auditor on the
    # aggregate (where the over-claim lives), not on per-row tables.
    states_proved_count = re.compile(
        r"theorem_status_proved_count"
        r"|\b\d+\s+(?:algebraically\s+)?`?proved`?\b"
        r"|\b(?:two|three|four|five|six|seven|eight|nine|ten)\s+"
        r"(?:algebraically\s+)?`?proved`?\b",
        re.IGNORECASE,
    )
    carveout_markers = (
        "theorem_proved_substantive_count",
        "theorem_proved_restricted_count",
        "theorem_proved_definitional_count",
        "statement-restricted",
        "faithfulness",
        "veridical_status",
    )
    offenders = []
    for p in surfaces:
        if not p.exists():
            continue
        # veridical_status.md IS the per-row audit home; its own status
        # table legitimately tabulates `proved` and carries the carve-out
        # globally — exempt the canonical ledger itself from the
        # per-paragraph rule (it is the carve-out).
        is_ledger = p.name == "veridical_status.md"
        blocks = _blocks(p.read_text(encoding="utf-8"))
        for i, blk in enumerate(blocks):
            if not states_proved_count.search(blk):
                continue
            window = blocks[max(0, i - 1) : i + 2]
            if is_ledger or any(m in b for b in window for m in carveout_markers):
                continue
            offenders.append(f"{p.relative_to(PROJECT).as_posix()} (block {i})")
    assert not offenders, (
        "reader-facing surfaces state the Lean proved-count with NO "
        f"statement-faithfulness carve-out in the same/adjacent paragraph: "
        f"{offenders}. Every site that gives the proved-count must also "
        "state the substantive / statement-restricted split (or point to "
        "veridical_status.md) RIGHT THERE. Disclosure elsewhere — even in "
        "the same file — is not remediation."
    )


def test_readme_and_abstract_agree_on_theorem_5_1_analytic_status() -> None:
    """Structural F1 close (RedTeam 2026-05-18). The Theorem-5.1
    analytic-status rewrite previously landed in the abstract but the
    README still asserted the *opposite* stale claim while presenting
    itself as authoritative — the recurring 'disclosure-not-remediation,
    one level up' gerrymander. This pins README and 0A to agree:
    neither may carry the stale 'does not currently machine-check ...
    decomposition' negative, and BOTH must co-locate the
    machine-checked-in-ℝ claim with its honest Float↔ℝ residual. A
    future edit that re-introduces the contradiction fails HERE."""
    readme = (PROJECT / "README.md").read_text(encoding="utf-8")
    abstract = (MANUSCRIPT_DIR / "0A_abstract.md").read_text(encoding="utf-8")

    stale = re.compile(
        r"does\s+\*?\*?not\s+currently\*?\*?\s+machine-check"
        r"[^.]*?(decomposition|KL-chain-rule|analytic)",
        re.IGNORECASE | re.DOTALL,
    )
    for name, text in (("README.md", readme), ("0A_abstract.md", abstract)):
        assert not stale.search(text), (
            f"{name} still carries the SUPERSEDED 'does not currently "
            "machine-check the analytic/decomposition payload' claim. "
            "Theorem 5.1's analytic kernel IS machine-checked in ℝ "
            "(MathlibProofs.entanglement_decomposition_generalK). Update "
            "this surface to match the abstract — a contradicting "
            "'authoritative' surface is the exact recurrence pattern."
        )

    # Both reader-facing surfaces must carry the strength AND the honest
    # residual together (no front-loading the strength without the gap).
    for name, text in (("README.md", readme), ("0A_abstract.md", abstract)):
        has_strength = ("machine-checked" in text) and ("ℝ" in text or "mathbb{R}" in text)
        names_residual = "Float" in text and ("ℝ" in text or "mathbb{R}" in text)
        assert has_strength and names_residual, (
            f"{name} must state the Theorem-5.1 analytic strength "
            "(machine-checked in ℝ) AND co-locate the Float↔ℝ residual; "
            f"got strength={has_strength}, residual_named={names_residual}. "
            "Strength without the residual on the same surface is the "
            "over-claim RedTeam flagged."
        )

    # RedTeam 2026-05-19 B-fix4: the FULL S01 identity is now genuinely
    # ℝ-machine-checked, so the pre-discharge "kernel-not-full / not full
    # formal verification / analytic discharge is unbuilt Mathlib4 work /
    # prose+numeric only" framing is RETIRED. README and 6C shipped it as
    # a live contradiction after the close. Fail-closed if any reader
    # surface re-introduces the retired framing — the recurring
    # concordance defect, structurally prevented this time.
    six_c = (MANUSCRIPT_DIR / "6C_discussion_and_outlook.md").read_text(encoding="utf-8")
    retired = re.compile(
        r"not\s+the\s+full\s+free-energy\s+identity"
        r"|prose\s*\+\s*numeric\s+witness\s+only"
        r"|prose-?\s*and\s*numerically-witnessed\s+only"
        r"|not\s+full\s+formal\s+verification"
        r"|analytic\s+discharge\s+is\s+scoped,?\s*unbuilt\s+Mathlib4\s+work"
        r"|does\s+not\s+replace\s+the\s+Mathlib4\s+analytic\s+discharge",
        re.IGNORECASE,
    )
    for name, text in (
        ("README.md", readme),
        ("0A_abstract.md", abstract),
        ("6C_discussion_and_outlook.md", six_c),
    ):
        hit = retired.search(text)
        assert not hit, (
            f"{name} re-introduced the RETIRED pre-discharge framing "
            f"({hit.group(0)!r}). The full S01 free-energy identity IS "
            "machine-checked in ℝ (MathlibProofs.free_energy_decomposition_full); "
            "this stale 'kernel-only / unbuilt Mathlib4' claim is a live "
            "contradiction with the abstract/CHANGELOG/ledger — the exact "
            "recurring concordance defect this pin now structurally blocks."
        )
