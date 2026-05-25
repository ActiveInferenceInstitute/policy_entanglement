"""Manuscript validation — regex patterns."""

from __future__ import annotations

import re

HYPERLINK_RE = re.compile(r"\[(?P<text>[^\]]*)\]\((?P<href>[^)]+)\)")
HEADING_RE = re.compile(r"^#\s+\S")
SECTION_FILES_RE = re.compile(r"^(\d[A-Z]_|\d{2}_|S\d{2}|preamble)")

# `§N(.M)` mentioned anywhere in body prose.  We treat top-level §N as
# always-resolvable when the corresponding `0N_*.md` exists, and §N.M
# as resolvable when the target file actually contains a heading
# `## §N.M ...`.
SECTION_REF_RE = re.compile(r"§\s*(\d+)(?:\.(\d+))?")

# Hardcoded-reference detectors that flag prose like `§5` / `Theorem 5.1` /
# `Prop 7.2` outside of their permitted sites (headings, the bold theorem
# block label that introduces the statement, and inline code spans).
HARDCODED_SEC_RE = re.compile(r"§\s*\d+(?:\.\d+[a-z]?)?\b")
HARDCODED_THM_RE = re.compile(
    r"\b(Theorem|Proposition|Prop\.?|Corollary|Cor\.?|Lemma|Definition|Def\.?)\s+\d+(?:\.\d+)?\b"
)
HARDCODED_FIG_EQ_RE = re.compile(r"\b(Figure|Fig\.?|Equation|Eq\.?)\s+\(?\d+(?:\.\d+)?\)?\b")
HARDCODED_APPENDIX_RE = re.compile(r"\bAppendix\s+[A-Z]\b")
# Word-form section/table references (the `§` symbol is caught by
# HARDCODED_SEC_RE, but spelled-out "Section 7" / "section 7" and
# "Table 2" slip past it). Manuscript-internal cross-references must
# flow through `[[SECREF:...]]` / registry tokens, and even an external
# "see doc section 7" pointer is brittle — use a stable anchor instead.
HARDCODED_SEC_WORD_RE = re.compile(r"\b[Ss]ection\s+\d+(?:\.\d+)?\b")
HARDCODED_TABLE_RE = re.compile(r"\b[Tt]able\s+\d+\b")
FENCED_CODE_RE = re.compile(r"(```|~~~)[^\n]*\n.*?\1", re.DOTALL)
FORBIDDEN_CODE_FENCE_TOKEN_RE = re.compile(
    r"\[\[(?:EQ|EQREF|FIG|FIGREF|THM|THMREF|SEC|SECREF|LEAN|CITE|CITELIST):[^\]]+\]\]"
)
_INLINE_CODE_RE = re.compile(r"`+[^`\n]*`+")
_RENDERED_TOKEN_LEAK_RE = re.compile(
    r"\[\[(?:VAR|SEC|SECREF|THM|THMREF|FIG|FIGREF|EQ|EQREF|LEAN|CITELIST):[^\]]+\]\]"
    r"|\[\[MISSING:[^\]]+\]\]"
)
