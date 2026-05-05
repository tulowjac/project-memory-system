---
description: Produce a read-only map of the current project memory environment and source files. Checks three-zone raw/ structure, emits structured gap output that /rework can consume directly.
---

# Project Memory Scan

Map the current environment without changing any files. Output is structured so `/rework` can consume it directly.

## Preflight

1. Identify the current working directory.
2. Run `core/scripts/inspect_project.py` if available.
3. Check for existing memory system files and agent compatibility files.
4. Do not open or print secret values.

## Commands

Run read-only inspection only:

### Agent & memory file detection
- Check for `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, `GEMINI.md` at root.
- Check `memory/` for: `00-project-overview.md`, `10-project-brief.md`, `11-source-index.md`, `12-injection-map.md`.
- For each memory file found: report line count and flag obvious staleness (placeholder text like `<TBD>`, `TODO`, or values that contradict content in `raw/md/`).

### Three-zone raw/ structure audit
The canonical structure is:
```
raw/
├── originals/   ← source files (binaries + any received markdown)
├── md/          ← converted markdown, organized by category
│   ├── project/
│   ├── instructions/
│   ├── research/
│   ├── frameworks/
│   └── [other categories: lectures/, textbook/, data/, etc.]
└── corpus/      ← large text corpora (grep-only)
```

Check for structural violations:
- **Misplaced binaries:** `.docx`, `.pdf`, `.pptx`, `.drawio`, `.xlsx` found in `raw/md/` or at `raw/` root → should be in `raw/originals/`
- **Misplaced markdown:** `.md` files found in `raw/originals/` → should be in `raw/md/<category>/`
- **Oversized md/ files:** files >50KB in `raw/md/` that are flat text → consider moving to `raw/corpus/`
- **Uncategorized md/:** markdown files in `raw/md/` root (not in a subcategory) → should be assigned a category
- **Missing zones:** if `raw/originals/`, `raw/md/`, or `raw/corpus/` don't exist yet

### Unconverted binary detection
List all binary source files in `raw/originals/` that have no corresponding `.md` in `raw/md/`. Group by extension.

### Source index coverage gap
Diff every file in `raw/md/` against entries in `memory/11-source-index.md`:
- Files in `raw/md/` NOT in the index → need to be added
- Entries in the index that no longer exist in `raw/md/` → stale entries

### Injection map coverage gap
Check `memory/12-injection-map.md` (if it exists):
- Files in `raw/md/` that appear in no task mapping → potential injection map gap
- Note: not every file needs a dedicated mapping, but flag obvious omissions

### Root cleanliness check
The project root should contain ONLY: `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `memory/`, `raw/`, `deliverables/`, `workstreams/`, `logs/`, `project-system/`.
Flag any source files (binaries, unconverted documents) found at the root.

### Pending rework detection
If a previous `/rework` was proposed but not executed, flag those items explicitly.

Do not move, write, delete, format, or initialize anything.

## Structured Gap Output

Always end the scan report with this machine-readable block that `/rework` can consume directly:

```
## Scan Gap Summary (for /rework)
- missing_originals: [source files at root or outside raw/originals/ that should be moved there]
- unconverted_binaries: [files in raw/originals/ with no raw/md/ counterpart, grouped by extension]
- misplaced_files: [binaries in raw/md/, markdown in raw/originals/, uncategorized md/ root files]
- stale_memory: [memory files with placeholder values or index entries for non-existent files]
- injection_map_gaps: [raw/md/ files not mapped to any task in memory/12-injection-map.md]
- missing_tools: [conversion tools not installed, with pip3 install command]
- pending_rework: [items proposed in a prior /rework but not yet executed]
- workstreams_empty: true | false
- root_clean: true | false
```

## Verification

Confirm no files were changed. If git exists, compare pre/post `git status --short`.

## Summary

```md
## Result
- **Action**: scan
- **Status**: success | partial | failed
- **Project Type Guess**: <academic | software | research | legal | other>
- **Memory Health**: <ready | partial | missing>
- **Raw Structure**: <clean | violations found>
- **Key Risks**: <short list>
```

## Next Steps

- `/rework` — if gaps exist; pass the Scan Gap Summary block as argument for scan-driven mode.
- `/setup` — if no memory system exists.
- `/add-agent` — if tool profiles are missing.
- `/subtasks` — if memory is complete and project work needs to be parallelized.
