"""TeX post-processing helpers aligned with template combined-PDF behavior."""

from __future__ import annotations

import re
from pathlib import Path

from orchestration.pdf_config import ManuscriptConfig


def patch_red_hyperlinks(tex_content: str) -> str:
    """Turn Pandoc's ``hidelinks`` into uniform red ``colorlinks``."""
    if "hidelinks" in tex_content:
        tex_content = tex_content.replace(
            "hidelinks,",
            "colorlinks=true,linkcolor=red,urlcolor=red,citecolor=red,anchorcolor=red,filecolor=red,",
        )
        tex_content = tex_content.replace(
            "  hidelinks,\n",
            "  colorlinks=true,\n  linkcolor=red,\n  urlcolor=red,\n  citecolor=red,\n",
        )
    color_keys = ("linkcolor", "urlcolor", "citecolor", "anchorcolor", "filecolor")
    marker = "\\hypersetup{"
    blocks: list[tuple[int, int, str]] = []
    index = 0
    while True:
        start = tex_content.find(marker, index)
        if start < 0:
            break
        body_start = start + len(marker)
        depth = 1
        cursor = body_start
        while cursor < len(tex_content) and depth > 0:
            char = tex_content[cursor]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            cursor += 1
        if depth != 0:
            break
        blocks.append((start, cursor, tex_content[body_start : cursor - 1]))
        index = cursor
    for start, end, body in reversed(blocks):
        if not any(re.search(rf"\b{key}\s*=", body) for key in color_keys):
            continue
        new_body = body
        for key in color_keys:
            new_body = re.sub(rf"\b{key}\s*=\s*[A-Za-z][A-Za-z0-9]*", f"{key}=red", new_body)
        tex_content = tex_content[:start] + "\\hypersetup{" + new_body + "}" + tex_content[end:]
    return tex_content


def postprocess_combined_tex(*, combined_tex: Path, config: ManuscriptConfig) -> None:
    text = combined_tex.read_text(encoding="utf-8")
    text = patch_red_hyperlinks(text)

    author_block = config.author_block()
    if author_block:
        replacement = "\\author{" + author_block + "}"

        def _swap_author(_: re.Match[str]) -> str:
            return replacement

        text, subs = re.subn(r"\\author\{[^}]*\}", _swap_author, text, count=1)
        if subs == 0:
            text = text.replace("\\begin{document}", f"{replacement}\n\\begin{{document}}", 1)

    date = str(config.paper.get("date") or "")
    if not date:
        text, _ = re.subn(r"\\date\{\s*\}", r"\\date{\\today}", text, count=1)

    title_body = config.title_page_body()
    text = text.replace("\\maketitle", title_body, 1)
    combined_tex.write_text(text, encoding="utf-8")
