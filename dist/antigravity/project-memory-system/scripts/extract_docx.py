#!/usr/bin/env python3
"""Extract DOCX paragraphs and simple tables to markdown/text."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", Path(name).stem).strip("-") or "document"


def style_to_md(style: str, text: str) -> str:
    style_l = (style or "").lower()
    text = text.strip()
    if not text:
        return ""
    if "title" in style_l or "heading 1" in style_l:
        return f"# {text}"
    if "heading 2" in style_l:
        return f"## {text}"
    if "heading 3" in style_l:
        return f"### {text}"
    if "heading 4" in style_l:
        return f"#### {text}"
    if "list bullet" in style_l:
        return f"- {text}"
    if "list number" in style_l:
        return f"1. {text}"
    return text


def table_to_md(table) -> list[str]:
    rows = [[cell.text.replace("\n", "<br>").strip() for cell in row.cells] for row in table.rows]
    if not rows:
        return []
    width = max(len(row) for row in rows)
    rows = [row + [""] * (width - len(row)) for row in rows]
    out = ["| " + " | ".join(rows[0]) + " |", "| " + " | ".join(["---"] * width) + " |"]
    out.extend("| " + " | ".join(row) + " |" for row in rows[1:])
    return out


def iter_blocks(document):
    from docx.oxml.table import CT_Tbl
    from docx.oxml.text.paragraph import CT_P
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract DOCX to markdown and text.")
    parser.add_argument("input", help="DOCX file")
    parser.add_argument("--markdown-dir", default="raw/extracted/markdown")
    parser.add_argument("--text-dir", default="raw/extracted/text")
    parser.add_argument("--source-prefix", default="")
    args = parser.parse_args()

    try:
        from docx import Document
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise SystemExit("python-docx is required for DOCX extraction") from exc

    path = Path(args.input)
    document = Document(str(path))
    md_dir = Path(args.markdown_dir)
    text_dir = Path(args.text_dir)
    md_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)
    base = slug(path.name)
    source = f"{args.source_prefix}{path.name}" if args.source_prefix else str(path)

    md_lines = [f"# Source Extraction: {path.name}", "", f"Original file: `{source}`", ""]
    txt_lines = [f"Source Extraction: {path.name}", f"Original file: {source}", ""]
    for block in iter_blocks(document):
        if isinstance(block, Paragraph):
            converted = style_to_md(block.style.name if block.style else "", block.text)
            if converted:
                md_lines.extend([converted, ""])
                txt_lines.extend([block.text.strip(), ""])
        elif isinstance(block, Table):
            table_md = table_to_md(block)
            if table_md:
                md_lines.extend(table_md + [""])
                for row in block.rows:
                    txt_lines.append(" | ".join(cell.text.strip().replace("\n", " / ") for cell in row.cells))
                txt_lines.append("")

    (md_dir / f"{base}.md").write_text("\n".join(md_lines).rstrip() + "\n", encoding="utf-8")
    (text_dir / f"{base}.txt").write_text("\n".join(txt_lines).rstrip() + "\n", encoding="utf-8")
    print(str(md_dir / f"{base}.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
