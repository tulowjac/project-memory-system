---
name: project-memory-system-rework
description: Reconcile newly added source files with the project memory system. Converts binaries to markdown, places them in the correct raw/md/<category>/ zone, updates source indexes and memory, and keeps the injection map current.
---


# Project Memory Rework

Use this after adding new source files, or after `/scan` has identified gaps.

## Input Modes

**Mode 1 — Scan-driven (preferred):** If `/scan` was just run or its gap summary is passed as an argument, consume that output directly. Do not re-scan. Use the scan's `missing_raw`, `unconverted_binaries`, `misplaced_files`, `stale_memory`, and `missing_tools` lists as the work order.

**Mode 2 — Argument-driven:** If the user passes specific files, folders, or task areas (e.g., `/rework raw/originals/new-report.pdf` or `/rework memory/10-project-brief.md`), scope rework to exactly those targets.

**Mode 3 — Discovery:** If no scan output or arguments are provided, run the preflight below to detect new or changed files.

## Preflight (Mode 3 only)

1. Confirm the project has a memory system. If not, recommend `/setup` and stop.
2. Check for files in `raw/originals/` that have no corresponding file in `raw/md/`.
3. Check for binaries (`.docx`, `.pdf`, `.pptx`, `.drawio`, `.xlsx`) anywhere outside `raw/originals/` or `raw/corpus/` — these are misplaced.
4. Check for markdown files in `raw/originals/` — these should be in `raw/md/<category>/`.
5. Diff `raw/md/` against `memory/11-source-index.md` — flag any `raw/md/` files not indexed.
6. Check memory files for staleness: placeholder text, values that contradict `raw/md/` content.
7. Do not read or print secret values.

## Three-Zone raw/ Structure

Every project must maintain this layout — rework enforces it:

```
raw/
├── originals/          ← ALL original source files live here (never read directly)
│   └── [subfolders or loose files as received]
├── md/                 ← converted markdown, organized by category (READ THESE)
│   ├── project/        ← user's own work: drafts, notes, designs, plans
│   ├── instructions/   ← rubric, requirements, specs, style guides
│   ├── research/       ← bibliography, external sources, references, case studies
│   ├── frameworks/     ← analytical tools, templates, worksheets, diagrams
│   ├── [other categories as needed: lectures/, textbook/, data/, etc.]
└── corpus/             ← large text corpora (grep by block, never read whole)
```

**Category guide** — assign each converted file to a category based on what it IS:

| Category | What goes here |
|----------|----------------|
| `project/` | The user's own drafts, notes, designs, plans — the main deliverable |
| `instructions/` | Rubric, requirements, specs, contributing guides, style guides |
| `research/` | Bibliography, external sources, case studies, references |
| `frameworks/` | Analytical tools, templates, worksheets, extracted diagrams |
| `lectures/` | Lecture slides, training materials, course notes |
| `textbook/` | Textbook or reference book chapters |
| `data/` | Datasets, schemas, exports, logs |
| `corpus/` | Large text dumps meant for grep/search, not direct reading |

## Plan

Before writing anything, propose:

- **New or changed sources:** files in `raw/originals/` without `raw/md/` counterparts, plus any misplaced files.
- **Action per file:** `convert-to-md` | `move-to-correct-category` | `move-to-corpus` | `preserve-only` | `schema-profile`.
- **Target category** for each file that needs conversion.
- **Memory files affected:** which memory files need updates (new index entries, value corrections, injection map additions).
- **Files to skip:** already-converted files, files outside project scope, sensitive data.

If running in scan-driven mode, reference the scan gap summary explicitly (e.g., "Scan identified 3 unconverted binaries in originals/ and 1 misplaced markdown — acting on those now").

Ask for explicit approval before mutation.

## Commands

After approval only:

### 1. Move originals into place
Any source file not already in `raw/originals/` → move it there. Never delete originals.

### 2. Convert to markdown in raw/md/<category>/
Use these tools:
- `.docx` → `python-docx` (`pip3 install python-docx`)
- `.pptx` → `python-pptx` (`pip3 install python-pptx`) — extract slide body text AND speaker notes
- `.pdf` → `pdfplumber` (`pip3 install pdfplumber`) — preferred pure-Python option
- `.drawio` / `.xml` → extract node labels via regex/XML parsing; copy raw XML to frameworks/ too
- `.html`, `.md`, `.txt` → copy as-is into appropriate category
- `.csv` / `.xlsx` → schema-profile only (column names, row counts, value ranges) — never dump full data
- Large corpora (>50KB flat text) → `raw/corpus/` instead of `raw/md/`

If a tool is missing: note it in the summary and skip — do not block rework.

### 3. Fix misplaced files
- Markdown files found in `raw/originals/` → move to correct `raw/md/<category>/`
- Binaries found in `raw/md/` → move to `raw/originals/`
- Large text files in `raw/md/` that should be corpus → move to `raw/corpus/`

### 4. Update memory/11-source-index.md
Add new files to the index under their category with: file path, brief description. Remove entries for files that no longer exist.

### 5. Update memory/12-injection-map.md
For each new file added to `raw/md/`, determine which task(s) it belongs to and add it to the relevant task section. If no injection map exists yet, create one following this template:

```markdown
# Injection Map

## Always Load First
- memory/00-project-overview.md
- memory/10-project-brief.md

## Task → Files to Inject
### [Task name]
- raw/md/[category]/[file.md]

## Injection Principles
1. Read memory/ first — synthesized facts take priority.
2. Pull by task — load what the task needs, not everything.
3. Project files over reference material.
4. corpus/ is last resort — grep a specific block, don't read the whole file.
5. Outputs go in deliverables/ — never write into raw/ or memory/.
```

### 6. Synthesize memory updates
For each affected memory file, extract only durable facts, decisions, locked values, open questions, or strategic opportunities. Do not paste raw content verbatim into memory.

### 7. Write a log entry
`logs/YYYY-MM-DD-rework.md` — what was converted, moved, or updated; what memory changed; open questions.

## Verification

- All original source files are in `raw/originals/` (never deleted).
- All converted markdown is in `raw/md/<category>/` (no markdown in originals/).
- No binaries in `raw/md/` (no .docx/.pdf/.pptx in md/).
- `memory/11-source-index.md` indexes every file in `raw/md/`.
- `memory/12-injection-map.md` maps new files to at least one task.
- Memory files reflect actual current values (no placeholders).
- No secrets logged.

## Summary

```md
## Result
- **Action**: rework
- **Status**: success | partial | failed
- **Mode**: scan-driven | argument-driven | discovery
- **Converted**: <count by category>
- **Moved/fixed**: <misplaced file count>
- **Memory Updated**: <list of memory files changed>
- **Skipped**: <file — reason>
```

## Next Steps

- `/scan` to verify the three-zone structure is clean.
- `/subtasks` if memory is complete and project work needs to be parallelized.
- List any missing tools with the exact `pip3 install` command needed.
