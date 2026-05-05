---
name: project-memory-system
description: Build and maintain portable multi-agent project memory systems. Use when a user asks to set up a folder for Claude, Codex, Antigravity, Gemini, or other agents; create AGENTS.md/CLAUDE.md/CODEX.md compatibility files; organize raw source files; convert DOCX/PDF/spreadsheet/CSV/diagram inputs into markdown; scan or rework a project knowledge base; discover sub-agent tasks; add agent profiles; create/update durable project memory from messy folders; visualize folder structure with /map; or find files by semantic description with /find.
---

# Project Memory System

Use this skill to turn an unstructured project folder into a durable, cross-agent project environment.

## Core Workflow

1. Inspect before asking. Identify folder shape, source files, existing agent files, memory files, git state, and obvious risks.
2. Separate the three memory layers:
   - Raw evidence: original files, preserved.
   - Extracted source layer: markdown/text/schema maps derived from originals.
   - Synthesized memory: durable facts, decisions, assumptions, questions, opportunities, and next actions.
3. Keep `AGENTS.md` canonical when creating project instructions.
4. Create tool-specific files such as `CLAUDE.md`, `CODEX.md`, `ANTIGRAVITY.md`, and `GEMINI.md` as pointer-only shims unless a tool requires otherwise.
5. Plan before mutation. For setup and rework, propose changes and ask for approval before writing or moving files.
6. Log meaningful work in `logs/agent-activity-log.md` and add handoff notes when another agent may continue.

## Default Folder Model

Use this model as a starting point, then adapt to the project:

```text
AGENTS.md
CLAUDE.md
CODEX.md
ANTIGRAVITY.md
GEMINI.md
NEXT-ACTIONS.md
project-system/
memory/
raw/
workstreams/
deliverables/
logs/
```

## Extraction Defaults

- DOCX: extract headings, paragraphs, and simple tables into markdown/text.
- PDF: extract text when useful; preserve originals.
- XLSX/CSV: create schema-level markdown by default. Do not duplicate full operational datasets unless the user explicitly asks.
- Draw.io/XML diagrams: extract labels and process structure when possible.
- Images: summarize only when visual content matters and image inspection is available.

## Memory Defaults

Create memory files only when they add durable value:

```text
memory/00-project-brief.md
memory/01-current-state.md
memory/02-stakeholders.md
memory/03-discovery-log.md
memory/04-open-questions.md
memory/05-assumptions.md
memory/06-decisions.md
memory/07-opportunities.md
memory/08-workstream-primary.md
memory/09-systems-and-data.md
memory/10-language-and-style.md
memory/11-source-index.md
```

## Secret Handling

Never read, print, summarize, store, log, or commit secret values. It is acceptable to use credentials through environment variables or ignored local secret files, but only by name/path and never by value.

## Bundled Resources

- Use `scripts/inspect_project.py` to inventory a folder.
- Use `scripts/extract_docx.py` for DOCX extraction when Python dependencies are available.
- Use `scripts/profile_spreadsheets.py` for schema-level spreadsheet/CSV profiling.
- Use `scripts/summarize_diagram_source.py` for Draw.io/XML diagram summaries.
- Use `scripts/scaffold_memory_system.py` to create approved scaffolds without overwriting.
- Use `scripts/generate_source_index.py` to build or refresh `memory/11-source-index.md`.
- Use `scripts/draft_memory_update.py` to draft durable memory updates from inspected or extracted sources.
- Use `scripts/validate_rework.py` before mutation to flag secret-heavy, oversized, or operational files that should not be casually ingested.
- Use `scripts/discover_subagent_tasks.py` to recommend explorer, worker, and verifier task briefs from file structure, memory, logs, handoffs, changelog/release notes, and workstreams.
- Read `references/folder-patterns.md` when choosing a project structure.
- Read `references/memory-templates.md` when drafting memory files.
- Read `references/agent-compatibility.md` when adding agent/tool shims.
- Read `references/secret-handling.md` before handling API keys or env files.
