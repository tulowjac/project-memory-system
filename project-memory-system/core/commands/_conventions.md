# Command Conventions

Every command is plan-first.

## Required Pattern

1. Preflight with read-only inspection.
2. Present a plan.
3. Ask for explicit approval before mutation.
4. Execute only approved changes.
5. Verify state.
6. Summarize outcome and next steps.

## Safety Rules

- Never read, print, log, store, summarize, or commit secret values.
- Never overwrite existing non-empty files without approval.
- Prefer structure-level extraction for spreadsheets and operational datasets.
- Keep `AGENTS.md` canonical.
- Keep compatibility files pointer-only unless a target tool requires otherwise.
