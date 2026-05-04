"""Token regular expressions and a single resolver entry point.
"""

from __future__ import annotations

import re

FIG_RE = re.compile(r"\[\[FIG:(?P<label>[A-Za-z0-9_]+)\]\]")
FIGREF_RE = re.compile(r"\[\[FIGREF:(?P<label>[A-Za-z0-9_]+)\]\]")
EQ_RE = re.compile(r"\[\[EQ:(?P<label>[A-Za-z0-9_]+)\]\]")
EQREF_RE = re.compile(r"\[\[EQREF:(?P<label>[A-Za-z0-9_]+)\]\]")
VAR_RE = re.compile(
    r"\[\[VAR:(?P<key>[A-Za-z0-9_]+)(?::(?P<fmt>[^\]]+))?\]\]"
)
# Citation token: matches single `[@key]` AND multi-citation
# `[@key1; @key2; @key3]` (Pandoc semicolon-separated form).  The
# `inner` group captures the body inside the outer brackets so the
# resolver can split on `;` and emit each key.
CITATION_RE = re.compile(
    r"\[(?P<inner>@[A-Za-z0-9_-]+(?:\s*;\s*@[A-Za-z0-9_-]+)*)\]"
)
CITELIST_RE = re.compile(r"\[\[CITELIST:(?P<topic>[A-Za-z0-9_]+)\]\]")

# Section + theorem tokens.
# `[[SEC:label]]`     → "§<number> <title>" (full label, used in headings)
# `[[SECREF:label]]`  → "§<number>"          (inline cross-reference)
# `[[THM:label]]`     → "**Kind N (Name).**" (full bold theorem-block label)
# `[[THMREF:label]]`  → "Kind N"             (inline cross-reference)
SEC_RE = re.compile(r"\[\[SEC:(?P<label>[A-Za-z0-9_.]+)\]\]")
SECREF_RE = re.compile(r"\[\[SECREF:(?P<label>[A-Za-z0-9_.]+)\]\]")
THM_RE = re.compile(r"\[\[THM:(?P<label>[A-Za-z0-9_]+)\]\]")
THMREF_RE = re.compile(r"\[\[THMREF:(?P<label>[A-Za-z0-9_]+)\]\]")

# `[[LEAN:label]]` → fenced Lean code block extracted from the live
# `lean/ActinfPolicyEntanglement/<module>.lean` file (looked up via
# the theorem registry's `lean_module` + `lean_name` fields).
LEAN_RE = re.compile(r"\[\[LEAN:(?P<label>[A-Za-z0-9_]+)\]\]")


def iter_tokens(text: str):
    """Yield ``(kind, label, span)`` triples for every token in `text`.

    Useful for the validator (which only needs to know what tokens are
    present, not how to render them).
    """
    for m in FIG_RE.finditer(text):
        yield ("FIG", m.group("label"), m.span())
    for m in FIGREF_RE.finditer(text):
        yield ("FIGREF", m.group("label"), m.span())
    for m in EQ_RE.finditer(text):
        yield ("EQ", m.group("label"), m.span())
    for m in EQREF_RE.finditer(text):
        yield ("EQREF", m.group("label"), m.span())
    for m in VAR_RE.finditer(text):
        yield ("VAR", m.group("key"), m.span())
    for m in CITATION_RE.finditer(text):
        # Each `key` inside a `[@a; @b]` multi-citation is yielded
        # individually so token-validation reports the missing key
        # rather than the whole bracket body.
        for key in re.findall(r"@([A-Za-z0-9_-]+)", m.group("inner")):
            yield ("CITE", key, m.span())
    for m in CITELIST_RE.finditer(text):
        yield ("CITELIST", m.group("topic"), m.span())
    for m in SEC_RE.finditer(text):
        yield ("SEC", m.group("label"), m.span())
    for m in SECREF_RE.finditer(text):
        yield ("SECREF", m.group("label"), m.span())
    for m in THM_RE.finditer(text):
        yield ("THM", m.group("label"), m.span())
    for m in THMREF_RE.finditer(text):
        yield ("THMREF", m.group("label"), m.span())
    for m in LEAN_RE.finditer(text):
        yield ("LEAN", m.group("label"), m.span())
