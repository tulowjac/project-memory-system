#!/usr/bin/env python3
"""Create a project-memory scaffold without overwriting existing files."""

from __future__ import annotations

import argparse
from pathlib import Path

DIRS = [
    "project-system",
    "memory",
    "raw/documents",
    "raw/data",
    "raw/extracted/markdown",
    "raw/extracted/text",
    "workstreams",
    "deliverables/drafts",
    "deliverables/final",
    "deliverables/archive",
    "logs/handoffs",
]

POINTER = """# Project Agent Instructions

This project uses `AGENTS.md` as the canonical cross-agent instruction file.

Read `AGENTS.md` first, then follow:

- `project-system/OPERATING-MANUAL.md`
- `project-system/MEMORY-PROTOCOL.md`
- `project-system/AGENT-HANDOFF.md`

Do not treat this file as an independent source of truth.
"""

FILES = {
    "AGENTS.md": """# Project Agent Instructions

This file is the canonical cross-agent entry point for this project.

Before doing substantive work:

1. Read `project-system/OPERATING-MANUAL.md`.
2. Read `project-system/MEMORY-PROTOCOL.md`.
3. Check relevant files in `memory/`.
4. Prefer `memory/` first, then `raw/extracted/`, then originals in `raw/`.
5. Leave a note in `logs/agent-activity-log.md` after meaningful work.

Never read, print, summarize, log, or commit secret values.
""",
    "CLAUDE.md": POINTER,
    "CODEX.md": POINTER,
    "ANTIGRAVITY.md": POINTER,
    "GEMINI.md": POINTER,
    "NEXT-ACTIONS.md": "# Next Actions\n\n- Run a project scan.\n- Add raw sources.\n- Rework memory after new sources are added.\n",
    "project-system/OPERATING-MANUAL.md": "# Operating Manual\n\nDescribe how this project should be worked.\n",
    "project-system/MEMORY-PROTOCOL.md": "# Memory Protocol\n\nRaw evidence, extracted sources, and synthesized memory are separate layers.\n",
    "project-system/AGENT-HANDOFF.md": "# Agent Handoff Protocol\n\nRecord meaningful work in `logs/agent-activity-log.md`.\n",
    "logs/agent-activity-log.md": "# Agent Activity Log\n",
    ".gitignore": ".DS_Store\n.env\n.env.*\n!.env.example\nsecrets/\ncredentials/\napi-keys/\ntokens/\n*.pem\n*.key\n",
}

MEMORY_FILES = [
    "00-project-brief.md",
    "01-current-state.md",
    "02-stakeholders.md",
    "03-discovery-log.md",
    "04-open-questions.md",
    "05-assumptions.md",
    "06-decisions.md",
    "07-opportunities.md",
    "08-workstream-primary.md",
    "09-systems-and-data.md",
    "10-language-and-style.md",
    "11-source-index.md",
    "12-subagent-tasks.md",
]


def write_if_allowed(path: Path, text: str, force: bool, dry_run: bool) -> str:
    if path.exists() and not force:
        return f"skip existing {path}"
    if dry_run:
        return f"would write {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return f"wrote {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create project memory scaffold.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    actions: list[str] = []
    for dirname in DIRS:
        path = root / dirname
        if args.dry_run:
            actions.append(f"would mkdir {path}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            actions.append(f"mkdir {path}")
    for rel, text in FILES.items():
        actions.append(write_if_allowed(root / rel, text, args.force, args.dry_run))
    for filename in MEMORY_FILES:
        actions.append(write_if_allowed(root / "memory" / filename, f"# {filename[:-3].replace('-', ' ').title()}\n", args.force, args.dry_run))
    print("\n".join(actions))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
