#!/usr/bin/env python3
"""Detect likely AI-tool plugin installation environments."""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    home = Path.home()
    candidates = {
        "codex_user_skills": home / ".codex" / "skills",
        "codex_plugins": home / ".codex" / "plugins",
        "claude": home / ".claude",
        "claude_plugins": home / ".claude" / "plugins",
        "claude_skills": home / ".claude" / "skills",
        "antigravity": home / ".antigravity",
    }
    result = {
        name: {
            "path": str(path),
            "exists": path.exists(),
            "is_dir": path.is_dir(),
        }
        for name, path in candidates.items()
    }
    result["cwd"] = os.getcwd()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
