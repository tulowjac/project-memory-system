---
description: Find files in the project by semantic description. Returns ranked file paths in chat. Read-only.
---

# Project Find

Locate files in the project using natural language. The query is interpreted semantically — match by name, type, purpose, topic, or memory reference — and ranked results are returned as clickable file paths in chat. Read-only.

## Arguments

Required: a natural language query describing what you are looking for.

Examples:
- `/find the client brief`
- `/find spreadsheets with pricing`
- `/find notes from the kickoff meeting`
- `/find the most recent log`
- `/find memory files about competitors`
- `/find anything related to budget`

## Preflight

1. Identify the project root.
2. Read `memory/11-source-index.md` if it exists — this is the primary lookup index.
3. Read `AGENTS.md` and `memory/00-project-overview.md` if they exist, for project context.
4. Do not open binary files. Do not print secret values.

## Search Strategy

Run these passes in order. Stop when you have at least 3 high-confidence matches, or exhaust all passes.

**Pass 1 — Source index lookup.**
Scan `memory/11-source-index.md` for entries whose path, type, or description matches the query. This is fastest and most reliable when the index is populated.

**Pass 2 — Memory file scan.**
Read each file in `memory/` line by line. Look for filenames, paths, or topic descriptions that match the query. Extract matching lines and note the source file.

**Pass 3 — Filename pattern match.**
List all files under the project root. Match filenames against the query by:
- Exact or partial name match (e.g., "brief" matches `client-brief.docx`).
- Extension match if the query specifies a type (e.g., "spreadsheets" matches `.csv`, `.xlsx`).
- Recency match if the query specifies time (e.g., "most recent log" → sort `logs/` by name descending).

**Pass 4 — Generative inference.**
If no strong matches emerged from passes 1–3, reason about where the file is likely to be based on project context and the query. Generate candidate paths and state confidence explicitly. Do not invent paths that do not exist.

## Output Format

Return results as a ranked list. For each result:

- File path (relative to project root), formatted so the agent can open it.
- Match reason: one short phrase explaining why this file matches (e.g., "listed in source-index as 'client brief'", "filename contains 'budget'", "memory/20-frameworks.md references this path").
- Confidence: high | medium | low.

**Example output:**

```
## Find Results: "the client brief"

1. `raw/client-brief.md` — source-index entry: "converted from client-brief.docx" [high]
2. `raw/client-brief.docx` — original binary, not yet converted [high]
3. `memory/10-project-brief.md` — memory synthesis of brief content [medium]

3 results. Use /map raw/ to see surrounding files.
```

If no matches are found:

```
## Find Results: "<query>"

No files matched. Suggestions:
- Run /scan to check if source material has been indexed.
- Try /map to browse the folder structure manually.
- Run /rework if new files have been added but not yet processed.
```

## Verification

Confirm no files were changed or opened beyond metadata and index reads.

## Summary

```md
## Result
- **Action**: find
- **Query**: <query>
- **Status**: success | no results | partial
- **Matches**: <count>
- **Source**: source-index | memory | filename | inferred
```

## Next Steps

- Open a result by asking the agent to read or summarize the file.
- `/map <folder>` — browse the folder containing a result.
- `/rework <path>` — process an unindexed file found during search.
- `/scan` — if the index appears incomplete.
