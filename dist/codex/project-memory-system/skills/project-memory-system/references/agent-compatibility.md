# Agent Compatibility

## Canonical Rule

Use `AGENTS.md` as the canonical cross-agent entry point when creating a project memory system.

## Pointer Shim Template

```md
# Project Agent Instructions

This project uses `AGENTS.md` as the canonical cross-agent instruction file.

Read `AGENTS.md` first, then follow:

- `project-system/OPERATING-MANUAL.md`
- `project-system/MEMORY-PROTOCOL.md`
- `project-system/AGENT-HANDOFF.md`

Do not treat this file as an independent source of truth.
```

## Common Shim Files

- `CLAUDE.md`
- `CODEX.md`
- `ANTIGRAVITY.md`
- `GEMINI.md`

## Profiles

Store tool-specific usage details in `project-system/agent-profiles/<tool>.md`, not in the pointer shim.
