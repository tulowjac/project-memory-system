---
description: Render a visual tree of the project folder structure in chat. Read-only. Accepts optional depth and path arguments.
---

# Project Map

Render a visual tree of the current project folder structure directly in chat. Read-only — no files are created or changed.

## Arguments

- No arguments: tree from the project root, depth 3.
- `/map <path>`: tree rooted at `<path>` (e.g., `/map raw/` or `/map memory/`).
- `/map <depth>`: integer controls tree depth (e.g., `/map 2` or `/map 5`).
- `/map <path> <depth>`: both (e.g., `/map raw/ 4`).

## Preflight

1. Identify the project root (look for `AGENTS.md`, `memory/`, or `.git`).
2. Resolve the target path and depth from arguments (default: root, depth 3).
3. Do not open file contents. Do not print secret values.

## Rendering Rules

Produce an ASCII tree in a fenced code block. Follow these rules:

- Show folders first, then files, alphabetically within each group.
- Use `├──` for non-last entries and `└──` for last entries, with `│   ` indent for non-last parents and `    ` for last parents.
- At the depth limit, if a folder has children, append `  (N items)` after the folder name instead of expanding it.
- Collapse `__pycache__`, `.git`, `.pytest_cache`, `node_modules`, and `.DS_Store` — omit them entirely.
- Flag memory system folders with a short inline label:
  - `memory/` → `# synthesized memory`
  - `raw/` → `# source material`
  - `workstreams/` → `# active workstreams`
  - `logs/` → `# session logs`
  - `deliverables/` → `# outputs`
  - `project-system/` → `# agent coordination`
- If a file has a known role, append a brief inline label:
  - `AGENTS.md` → `# canonical entry point`
  - `CLAUDE.md`, `CODEX.md`, `GEMINI.md` → `# pointer only`
  - `memory/11-source-index.md` → `# source index`
  - `memory/00-project-overview.md` → `# overview`

**Example output:**

```
project-root/
├── AGENTS.md               # canonical entry point
├── CLAUDE.md               # pointer only
├── .gitignore
├── memory/                 # synthesized memory
│   ├── 00-project-overview.md  # overview
│   ├── 11-source-index.md      # source index
│   └── 20-frameworks.md
├── raw/                    # source material
│   ├── brief.md
│   ├── deck.pptx
│   └── data/  (3 items)
├── deliverables/           # outputs
├── logs/                   # session logs
└── workstreams/            # active workstreams
```

After the tree, append a one-line health note:

- If `memory/` is missing: `⚠ No memory system found — run /setup to initialize.`
- If `raw/` is empty or missing: `⚠ No source material in raw/ — add files and run /rework.`
- If the tree looks healthy: `✓ Memory system present. Run /scan to check coverage.`

## Verification

Confirm no files were changed.

## Summary

```md
## Result
- **Action**: map
- **Path**: <root or argument path>
- **Depth**: <depth used>
- **Status**: success | partial | failed
```

## Next Steps

- `/map <path>` — zoom into a subfolder.
- `/find <query>` — locate a specific file by description.
- `/scan` — check memory coverage and gaps.
