"""Extract Lean theorem signatures from `lean/ActinfPolicyEntanglement/`."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LeanSnippet:
    """One declaration extracted from a Lean source file.

    `body` is the raw text from the start of the `theorem` / `def` /
    `lemma` keyword up to (and including) the line that introduces the
    proof (`by`, `:=`, or the final closing of the type).  `docstring`
    is the preceding `/-- … -/` block (if any).
    """

    label: str  # registry label (`thm_4_1`, …)
    module: str  # Lean module name (`Decomposition`)
    qualified_name: str  # full Lean name (`Bipartite.schmidtRank_one_iff_meanField`)
    keyword: str  # `theorem` / `def` / `lemma` / `instance`
    docstring: str
    body: str
    file_path: Path
    start_line: int


# Lean keywords that introduce a top-level declaration we may want to
# embed.  We exclude `namespace` / `import` / `open`.
_DECL_KEYWORDS = ("theorem", "lemma", "def", "instance", "abbrev", "structure")


def _scan_module(module_path: Path) -> dict[str, LeanSnippet]:
    """Parse a single `.lean` file and return `{qualified_name: LeanSnippet}`.

    Resolves nested `namespace ... end` blocks so a declaration inside
    `namespace Bipartite` shows up as `Bipartite.<name>`.
    """
    text = module_path.read_text()
    lines = text.splitlines()
    namespace_stack: list[str] = []
    snippets: dict[str, LeanSnippet] = {}

    i = 0
    in_block_comment = False
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # Skip block-comment regions `/- … -/` and `/-! … -/` so decl
        # keywords inside narrative docs (e.g. "structure of") aren't
        # mis-parsed as definitions.
        if in_block_comment:
            if "-/" in stripped:
                in_block_comment = False
            i += 1
            continue
        if stripped.startswith("/-") and "-/" not in stripped:
            in_block_comment = True
            i += 1
            continue
        if stripped.startswith("/-") and "-/" in stripped:
            # single-line block comment — skip
            i += 1
            continue
        if stripped.startswith("--"):
            i += 1
            continue

        # Track namespace context.
        m_ns = re.match(r"namespace\s+(\S+)", stripped)
        if m_ns:
            namespace_stack.append(m_ns.group(1))
            i += 1
            continue
        m_end = re.match(r"end\s+(\S+)?", stripped)
        if m_end and namespace_stack:
            namespace_stack.pop()
            i += 1
            continue

        # Try to consume a declaration starting at line i.
        m_decl = re.match(
            r"^(?P<kw>theorem|lemma|def|instance|abbrev|structure)\s+(?P<name>\S+)",
            stripped,
        )
        if m_decl:
            keyword = m_decl.group("kw")
            short_name = m_decl.group("name").rstrip(":")
            # Walk backwards to capture an attached `/-- … -/` docstring.
            doc_lines: list[str] = []
            j = i - 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            # Block-style doc?
            if j >= 0 and lines[j].strip().endswith("-/"):
                k = j
                while k >= 0 and "/-" not in lines[k]:
                    k -= 1
                if k >= 0:
                    doc_lines = lines[k : j + 1]
            docstring = "\n".join(doc_lines).strip()

            # Walk forward until we see the proof opener: ` by` at end of
            # line, or `:=` introducing the term, or a line that is just
            # `:=` / `by`.  Inclusive: keep the opener line.
            body_lines: list[str] = [raw]
            k = i + 1
            opener_re = re.compile(r":=|\bby\s*$|\bby\s+\S|\brfl\s*$")
            # If this line itself already opens (`by` / `:=`), stop here.
            if opener_re.search(raw):
                # Single-line decl — no further work.
                pass
            else:
                while k < len(lines):
                    body_lines.append(lines[k])
                    if opener_re.search(lines[k]):
                        break
                    if not lines[k].strip() and k > i + 1:
                        # Blank line inside a multi-line decl is allowed
                        # — keep going only if next non-blank still
                        # belongs to this decl (continues with ' ' indent
                        # or ends with ':=' / 'by').
                        pass
                    # Hard stop: next top-level keyword starts.
                    nxt = lines[k].strip()
                    if any(nxt.startswith(kw + " ") for kw in _DECL_KEYWORDS) and k != i:
                        # rewind one — that line belongs to the next decl.
                        body_lines.pop()
                        k -= 1
                        break
                    k += 1
            body = "\n".join(body_lines).rstrip()
            qualified = ".".join(namespace_stack[1:] + [short_name]) if len(namespace_stack) > 1 else short_name
            # Strip the outer `ActinfPolicyEntanglement.` prefix; expose
            # only inner-namespace qualifiers like `Bipartite.foo`.
            snippets[qualified] = LeanSnippet(
                label="",
                module=module_path.stem,
                qualified_name=qualified,
                keyword=keyword,
                docstring=docstring,
                body=body,
                file_path=module_path,
                start_line=i + 1,
            )
            i = max(k + 1, i + 1)
            continue
        i += 1

    return snippets


def load_lean_snippets(lean_dir: Path) -> dict[tuple[str, str], LeanSnippet]:
    """Walk every `.lean` file under `lean_dir` and return a mapping
    keyed by `(module, qualified_name)` for fast lookup.
    """
    out: dict[tuple[str, str], LeanSnippet] = {}
    for path in sorted(lean_dir.glob("*.lean")):
        for qname, snip in _scan_module(path).items():
            out[(path.stem, qname)] = snip
    return out


def render_lean_snippet(snip: LeanSnippet, *, status: str = "") -> str:
    """Render a `LeanSnippet` as a fenced Lean code block with a
    one-line caption pointing at the source file.

    Use tilde fences instead of backtick fences because Lean docstrings
    may legitimately contain Markdown examples fenced with triple
    backticks. A tilde fence keeps the entire extracted declaration in
    one block when Pandoc renders the PDF.
    """
    rel = f"`lean/ActinfPolicyEntanglement/{snip.module}.lean:{snip.start_line}`"
    status_tag = f" [status: **{status}**]" if status else ""
    parts = [
        "~~~lean",
        f"-- From {rel}{status_tag}",
    ]
    if snip.docstring:
        # Trim leading/trailing whitespace inside the doc block.
        parts.append(snip.docstring)
    parts.append(snip.body)
    parts.append("~~~")
    return "\n".join(parts)
