#!/usr/bin/env python3
"""Read-only project inventory for project-memory-system."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}
SECRET_PARTS = {"secrets", "credentials", "api-keys", "tokens", ".git"}
AGENT_FILES = ["AGENTS.md", "CLAUDE.md", "CODEX.md", "ANTIGRAVITY.md", "GEMINI.md"]
MEMORY_DIRS = ["memory", "project-system", "raw", "workstreams", "deliverables", "logs"]


def is_secretish(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if path.name in SECRET_NAMES:
        return True
    if path.name.startswith(".env."):
        return True
    return bool(lowered_parts & SECRET_PARTS)


def project_type(root: Path, exts: Counter[str], files: list[Path]) -> str:
    names = {p.name for p in files}
    if {"package.json", "pnpm-workspace.yaml", "turbo.json"} & names:
        return "software"
    if any(ext in exts for ext in [".docx", ".xlsx", ".pptx"]) and any(ext in exts for ext in [".xlsx", ".csv"]):
        return "consulting-or-client"
    if any(ext in exts for ext in [".pdf", ".bib", ".ipynb"]):
        return "research-or-data"
    if (root / "memory").exists() or (root / "AGENTS.md").exists():
        return "memory-enabled"
    return "mixed-or-unknown"


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a project folder without reading secret values.")
    parser.add_argument("root", nargs="?", default=".", help="Project root to inspect")
    parser.add_argument("--max-files", type=int, default=5000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files: list[Path] = []
    skipped_secretish: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath_p = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not is_secretish(dirpath_p / d)]
        for filename in filenames:
            path = dirpath_p / filename
            rel = path.relative_to(root)
            if is_secretish(rel):
                skipped_secretish.append(str(rel))
                continue
            files.append(rel)
            if len(files) >= args.max_files:
                break
        if len(files) >= args.max_files:
            break

    ext_counts = Counter(p.suffix.lower() or "<none>" for p in files)
    top_dirs = Counter(p.parts[0] if len(p.parts) > 1 else "." for p in files)
    categories: dict[str, list[str]] = defaultdict(list)
    for p in files:
        ext = p.suffix.lower()
        if ext in [".docx", ".pdf", ".md", ".txt", ".pptx"]:
            categories["documents"].append(str(p))
        elif ext in [".xlsx", ".xls", ".csv", ".tsv"]:
            categories["data"].append(str(p))
        elif ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"]:
            categories["images"].append(str(p))
        elif ext in [".drawio", ".xml"]:
            categories["diagrams"].append(str(p))
        elif ext in [".py", ".js", ".ts", ".tsx", ".json", ".yaml", ".yml"]:
            categories["code-config"].append(str(p))

    result = {
        "root": str(root),
        "project_type_guess": project_type(root, ext_counts, files),
        "file_count": len(files),
        "extension_counts": dict(ext_counts.most_common()),
        "top_directories": dict(top_dirs.most_common()),
        "agent_files": {name: (root / name).exists() for name in AGENT_FILES},
        "memory_dirs": {name: (root / name).exists() for name in MEMORY_DIRS},
        "has_git": (root / ".git").exists(),
        "has_gitignore": (root / ".gitignore").exists(),
        "categories": {key: value[:100] for key, value in categories.items()},
        "skipped_secretish_count": len(skipped_secretish),
        "truncated": len(files) >= args.max_files,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
