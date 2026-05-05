---
description: Add or update an AI tool/agent profile without duplicating canonical project instructions.
---

# Add Agent Profile

Record how another AI tool, model, or agent should work inside this project.

## Preflight

1. Read canonical `AGENTS.md` if present.
2. Read `project-system/AGENT-HANDOFF.md` if present.
3. Check for existing agent profile files.
4. Do not overwrite tool-specific files without approval.

## Plan

Ask for or infer:

- Tool name.
- Models commonly used.
- Where it runs.
- Strengths and constraints.
- Available skills/plugins.
- Preferred use cases.
- Any special permissions or safety rules.

Propose a profile location and any compatibility pointer file before writing.

## Commands

After approval only:

1. Add/update `project-system/agent-profiles/<tool-name>.md`.
2. Create a pointer-only compatibility file if appropriate.
3. Update `project-system/AGENT-HANDOFF.md` if workflow coordination changes.
4. Keep `AGENTS.md` canonical.

## Verification

Verify:

- The new profile exists.
- No canonical instructions were duplicated into pointer files.
- Agent-specific rules do not conflict with global project rules.

## Summary

Return:

```md
## Result
- **Action**: add-agent
- **Status**: success | partial | failed
- **Agent Profile**: <path>
- **Compatibility File**: <path or none>
```

## Next Steps

Suggest `/scan` to verify the project environment or `/rework` if new tool outputs have been added.
