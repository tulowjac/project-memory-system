from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
CORE_SCRIPTS = PACKAGE_ROOT / "core" / "scripts"
SKILL_SCRIPTS = PACKAGE_ROOT / "core" / "skills" / "project-memory-system" / "scripts"
INSTALLER = PACKAGE_ROOT / "installers" / "install.py"


def run_script(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        check=True,
        text=True,
        capture_output=True,
    )


def load_installer():
    spec = importlib.util.spec_from_file_location("project_memory_installer", INSTALLER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_copies_stay_in_sync() -> None:
    root_scripts = {path.name for path in CORE_SCRIPTS.glob("*.py")}
    skill_scripts = {path.name for path in SKILL_SCRIPTS.glob("*.py")}

    assert root_scripts == skill_scripts
    for script_name in sorted(root_scripts):
        assert (CORE_SCRIPTS / script_name).read_bytes() == (SKILL_SCRIPTS / script_name).read_bytes()


def test_generate_source_index_groups_sources_and_skips_secretish_paths(tmp_path: Path) -> None:
    (tmp_path / "raw" / "documents").mkdir(parents=True)
    (tmp_path / "raw" / "data").mkdir(parents=True)
    (tmp_path / "raw" / "extracted" / "markdown").mkdir(parents=True)
    (tmp_path / "raw" / "secrets").mkdir(parents=True)

    (tmp_path / "raw" / "documents" / "brief.md").write_text("Project brief", encoding="utf-8")
    (tmp_path / "raw" / "data" / "accounts.csv").write_text("id,name\n1,Ada\n", encoding="utf-8")
    (tmp_path / "raw" / "extracted" / "markdown" / "brief.md").write_text("- Durable note from extraction\n", encoding="utf-8")
    (tmp_path / "raw" / ".env").write_text("TOKEN=not-for-memory", encoding="utf-8")
    (tmp_path / "raw" / "secrets" / "token.txt").write_text("not-for-memory", encoding="utf-8")

    run_script(CORE_SCRIPTS / "generate_source_index.py", str(tmp_path))

    index = (tmp_path / "memory" / "11-source-index.md").read_text(encoding="utf-8")
    assert "## Raw Evidence" in index
    assert "- `raw/documents/brief.md`" in index
    assert "- `raw/data/accounts.csv`" in index
    assert index.count("raw/extracted/markdown/brief.md") == 1
    assert "## Extracted Sources" in index
    assert ".env" not in index
    assert "secrets/token.txt" not in index


def test_draft_memory_update_summarizes_extracted_markdown(tmp_path: Path) -> None:
    extracted = tmp_path / "raw" / "extracted" / "markdown"
    extracted.mkdir(parents=True)
    (tmp_path / "memory").mkdir()
    (tmp_path / "memory" / "11-source-index.md").write_text("# Source Index\n", encoding="utf-8")
    (extracted / "notes.md").write_text(
        "\n".join(
            [
                "# Notes",
                "- Durable product decision that should be reviewed by the agent",
                "* Durable product decision that should be reviewed by the agent",
                "Short",
                "1. A second durable assumption worth considering for project memory",
            ]
        ),
        encoding="utf-8",
    )

    run_script(CORE_SCRIPTS / "draft_memory_update.py", str(tmp_path))

    draft = (tmp_path / "memory" / "03-discovery-log.md").read_text(encoding="utf-8")
    assert "- Source index present: yes" in draft
    assert "- Extracted markdown files reviewed: 1" in draft
    assert "### `raw/extracted/markdown/notes.md`" in draft
    assert draft.count("Durable product decision that should be reviewed by the agent") == 1
    assert "- A second durable assumption worth considering for project memory" in draft
    assert "Short" not in draft


def test_validate_rework_flags_secrets_and_large_files(tmp_path: Path) -> None:
    (tmp_path / "raw").mkdir()
    (tmp_path / ".env.local").write_text("TOKEN=not-for-memory", encoding="utf-8")
    (tmp_path / "raw" / "archive.sqlite").write_text("not-for-memory", encoding="utf-8")
    large_file = tmp_path / "raw" / "large.bin"
    large_file.write_bytes(b"x" * (10 * 1024 * 1024 + 1))

    result = run_script(CORE_SCRIPTS / "validate_rework.py", str(tmp_path))
    payload = json.loads(result.stdout)

    assert payload["status"] == "attention-needed"
    flagged = {item["path"]: item["reason"] for item in payload["flagged"]}
    assert flagged[".env.local"] == "secret-like path or suffix"
    assert flagged["raw/archive.sqlite"] == "secret-like path or suffix"
    assert flagged["raw/large.bin"].startswith("large file")


def test_discover_subagent_tasks_uses_memory_logs_and_structure(tmp_path: Path) -> None:
    (tmp_path / "raw" / "documents").mkdir(parents=True)
    (tmp_path / "raw" / "extracted" / "markdown").mkdir(parents=True)
    (tmp_path / "logs").mkdir()
    (tmp_path / "memory").mkdir()
    (tmp_path / "workstreams").mkdir()
    (tmp_path / "secrets").mkdir()

    (tmp_path / "raw" / "documents" / "brief.docx").write_bytes(b"placeholder")
    (tmp_path / "raw" / "extracted" / "markdown" / "brief.md").write_text(
        "- Durable fact that should be synthesized later\n",
        encoding="utf-8",
    )
    (tmp_path / "logs" / "agent-activity-log.md").write_text(
        "## 2026-05-05 - Agent\n- Next: add installer tests for the release workflow\n",
        encoding="utf-8",
    )
    (tmp_path / "memory" / "04-open-questions.md").write_text(
        "- Open question: which release targets need deeper smoke tests?\n",
        encoding="utf-8",
    )
    (tmp_path / "workstreams" / "packaging.md").write_text("# Packaging\n", encoding="utf-8")
    (tmp_path / "secrets" / "token.txt").write_text("TOKEN=not-for-memory", encoding="utf-8")

    result = run_script(CORE_SCRIPTS / "discover_subagent_tasks.py", str(tmp_path))
    report = result.stdout

    assert "# Sub-Agent Task Discovery" in report
    assert "Review raw-to-extracted coverage" in report
    assert "Synthesize durable memory updates" in report
    assert "Triage next actions and handoff notes" in report
    assert "Split workstreams into parallel execution briefs" in report
    assert "logs/agent-activity-log.md" in report
    assert "secrets/token.txt" not in report


@pytest.mark.parametrize("target", ["codex", "claude-code", "antigravity", "portable"])
def test_installer_exports_valid_target_layouts(target: str, tmp_path: Path) -> None:
    dest = tmp_path / target / "project-memory-system"

    run_script(INSTALLER, "--target", target, "--dest", str(dest))

    assert (dest / "README.md").exists()
    assert (dest / "RELEASE.md").exists()
    assert (dest / "INSTALL.md").exists()
    assert (dest / "commands" / "setup.md").exists()
    assert (dest / "commands" / "subtasks.md").exists()
    assert (dest / "skills" / "project-memory-system" / "SKILL.md").exists()
    for script_name in [
        "generate_source_index.py",
        "draft_memory_update.py",
        "validate_rework.py",
        "discover_subagent_tasks.py",
    ]:
        assert (dest / "scripts" / script_name).exists()
        assert (dest / "skills" / "project-memory-system" / "scripts" / script_name).exists()

    if target == "codex":
        assert (dest / ".codex-plugin" / "plugin.json").exists()
        assert "/project-memory-system:setup" in (dest / "README.md").read_text(encoding="utf-8")
        assert "/project-memory-system:scan" in (dest / "commands" / "setup.md").read_text(encoding="utf-8")
        assert "`/setup`" not in (dest / "README.md").read_text(encoding="utf-8")
    if target == "claude-code":
        assert (dest / ".claude-plugin" / "plugin.json").exists()
        assert not (dest / "plugin.json").exists()
        assert "`/setup`" in (dest / "README.md").read_text(encoding="utf-8")
    if target in {"antigravity", "portable"}:
        assert (dest / "AGENTS.md").exists()


def test_copy_tree_skips_python_cache_files(tmp_path: Path) -> None:
    installer = load_installer()
    src = tmp_path / "src"
    dest = tmp_path / "dest"
    (src / "nested" / "__pycache__").mkdir(parents=True)
    (src / "nested" / "keep.py").write_text("print('ok')\n", encoding="utf-8")
    (src / "nested" / "__pycache__" / "skip.pyc").write_bytes(b"compiled")
    (src / "nested" / "skip.pyc").write_bytes(b"compiled")
    actions: list[str] = []

    installer.copy_tree(src, dest, force=False, dry_run=False, actions=actions)

    assert (dest / "nested" / "keep.py").exists()
    assert not (dest / "nested" / "__pycache__" / "skip.pyc").exists()
    assert not (dest / "nested" / "skip.pyc").exists()
