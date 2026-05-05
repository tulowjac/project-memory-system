# Project Memory System

Project Memory System is a portable plugin pack for turning messy project folders into durable, cross-agent working environments.

This is a framework for good agents, not a fully autonomous knowledge engine. It gives the agent a structure, operating rules, extraction tools, and safe workflows so project memory can stay coherent across tools.

## What It Does

- Scaffolds a cross-agent project memory layout
- Keeps `AGENTS.md` canonical across tools
- Uses pointer shims for `CLAUDE.md`, `CODEX.md`, `ANTIGRAVITY.md`, and `GEMINI.md`
- Preserves raw source files while generating extracted markdown and text
- Builds a source index and drafts memory updates from newly added material
- Discovers concrete sub-agent task briefs from structure, memory, logs, and recent work
- Adds basic safety checks before rework so agents do not casually ingest secret-heavy or operational files

## Commands

- `/project-memory-system:setup`
- `/project-memory-system:scan`
- `/project-memory-system:rework`
- `/project-memory-system:add-agent`
- `/project-memory-system:subtasks`

## Package Layout

- `core/commands/`: reusable command prompts
- `core/skills/project-memory-system/`: canonical skill, references, and skill-local script copies
- `core/scripts/`: shared helper scripts used by commands and installers
- `adapters/`: target-specific packaging notes and manifests
- `installers/`: export and environment-detection helpers
- `tests/`: automated checks for installer output and v2 helper-script behavior

## Install

Use the installer for a target-specific build:

```bash
python installers/install.py --target codex --dest dist/codex/project-memory-system
python installers/install.py --target claude-code --dest dist/claude-code/project-memory-system
python installers/install.py --target antigravity --dest dist/antigravity/project-memory-system
python installers/install.py --target portable --dest dist/portable/project-memory-system
```

Dry-run is supported for every target:

```bash
python installers/install.py --target codex --dest dist/codex/project-memory-system --dry-run
```

## Test

Run the automated smoke suite from this package directory:

```bash
python -m pytest tests
```

## Best Current Fit

The strongest use case today is an agent-assisted project where the model follows a disciplined workflow:

1. Inspect the folder safely.
2. Propose a structure or rework plan.
3. Preserve originals.
4. Generate extracted source artifacts.
5. Update source indexes and draft durable memory.

## Safety

Commands default to plan-then-ask before mutation. Secret values must never be read, printed, logged, stored, summarized, or committed.

## Release Notes

See [RELEASE.md](/Users/jacquestulowitzky/Downloads/plugin-export/project-memory-system/RELEASE.md) for the recommended install path per target and packaged output expectations.
