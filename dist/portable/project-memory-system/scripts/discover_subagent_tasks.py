#!/usr/bin/env python3
"""Discover concrete sub-agent task candidates from project structure and memory trail."""

from __future__ import annotations

import argparse
import os
import re
from collections import Counter
from dataclasses import dataclass
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
CODE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".md"}
TASK_MARKERS = re.compile(r"\b(todo|fixme|next|blocked|follow[- ]?up|open question|needs?|opportunit|handoff|task)\b", re.I)
SECRET_VALUE_MARKERS = re.compile(r"\b(api[_-]?key|token|password|secret|credential)\b\s*[:=]", re.I)


@dataclass(frozen=True)
class Candidate:
    title: str
    agent_type: str
    why: str
    scope: str
    files: list[str]
    prompt: str


def is_secretish(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if path.name.lower() in SECRET_NAMES or path.name.lower().startswith(".env."):
        return True
    return bool(lowered_parts & SECRET_PARTS)


def walk_visible(root: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirpath_p = Path(dirpath)
        dirnames[:] = [dirname for dirname in dirnames if not is_secretish((dirpath_p / dirname).relative_to(root))]
        for filename in sorted(filenames):
            path = dirpath_p / filename
            rel = path.relative_to(root)
            if is_secretish(rel):
                continue
            files.append(rel)
            if len(files) >= max_files:
                return files
    return sorted(files)


def read_text(path: Path, limit: int = 8000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def collect_task_lines(root: Path, files: list[Path], max_lines: int = 8) -> list[str]:
    hint_files = [
        path
        for path in files
        if path.suffix.lower() in {".md", ".txt"}
        and (
            path.name.lower() in {"next-actions.md", "changelog.md", "release.md"}
            or path.parts[:1] in [("memory",), ("logs",), ("workstreams",), ("project-system",)]
        )
    ]
    task_lines: list[str] = []
    seen: set[str] = set()
    for rel in sorted(hint_files):
        for raw_line in read_text(root / rel).splitlines():
            line = raw_line.strip().lstrip("-*0123456789. ").strip()
            if len(line) < 12 or not TASK_MARKERS.search(line):
                continue
            if SECRET_VALUE_MARKERS.search(line):
                continue
            key = line.lower()
            if key in seen:
                continue
            seen.add(key)
            task_lines.append(f"{rel}: {line}")
            if len(task_lines) >= max_lines:
                return task_lines
    return task_lines


def category_counts(files: list[Path]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for path in files:
        suffix = path.suffix.lower()
        if suffix in DOC_EXTS:
            counts["documents"] += 1
        elif suffix in DATA_EXTS:
            counts["data"] += 1
        elif suffix in CODE_EXTS:
            counts["code-config"] += 1
        elif suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            counts["images"] += 1
        elif suffix in {".drawio", ".xml"}:
            counts["diagrams"] += 1
        else:
            counts["other"] += 1
    return counts


def existing(paths: list[Path], *prefixes: str) -> list[str]:
    prefix_paths = [Path(prefix).parts for prefix in prefixes]
    result: list[str] = []
    for path in paths:
        if any(path.parts[: len(prefix)] == prefix for prefix in prefix_paths):
            result.append(str(path))
    return result


def first_existing(paths: list[Path], names: list[str], limit: int = 6) -> list[str]:
    wanted = set(names)
    return [str(path) for path in paths if str(path) in wanted or path.name in wanted][:limit]


def discover(root: Path, max_files: int) -> tuple[list[Path], list[str], list[Candidate]]:
    files = walk_visible(root, max_files=max_files)
    task_lines = collect_task_lines(root, files)
    counts = category_counts(files)
    candidates: list[Candidate] = []

    raw_originals = [
        str(path)
        for path in files
        if path.parts[:1] == ("raw",) and path.parts[:2] != ("raw", "extracted")
    ]
    extracted_markdown = existing(files, "raw/extracted/markdown")
    memory_files = existing(files, "memory")
    workstream_files = existing(files, "workstreams")
    tests = [str(path) for path in files if "test" in path.name.lower() or "tests" in path.parts]
    scripts = existing(files, "core/scripts", "scripts")
    logs = existing(files, "logs")

    if raw_originals:
        candidates.append(
            Candidate(
                title="Review raw-to-extracted coverage",
                agent_type="worker",
                why=f"{len(raw_originals)} visible raw source file(s) may need extraction, profiling, or indexing.",
                scope="Compare raw sources to extracted markdown/text and update only approved derived artifacts.",
                files=raw_originals[:6] + extracted_markdown[:3] + first_existing(files, ["memory/11-source-index.md"]),
                prompt="Inspect raw sources by filename and type, identify which need extraction or profiling, then update the source index without reading or printing secret values.",
            )
        )

    if extracted_markdown or first_existing(files, ["memory/03-discovery-log.md", "memory/04-open-questions.md"]):
        candidates.append(
            Candidate(
                title="Synthesize durable memory updates",
                agent_type="worker",
                why="Extracted markdown or discovery/open-question notes exist and may contain durable facts, assumptions, decisions, or next actions.",
                scope="Review extracted/source-memory files and propose concise updates to durable memory files.",
                files=extracted_markdown[:6] + first_existing(files, ["memory/03-discovery-log.md", "memory/04-open-questions.md", "memory/06-decisions.md"]),
                prompt="Draft durable memory updates from extracted markdown and discovery logs. Keep only lasting facts, decisions, assumptions, open questions, and opportunities.",
            )
        )

    if task_lines:
        candidates.append(
            Candidate(
                title="Triage next actions and handoff notes",
                agent_type="explorer",
                why=f"{len(task_lines)} task-like line(s) were found in memory, logs, handoffs, changelog, or next-action files.",
                scope="Read only task/handoff files, group follow-ups by ownership and urgency, and identify which work can be delegated.",
                files=[line.split(":", 1)[0] for line in task_lines[:6]],
                prompt="Review the task-like lines in logs, handoffs, changelog, and memory files. Return a ranked list of follow-ups, blockers, and sub-agent task briefs.",
            )
        )

    if workstream_files:
        candidates.append(
            Candidate(
                title="Split workstreams into parallel execution briefs",
                agent_type="explorer",
                why=f"{len(workstream_files)} workstream file(s) suggest separable tracks of work.",
                scope="Map workstream files to independent implementation, research, verification, or writing tasks.",
                files=workstream_files[:8],
                prompt="Read the workstream files and produce disjoint sub-agent briefs with clear ownership, inputs, expected outputs, and collision risks.",
            )
        )

    if scripts and len(tests) < max(1, len(scripts) // 3):
        candidates.append(
            Candidate(
                title="Expand automated verification coverage",
                agent_type="verifier",
                why=f"{len(scripts)} helper script(s) were found and only {len(tests)} test-like file(s) were visible.",
                scope="Identify high-value behavior tests for scripts, commands, installers, and release packaging.",
                files=scripts[:8] + tests[:4],
                prompt="Inspect helper scripts and existing tests. Recommend or add focused tests for risky behaviors, installer output, and release cleanliness.",
            )
        )

    if counts["documents"] + counts["data"] + counts["code-config"] > 25 and memory_files:
        candidates.append(
            Candidate(
                title="Map project structure into ownership lanes",
                agent_type="explorer",
                why="The project has enough source files and memory files that parallel ownership lanes may reduce coordination load.",
                scope="Create a concise map of folders, likely owners, and safe delegation boundaries.",
                files=memory_files[:6] + first_existing(files, ["AGENTS.md", "project-system/AGENT-HANDOFF.md"]),
                prompt="Inspect the visible folder structure and memory files. Recommend sub-agent ownership lanes with disjoint file scopes and verification expectations.",
            )
        )

    if not candidates:
        candidates.append(
            Candidate(
                title="Run a baseline project scan",
                agent_type="explorer",
                why="No obvious delegation candidates were discovered from the visible memory trail.",
                scope="Perform read-only inventory and identify what context is missing before delegation.",
                files=first_existing(files, ["AGENTS.md", "NEXT-ACTIONS.md", "memory/11-source-index.md"]),
                prompt="Run a read-only project scan and report whether setup, rework, source extraction, or test planning should happen next.",
            )
        )

    return files, task_lines, candidates


def render_markdown(root: Path, files: list[Path], task_lines: list[str], candidates: list[Candidate]) -> str:
    counts = category_counts(files)
    lines = [
        "# Sub-Agent Task Discovery",
        "",
        "Read-only candidate briefs for work that may be safe to delegate or run in parallel. Review ownership and collision risk before spawning sub-agents.",
        "",
        "## Project Signals",
        "",
        f"- Root: `{root}`",
        f"- Visible files scanned: {len(files)}",
        f"- Memory files visible: {len(existing(files, 'memory'))}",
        f"- Workstream files visible: {len(existing(files, 'workstreams'))}",
        f"- Activity/log files visible: {len(existing(files, 'logs'))}",
        f"- Task-like lines found: {len(task_lines)}",
        f"- File categories: {', '.join(f'{key}={value}' for key, value in sorted(counts.items())) if counts else 'none'}",
        "",
        "## Recommended Sub-Agent Tasks",
        "",
    ]
    for index, candidate in enumerate(candidates, start=1):
        unique_files = list(dict.fromkeys(candidate.files))
        lines.extend(
            [
                f"### {index}. {candidate.title}",
                "",
                f"- Agent type: `{candidate.agent_type}`",
                f"- Why: {candidate.why}",
                f"- Scope: {candidate.scope}",
                "- Candidate files:",
            ]
        )
        if unique_files:
            lines.extend(f"  - `{path}`" for path in unique_files[:10])
        else:
            lines.append("  - _No specific files identified._")
        lines.extend(["- Suggested prompt:", "", f"  {candidate.prompt}", ""])

    if task_lines:
        lines.extend(["## Task-Like Lines", ""])
        lines.extend(f"- `{line}`" for line in task_lines)
        lines.append("")

    lines.extend(
        [
            "## Coordination Notes",
            "",
            "- Prefer read-only explorer tasks until ownership is clear.",
            "- Assign workers disjoint file scopes before editing.",
            "- Keep secrets out of task prompts, logs, summaries, and memory updates.",
            "- Have a separate verifier review high-risk packaging, installer, or release changes.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover sub-agent task candidates from project memory and structure.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--max-files", type=int, default=5000)
    parser.add_argument("--output", help="Optional markdown file to write after the user approves saving results.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files, task_lines, candidates = discover(root, max_files=args.max_files)
    markdown = render_markdown(root, files, task_lines, candidates)
    if args.output:
        output = root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(markdown + "\n", encoding="utf-8")
        print(str(output))
    else:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
