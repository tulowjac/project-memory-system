---
description: Discover concrete sub-agent task candidates from project structure, memory, logs, and recent work.
---

# Sub-Agent Task Discovery

Use this when a project has enough structure, source material, activity logs, or open work that parallel agents may help.

## Preflight

1. Confirm the current working directory is the intended project root.
2. Run `core/scripts/discover_subagent_tasks.py` if available.
3. Inspect `AGENTS.md`, `NEXT-ACTIONS.md`, `memory/`, `workstreams/`, `logs/`, changelog/release notes, and visible source folders by path and summary only.
4. Do not read, print, summarize, or pass along secret values.

## Plan

State that the default pass is read-only and will produce:

- Project signals that suggest parallelizable work.
- Candidate sub-agent task briefs.
- Suggested agent type: explorer, worker, or verifier.
- Candidate file scope for each task.
- Collision and coordination notes.

Ask for explicit approval before saving a task-discovery artifact or spawning/assigning any agent work.

## Commands

Read-only discovery:

```bash
python core/scripts/discover_subagent_tasks.py .
```

After approval only, save a draft artifact:

```bash
python core/scripts/discover_subagent_tasks.py . --output memory/12-subagent-tasks.md
```

## Task Brief Rules

Each recommended task should include:

- Agent type: explorer, worker, or verifier.
- Why the task is separable.
- File or folder ownership.
- Expected output.
- Collision risks.
- Suggested prompt.

Prefer explorer tasks for unclear ownership, worker tasks for disjoint edits, and verifier tasks for tests, packaging, release checks, or safety review.

## Verification

Verify:

- Discovery did not mutate files unless saving was explicitly approved.
- Candidate tasks have non-overlapping write scopes where possible.
- Secret-like files and values were excluded.
- Worker tasks identify concrete files or folders.
- Verifier tasks identify what must be checked.

## Summary

Return:

```md
## Result
- **Action**: subtasks
- **Status**: success | partial | failed
- **Candidates**: <count>
- **Best First Delegation**: <task title or none>
- **Save Location**: <path or none>
```

## Next Steps

Recommend whether to run one explorer, split workers by file scope, or add a verifier after implementation.
