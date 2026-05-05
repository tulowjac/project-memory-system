#!/usr/bin/env python3
"""Draft durable memory updates from source index and extracted materials."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path


def read_text(path: Path, limit: int = 12000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return text[:limit]


def summarize_bullets(text: str, max_items: int = 8) -> list[str]:
    bullets: list[str] = []
    seen: set[str] = set()
    for raw in text.splitlines():
        cleaned = raw.strip().lstrip("-*0123456789. ").strip()
        if len(cleaned) < 20:
            continue
        if cleaned.lower() in seen:
            continue
        seen.add(cleaned.lower())
        bullets.append(cleaned)
        if len(bullets) >= max_items:
            break
    return bullets


def file_digest(path: Path) -> tuple[str, list[str]]:
    text = read_text(path)
    bullets = summarize_bullets(text, max_items=4)
    return (str(path), bullets)


def main() -> int:
    parser = argparse.ArgumentParser(description="Draft memory updates from source index and extracted markdown.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--source-index", default="memory/11-source-index.md")
    parser.add_argument("--output", default="memory/03-discovery-log.md")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    source_index = root / args.source_index
    output = root / args.output
    extracted_dir = root / "raw" / "extracted" / "markdown"

    extracted_files = sorted(p for p in extracted_dir.rglob("*.md")) if extracted_dir.exists() else []
    category_counts = Counter(p.suffix.lower() or "<none>" for p in extracted_files)

    lines = [
        "# Discovery Log",
        "",
        "## Draft Update",
        "",
        "This file is a draft starting point for durable memory updates. Review and keep only lasting facts, decisions, assumptions, questions, and opportunities.",
        "",
        "## Source Snapshot",
        "",
        f"- Source index present: {'yes' if source_index.exists() else 'no'}",
        f"- Extracted markdown files reviewed: {len(extracted_files)}",
        f"- Extracted file types: {', '.join(sorted(category_counts)) if category_counts else 'none'}",
        "",
        "## Candidate Durable Notes",
        "",
    ]

    if not extracted_files:
        lines.append("- No extracted markdown found yet. Add sources and run extraction before drafting memory.")
        lines.append("")
    else:
        for path in extracted_files[:12]:
            rel = path.relative_to(root)
            _, bullets = file_digest(path)
            lines.append(f"### `{rel}`")
            lines.append("")
            if bullets:
                for bullet in bullets:
                    lines.append(f"- {bullet}")
            else:
                lines.append("- Review manually; no clear bullet-like summary lines were found.")
            lines.append("")

    lines.extend(
        [
            "## Open Questions To Resolve",
            "",
            "- Which facts from the candidate notes are durable enough for `memory/01-current-state.md`?",
            "- Which assumptions should move into `memory/05-assumptions.md`?",
            "- Which decisions or tradeoffs belong in `memory/06-decisions.md`?",
            "",
        ]
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
