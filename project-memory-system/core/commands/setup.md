---
description: Inspect the current folder and propose a cross-agent project memory system before creating files.
---

# Project Memory Setup

Set up a cross-agent project memory system for the current folder.

## Preflight

1. Identify the current working directory and confirm it is the intended project root.
2. Run `core/scripts/inspect_project.py` if available.
3. Check for existing `AGENTS.md`, `CLAUDE.md`, `memory/`, `raw/`, `project-system/`, `logs/`.
4. Check for `.gitignore` and local git status without changing the repo.
5. Do not read or print secret values.

## Plan

Present a setup plan before writing anything. Include:
- Project type guess (academic, software, research, legal, etc.)
- Existing files found at root — categorize as: **project work**, **instructions/requirements**, **reference material**, **course/training material**, **data/corpus**
- Proposed folder structure
- Which files move into `raw/originals/` and which category under `raw/md/` their conversions will go into
- Files to be created
- Whether git initialization is recommended

Ask for explicit approval before mutation.

## Canonical Structure

The root must be clean. ALL source material lives in `raw/`:

```
project-root/
├── AGENTS.md               ← canonical entry point
├── CLAUDE.md               ← pointer only
├── .gitignore
├── memory/                 ← synthesized facts agents read
│   ├── 00-project-overview.md
│   ├── 10-project-brief.md
│   ├── 11-source-index.md  ← index of raw/md/ files
│   └── 12-injection-map.md ← task → file mappings
├── deliverables/           ← agent outputs
├── workstreams/            ← active workstream tracking
├── logs/                   ← session logs
├── project-system/         ← coordination metadata
└── raw/
    ├── md/                 ← converted markdown, organized by category
    │   ├── project/        ← user's own work-in-progress files
    │   ├── instructions/   ← rubric, requirements, specs, style guides
    │   ├── research/       ← bibliography, external sources, references
    │   ├── frameworks/     ← analytical tools, templates, extracted diagrams
    │   └── [other categories as needed: lectures/, textbook/, data/, etc.]
    ├── corpus/             ← large text corpora (grep, don't read whole)
    ├── originals/          ← all original source files (never read directly)
    └── README.md
```

**Category guide** — assign each source file to a category based on what it IS, not where it came from:
| Category | What goes here |
|----------|---------------|
| `project/` | The user's own drafts, notes, designs, plans — the main deliverable |
| `instructions/` | Rubric, requirements, specs, contributing guides, style guides |
| `research/` | Bibliography, external sources, case studies, references |
| `frameworks/` | Analytical tools, templates, worksheets, extracted diagrams |
| `lectures/` | Lecture slides, training materials, course notes |
| `textbook/` | Textbook or reference book chapters |
| `data/` | Datasets, schemas, exports, logs |
| `corpus/` | Large text dumps meant for grep/search, not direct reading |

## Commands

After approval only:

1. **Move all source files and subfolders into `raw/originals/`** — everything at the project root that isn't a memory system file gets moved, not copied.
2. **Convert binaries to markdown** in `raw/md/<category>/`:
   - `.docx` → `python-docx` (`pip3 install python-docx`)
   - `.pptx` → `python-pptx` (`pip3 install python-pptx`)
   - `.pdf` → `pdfplumber` (`pip3 install pdfplumber`)
   - `.drawio`/`.xml` → extract node labels via regex/XML parsing
   - `.html`, `.md`, `.txt` → copy as-is into appropriate category
   - Large corpora → `raw/corpus/` (not `raw/md/`)
   - If a tool is missing, note it and skip — don't block setup
3. **Create `AGENTS.md`** with: project identity, folder map, "how to work" section referencing the injection map, current status table.
4. **Create `CLAUDE.md`** as pointer only.
5. **Create memory files:**
   - `memory/00-project-overview.md` — project type, goal, key people, current status
   - `memory/10-project-brief.md` — deliverable details, locked values, key claims
   - `memory/11-source-index.md` — index of all `raw/md/` files by category
   - `memory/12-injection-map.md` — task → file mappings (see template below)
6. **Create `.gitignore`** excluding binaries and secrets.
7. **Initialize git** only if explicitly approved.

## Injection Map Template

`memory/12-injection-map.md` should follow this pattern (adapt to the project):

```markdown
# Injection Map

## Always Load First
- memory/00-project-overview.md
- memory/10-project-brief.md

## Task → Files to Inject
### [Task name]
- raw/md/[category]/[file.md]
- raw/md/[category]/[file.md]

## Injection Principles
1. Read memory/ first — synthesized facts take priority.
2. Pull by task — load what the task needs, not everything.
3. Project files over reference material — check project/ before lectures/.
4. corpus/ is last resort — grep a specific block, don't read the whole file.
5. Outputs go in deliverables/ — never write into raw/ or memory/.
```

## Verification

- Root contains ONLY: `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `memory/`, `raw/`, `deliverables/`, `workstreams/`, `logs/`, `project-system/`
- All source files moved to `raw/originals/`
- Converted `.md` files in correct `raw/md/<category>/` folders
- `memory/11-source-index.md` indexes all `raw/md/` files
- `memory/12-injection-map.md` maps at least 3–5 common tasks to files
- `AGENTS.md` references the injection map
- No secrets in memory or logs

## Summary

```md
## Result
- **Action**: setup
- **Status**: success | partial | failed
- **Created**: <key folders/files>
- **Moved to raw/originals/**: <count and types>
- **Converted to raw/md/**: <count by category>
- **Skipped**: <file — reason>
```

## Next Steps
- `/scan` to verify the environment
- `/rework` after adding new source files
- `/subtasks` to parallelize project work
