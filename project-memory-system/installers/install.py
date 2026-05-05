#!/usr/bin/env python3
"""Install project-memory-system into Codex, Claude Code, Antigravity, or portable layouts."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

TARGETS = {"codex", "claude-code", "antigravity", "portable"}
COMMANDS = ["setup.md", "scan.md", "rework.md", "add-agent.md", "subtasks.md", "map.md", "find.md"]
CODEX_COMMAND_NAMES = {
    "/setup": "/project-memory-system:setup",
    "/scan": "/project-memory-system:scan",
    "/rework": "/project-memory-system:rework",
    "/add-agent": "/project-memory-system:add-agent",
    "/subtasks": "/project-memory-system:subtasks",
    "/map": "/project-memory-system:map",
    "/find": "/project-memory-system:find",
}
# Commands packaged as Codex skills (Codex Desktop indexes skills/, not commands/)
CODEX_SKILL_COMMANDS = ["setup", "scan", "rework", "add-agent", "subtasks", "map", "find"]
SCRIPT_NAMES = [
    "inspect_project.py",
    "extract_docx.py",
    "profile_spreadsheets.py",
    "summarize_diagram_source.py",
    "scaffold_memory_system.py",
    "generate_source_index.py",
    "draft_memory_update.py",
    "validate_rework.py",
    "discover_subagent_tasks.py",
]


def package_root() -> Path:
    return Path(__file__).resolve().parents[1]


def copy_file(src: Path, dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    if dest.exists() and not force:
        actions.append(f"skip existing {dest}")
        return
    actions.append(f"{'would copy' if dry_run else 'copy'} {src} -> {dest}")
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def copy_tree(src: Path, dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    for path in src.rglob("*"):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_file():
            rel = path.relative_to(src)
            copy_file(path, dest / rel, force, dry_run, actions)


def write_json(path: Path, data: dict, force: bool, dry_run: bool, actions: list[str]) -> None:
    if path.exists() and not force:
        actions.append(f"skip existing {path}")
        return
    actions.append(f"{'would write' if dry_run else 'write'} {path}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str, force: bool, dry_run: bool, actions: list[str]) -> None:
    if path.exists() and not force:
        actions.append(f"skip existing {path}")
        return
    actions.append(f"{'would write' if dry_run else 'write'} {path}")
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def target_install_text(target: str) -> str:
    if target == "codex":
        return """# Install

This build is packaged for Codex.

Expected entry points:

- `.codex-plugin/plugin.json`
- `commands/` (reference only — Codex Desktop does not index these)
- `skills/project-memory-system/` (overview skill)
- `skills/project-memory-system-<cmd>/` (one skill per command workflow)
- `scripts/`

Recommended first prompt:

- Set up this folder as a cross-agent project memory system

Codex surfaces each command as a namespaced skill in the picker:

- `$project-memory-system-setup`
- `$project-memory-system-scan`
- `$project-memory-system-rework`
- `$project-memory-system-add-agent`
- `$project-memory-system-subtasks`
- `$project-memory-system-map`
- `$project-memory-system-find`
"""
    if target == "claude-code":
        return """# Install

This build is packaged for Claude Code.

Expected entry points:

- `.claude-plugin/plugin.json`
- `commands/`
- `skills/project-memory-system/`
- `scripts/`

Recommended first prompt:

- Set up this folder as a cross-agent project memory system
"""
    if target == "antigravity":
        return """# Install

This build is packaged for Antigravity.

Start from `AGENTS.md`, then use the command markdown files in `commands/`.
"""
    return """# Install

This build is a portable project-memory package for tools without a native plugin manifest.

