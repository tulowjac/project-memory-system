# Release Guide

This package exports into several target-specific plugin layouts. The easiest path is to install the build that matches the tool you actually use.

## Recommended Target Per Tool

- Codex: build `--target codex`
- Claude Code: build `--target claude-code`
- Antigravity: build `--target antigravity`
- Generic/manual agent environments: build `--target portable`

## One Polished Install Path Per Target

### Codex

```bash
python installers/install.py --target codex --dest dist/codex/project-memory-system
```

Expected result:

- `.codex-plugin/plugin.json`
- `commands/`
- `skills/project-memory-system/`
- `scripts/`

### Claude Code

```bash
python installers/install.py --target claude-code --dest dist/claude-code/project-memory-system
```

Expected result:

- `.claude-plugin/plugin.json`
- `commands/`
- `skills/project-memory-system/`
- `scripts/`

### Antigravity

```bash
python installers/install.py --target antigravity --dest dist/antigravity/project-memory-system
```

Expected result:

- `AGENTS.md`
- `ANTIGRAVITY.md`
- `commands/`
- `skills/project-memory-system/`
- `scripts/`

### Portable

```bash
python installers/install.py --target portable --dest dist/portable/project-memory-system
```

Expected result:

- `AGENTS.md`
- `INSTALL.md`
- `commands/`
- `skills/project-memory-system/`
- `scripts/`

## Product Positioning

This is version one of a structured agent workflow. It is intentionally strongest when paired with a careful agent that can inspect, plan, and synthesize responsibly.

The package already provides:

- structure scaffolding
- source extraction
- spreadsheet profiling
- diagram summarization
- source index generation
- memory draft synthesis
- sub-agent task discovery
- safe rework preflight checks

The long-term direction is to keep shifting reliable behavior out of prompts and into stronger tooling without breaking portability.
