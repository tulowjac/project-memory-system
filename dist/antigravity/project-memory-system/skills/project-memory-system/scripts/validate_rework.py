#!/usr/bin/env python3
"""Flag risky rework inputs before extraction or memory updates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

SECRET_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".env.development",
}
SECRET_PARTS = {"secrets", "credentials", "api-keys", "tokens", ".git"}
LARGE_FILE_BYTES = 10 * 1024 * 1024
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".sqlite", ".db"}


def is_secretish(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if path.name in SECRET_NAMES or path.name.startswith(".env."):
        return True
    if path.suffix.lower() in SENSITIVE_SUFFIXES:
        return True
    return bool(lowered_parts & SECRET_PARTS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate visible files before rework.")
    parser.add_argument("root", nargs="?", default=".")
    parser.add_argument("--limit", type=int, default=2000)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    flagged: list[dict[str, str]] = []
    scanned = 0
    for path in sorted(root.rglob("*")):
        if scanned >= args.limit:
            break
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        scanned += 1
        if is_secretish(rel):
            flagged.append({"path": str(rel), "reason": "secret-like path or suffix"})
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > LARGE_FILE_BYTES:
            flagged.append({"path": str(rel), "reason": f"large file ({size} bytes)"})

    result = {
        "root": str(root),
        "scanned_files": scanned,
        "flagged_count": len(flagged),
        "status": "attention-needed" if flagged else "ok",
        "flagged": flagged[:100],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