Start from `AGENTS.md`, then use the command markdown files in `commands/`.
"""


def install_common(dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    root = package_root()
    for command in COMMANDS:
        copy_file(root / "core" / "commands" / command, dest / "commands" / command, force, dry_run, actions)
    copy_tree(root / "core" / "skills", dest / "skills", force, dry_run, actions)
    copy_tree(root / "core" / "scripts", dest / "scripts", force, dry_run, actions)
    copy_file(root / "README.md", dest / "README.md", force, dry_run, actions)
    copy_file(root / "RELEASE.md", dest / "RELEASE.md", force, dry_run, actions)


def namespace_codex_commands(dest: Path, dry_run: bool, actions: list[str]) -> None:
    paths = [dest / "README.md", *(dest / "commands").glob("*.md")]
    for path in paths:
        if not path.exists():
            continue
        actions.append(f"{'would namespace' if dry_run else 'namespace'} Codex command refs in {path}")
        if dry_run:
            continue
        text = path.read_text(encoding="utf-8")
        for bare, namespaced in CODEX_COMMAND_NAMES.items():
            text = text.replace(f"`{bare}`", f"`{namespaced}`")
        path.write_text(text, encoding="utf-8")


def codex_manifest() -> dict:
    return {
        "name": "project-memory-system",
        "version": "0.1.0",
        "description": "Portable multi-agent project memory setup, scanning, rework, subtask discovery, and agent profile workflows.",
        "author": {"name": "Jacques Tulowitzky"},
        "license": "MIT",
        "keywords": ["agents", "memory", "project-setup", "knowledge-base", "slash-commands"],
        "skills": "./skills/",
        "interface": {
            "displayName": "Project Memory System",
            "shortDescription": "Structure folders into portable multi-agent memory systems.",
            "longDescription": "Creates and maintains cross-tool project memory environments for Codex, Claude Code, Antigravity, and portable AI-agent workflows.",
            "developerName": "Jacques Tulowitzky",
            "category": "Productivity",
            "capabilities": ["Interactive", "Write"],
            "defaultPrompt": [
                "Set up this folder as a cross-agent project memory system",
                "Scan this project memory environment",
                "Rework memory after I added new raw data",
                "Discover useful sub-agent tasks for this project",
            ],
        },
    }


def claude_manifest() -> dict:
    return {
        "name": "project-memory-system",
        "version": "0.1.0",
        "description": "Cross-agent project memory setup, scan, rework, subtask discovery, and agent profile commands.",
        "author": {"name": "Jacques Tulowitzky"},
    }


def install_codex_skills(dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    """Create a namespaced skill folder for each command workflow (Codex indexes skills, not commands/)."""
    root = package_root()
    display_names = {
        "setup": "Project Memory System: Setup",
        "scan": "Project Memory System: Scan",
        "rework": "Project Memory System: Rework Sources",
        "add-agent": "Project Memory System: Add Agent Profile",
        "subtasks": "Project Memory System: Subtasks",
        "map": "Project Memory System: Map",
        "find": "Project Memory System: Find",
    }
    short_descs = {
        "setup": "Initialize a project folder as a cross-agent memory system",
        "scan": "Read-only map of the project memory environment and source files",
        "rework": "Reconcile newly added source files and update project memory",
        "add-agent": "Add an agent or tool compatibility profile to the project",
        "subtasks": "Discover parallelizable sub-agent task candidates",
        "map": "Render a visual tree of the project folder structure in chat",
        "find": "Find files by semantic description and return file paths",
    }
    for cmd in CODEX_SKILL_COMMANDS:
        skill_id = f"project-memory-system-{cmd}"
        skill_dir = dest / "skills" / skill_id
        cmd_src = root / "core" / "commands" / f"{cmd}.md"
        if not cmd_src.exists():
            actions.append(f"warning: source command not found {cmd_src}")
            continue
        cmd_text = cmd_src.read_text(encoding="utf-8")
        # Extract description from frontmatter
        parts = cmd_text.split("---", 2)
        orig_desc = ""
        if len(parts) >= 2:
            for line in parts[1].splitlines():
                if line.startswith("description:"):
                    orig_desc = line[len("description:"):].strip()
                    break
        body = parts[2].lstrip("\n") if len(parts) >= 3 else cmd_text
        skill_md = f"---\nname: {skill_id}\ndescription: {orig_desc}\n---\n\n{body}"
        openai_yaml = (
            f'display_name: "{display_names[cmd]}"\n'
            f'short_description: "{short_descs[cmd]}"\n'
            f"default_prompt:\n"
            f'  - "Use ${skill_id} for this project memory workflow"\n'
        )
        write_text(skill_dir / "SKILL.md", skill_md, force, dry_run, actions)
        write_text(skill_dir / "agents" / "openai.yaml", openai_yaml, force, dry_run, actions)


def install_codex(dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    install_common(dest, force, dry_run, actions)
    install_codex_skills(dest, force, dry_run, actions)
    namespace_codex_commands(dest, dry_run, actions)
    write_json(dest / ".codex-plugin" / "plugin.json", codex_manifest(), force, dry_run, actions)
    write_text(dest / "INSTALL.md", target_install_text("codex"), force, dry_run, actions)


def install_claude(dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    install_common(dest, force, dry_run, actions)
    write_json(dest / ".claude-plugin" / "plugin.json", claude_manifest(), force, dry_run, actions)
    write_text(dest / "INSTALL.md", target_install_text("claude-code"), force, dry_run, actions)


def install_antigravity(dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    install_common(dest, force, dry_run, actions)
    write_text(dest / "AGENTS.md", "Read `skills/project-memory-system/SKILL.md` and use `commands/` for slash-command style workflows.\n", force, dry_run, actions)
    write_text(dest / "ANTIGRAVITY.md", "This pack uses `AGENTS.md` as its portable entry point.\n", force, dry_run, actions)
    write_text(dest / "INSTALL.md", target_install_text("antigravity"), force, dry_run, actions)


def install_portable(dest: Path, force: bool, dry_run: bool, actions: list[str]) -> None:
    install_common(dest, force, dry_run, actions)
    write_text(dest / "AGENTS.md", "Portable Project Memory System pack. Read `skills/project-memory-system/SKILL.md`; command prompts live in `commands/`.\n", force, dry_run, actions)
    write_text(dest / "INSTALL.md", target_install_text("portable"), force, dry_run, actions)


def validate(dest: Path, target: str) -> list[str]:
    errors: list[str] = []
    for command in COMMANDS:
        path = dest / "commands" / command
        if not path.exists():
            errors.append(f"missing command {path}")
        elif "description:" not in path.read_text(encoding="utf-8", errors="replace").split("---", 2)[1]:
            errors.append(f"missing command description {path}")
    skill = dest / "skills" / "project-memory-system" / "SKILL.md"
    if not skill.exists():
        errors.append(f"missing skill {skill}")
    else:
        text = skill.read_text(encoding="utf-8", errors="replace")
        if "name: project-memory-system" not in text or "description:" not in text:
            errors.append(f"invalid skill frontmatter {skill}")
    if target == "codex" and not (dest / ".codex-plugin" / "plugin.json").exists():
        errors.append("missing Codex plugin manifest")
    if target == "codex":
        for cmd in CODEX_SKILL_COMMANDS:
            skill_id = f"project-memory-system-{cmd}"
            skill_md = dest / "skills" / skill_id / "SKILL.md"
            openai_yaml = dest / "skills" / skill_id / "agents" / "openai.yaml"
            if not skill_md.exists():
                errors.append(f"missing Codex command skill {skill_md}")
            elif f"name: {skill_id}" not in skill_md.read_text(encoding="utf-8", errors="replace"):
                errors.append(f"incorrect skill name frontmatter in {skill_md}")
            if not openai_yaml.exists():
                errors.append(f"missing Codex skill display metadata {openai_yaml}")
    if target == "claude-code" and not (dest / ".claude-plugin" / "plugin.json").exists():
        errors.append("missing Claude plugin manifest")
    for script in SCRIPT_NAMES:
        if not (dest / "scripts" / script).exists():
            errors.append(f"missing root script {script}")
        if not (dest / "skills" / "project-memory-system" / "scripts" / script).exists():
            errors.append(f"missing skill script {script}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Install project-memory-system adapter.")
    parser.add_argument("--target", required=True, choices=sorted(TARGETS))
    parser.add_argument("--dest", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    dest = Path(args.dest).resolve()
    actions: list[str] = []
    installers = {
        "codex": install_codex,
        "claude-code": install_claude,
        "antigravity": install_antigravity,
        "portable": install_portable,
    }
    installers[args.target](dest, args.force, args.dry_run, actions)
    print("\n".join(actions))
    if args.dry_run:
        return 0
    errors = validate(dest, args.target)
    if errors:
        print("\nValidation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"\nInstalled project-memory-system for {args.target} at {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
