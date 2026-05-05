#!/usr/bin/env python3
"""Generate a compact source index for raw and extracted project materials."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}
SECRET_PARTS = {"secrets", "credentials", "api-keys", "tokens", ".git"}
DOC_EXTS = {".docx", ".pdf", ".md", ".txt", ".pptx"}
DATA_EXTS = {".xlsx", ".xls", ".csv", ".tsv"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
DIAGRAM_EXTS = {".drawio", ".xml"}


def is_secretish(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if path.name in SECRET_NAMES or path.name.startswith(".env."):
        return True
    return bool(lowered_parts & SECRET_PARTS)


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in DOC_EXTS:
        return "documents"
    if suffix in DATA_EXTS:
        return "data"
    if suffix in IMAGE_EXTS:
        return "images"
    if suffix in DIAGRAM_EXTS:
        return "diagrams"
    return "other"


def walk_visible(root: Path, relative_dir: str) -> list[Path]:
    base = root / relative_dir
    if not base.exists():
        return []
    visible: list[Path] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if is_secretish(rel):
            continue
        visible.append(rel)
    return visible


def is_under(path: Path, prefix: str) -> bool:
    return path.parts[: len(Path(prefix).parts)] == Path(prefix).parts


def bullet_rows(paths: list[Path]) -> list[str]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        grouped[classify(path)].append(str(path))
    lines: list[str] = []
    for group in ["documents", "data", "images", "diagrams", "other"]:
        items = grouped.get(group, [])
        if not items:
            continue
        lines.append(f"### {group.title()}")
        lines.append("")
        for item in items:
            lines.append(f"- `{item}`")
        lines.append("")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate memory/11-source-index.md from visible project files.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--output", default="memory/11-source-index.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = root / args.output
    raw_paths = [path for path in walk_visible(root, "raw") if not is_under(path, "raw/extracted")]
    extracted_paths = walk_visible(root, "raw/extracted")

    lines = [
        "# Source Index",
        "",
        "This index tracks visible source materials without reading secret values.",
        "",
        "## Raw Evidence",
        "",
    ]
    if raw_paths:
        lines.extend(bullet_rows(raw_paths))
    else:
        lines.append("_No raw evidence indexed yet._")
        lines.append("")

    lines.extend(["## Extracted Sources", ""])
    if extracted_paths:
        lines.extend(bullet_rows(extracted_paths))
    else:
        lines.append("_No extracted sources indexed yet._")
        lines.append("")

    lines.extend(
        [
            "## Extraction Notes",
            "",
            "- Preserve originals under `raw/`.",
            "- Prefer schema-level extraction for operational data.",
            "- Keep secrets out of extracted markdown and memory files.",
            "",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
