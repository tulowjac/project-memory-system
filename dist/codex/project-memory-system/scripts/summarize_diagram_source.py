#!/usr/bin/env python3
"""Summarize Draw.io/XML-style diagram source into markdown labels."""

from __future__ import annotations

import argparse
import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def slug(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", Path(name).stem).strip("-") or "diagram"


def clean_label(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    value = re.sub(r"<[^>]+>", "", value)
    value = value.replace("\xa0", " ")
    return "\n".join(line.strip() for line in value.splitlines() if line.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract labels from Draw.io/XML diagrams.")
    parser.add_argument("input")
    parser.add_argument("--markdown-dir", default="raw/extracted/markdown")
    args = parser.parse_args()

    path = Path(args.input)
    md_dir = Path(args.markdown_dir)
    md_dir.mkdir(parents=True, exist_ok=True)
    labels: list[tuple[str, str]] = []
    edges: list[tuple[str, str, str]] = []
    try:
        root = ET.parse(path).getroot()
        for cell in root.iter("mxCell"):
            value = clean_label(cell.attrib.get("value", ""))
            cell_id = cell.attrib.get("id", "")
            if value:
                labels.append((cell_id, value))
            if cell.attrib.get("edge") == "1":
                source = cell.attrib.get("source", "")
                target = cell.attrib.get("target", "")
                if source or target:
                    edges.append((source, target, value))
    except ET.ParseError:
        labels.append(("parse-error", "Could not parse this diagram source as XML. Inspect the original visually."))

    lines = [f"# Diagram Structure: {path.name}", "", f"Original file: `{path}`", "", "## Labels", ""]
    if labels:
        for cell_id, value in labels:
            lines.append(f"- `{cell_id}`: {value.replace(chr(10), ' / ')}")
    else:
        lines.append("_No text labels found._")
    lines.extend(["", "## Edges", ""])
    if edges:
        for source, target, label in edges:
            suffix = f" ({label.replace(chr(10), ' / ')})" if label else ""
            lines.append(f"- `{source}` -> `{target}`{suffix}")
    else:
        lines.append("_No explicit edges found._")
    out = md_dir / f"{slug(path.name)}.md"
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
