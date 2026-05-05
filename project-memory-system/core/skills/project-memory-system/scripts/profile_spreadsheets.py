#!/usr/bin/env python3
"""Create compact schema-level markdown for XLSX/CSV data sources."""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-") or "file"


def clean(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def table(rows: list[list]) -> list[str]:
    if not rows:
        return ["_None._"]
    width = len(rows[0])
    out = ["| " + " | ".join(str(x).replace("|", "\\|") for x in rows[0]) + " |"]
    out.append("| " + " | ".join(["---"] * width) + " |")
    for row in rows[1:]:
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
    return out


def trim(rows: list[list[str]]) -> list[list[str]]:
    rows = [[clean(cell) for cell in row] for row in rows]
    while rows and not any(rows[-1]):
        rows.pop()
    if not rows:
        return []
    max_cols = max(len(row) for row in rows)
    rows = [row + [""] * (max_cols - len(row)) for row in rows]
    last_col = max((i for i in range(max_cols) if any(row[i] for row in rows)), default=-1)
    return [row[: last_col + 1] for row in rows] if last_col >= 0 else []


def header_score(row: list[str]) -> int:
    vals = [v for v in row if v]
    if not vals:
        return -1
    alpha = sum(any(ch.isalpha() for ch in v) for v in vals)
    return alpha * 3 + len(set(vals)) + min(len(vals), 20)


def profile(sheet_name: str, rows: list[list[str]]) -> dict:
    rows = trim(rows)
    if not rows:
        return {"sheet": sheet_name, "header_row": None, "rows": 0, "cols": 0, "columns": []}
    scan = rows[:15]
    header_i = max(range(len(scan)), key=lambda i: header_score(scan[i]))
    header = scan[header_i]
    first = next((i for i, value in enumerate(header) if value), 0)
    if first:
        rows = [row[first:] for row in rows]
        header = header[first:]
    columns = [(i + 1, col) for i, col in enumerate(header) if col]
    return {
        "sheet": sheet_name,
        "header_row": header_i + 1,
        "rows": max(len(rows) - header_i - 1, 0),
        "cols": len(header),
        "columns": columns,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Profile XLSX/CSV files into compact markdown schemas.")
    parser.add_argument("inputs", nargs="+", help="Spreadsheet/CSV files")
    parser.add_argument("--markdown-dir", default="raw/extracted/markdown/database")
    parser.add_argument("--text-dir", default="raw/extracted/text/database")
    args = parser.parse_args()

    md_dir = Path(args.markdown_dir)
    txt_dir = Path(args.text_dir)
    md_dir.mkdir(parents=True, exist_ok=True)
    txt_dir.mkdir(parents=True, exist_ok=True)

    index_rows = [["Source file", "Sheets/tables", "Extracted markdown"]]
    for raw in args.inputs:
        path = Path(raw)
        profiles = []
        if path.suffix.lower() == ".xlsx":
            try:
                import openpyxl
            except ImportError as exc:
                raise SystemExit("openpyxl is required for XLSX profiling") from exc
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            for ws in wb.worksheets:
                rows = [[cell for cell in row] for row in ws.iter_rows(values_only=True)]
                profiles.append(profile(ws.title, rows))
        elif path.suffix.lower() in [".csv", ".tsv"]:
            dialect = "excel-tab" if path.suffix.lower() == ".tsv" else "excel"
            with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
                profiles.append(profile(path.stem, list(csv.reader(handle, dialect=dialect))))
        else:
            continue

        base = slug(path.name)
        md_path = md_dir / f"{base}.md"
        lines = [
            f"# Database Structure: {path.name}",
            "",
            f"Original file: `{path}`",
            "",
            "This is a structure-level extraction. Use the original raw file for examples or record-level validation.",
            "",
            "## Tables / Sheets",
            "",
        ]
        lines.extend(table([["Sheet/table", "Header row", "Data rows", "Columns"]] + [[p["sheet"], p["header_row"] or "", p["rows"], p["cols"]] for p in profiles]))
        lines.append("")
        for p in profiles:
            lines.extend([f"## {p['sheet']}", "", f"Header row detected: {p['header_row'] or 'not detected'}", "", f"Approximate data rows: {p['rows']}", "", "### Columns", ""])
            lines.extend(table([["#", "Column"]] + [[i, col] for i, col in p["columns"]]))
            lines.append("")
        text = "\n".join(lines).rstrip() + "\n"
        md_path.write_text(text, encoding="utf-8")
        (txt_dir / f"{base}.txt").write_text(re.sub(r"[#|`*_]", "", text), encoding="utf-8")
        index_rows.append([str(path), ", ".join(p["sheet"] for p in profiles), str(md_path)])

    index = ["# Database Structure Index", "", "Raw files remain the source for record-level examples.", ""]
    index.extend(table(index_rows))
    (md_dir / "_database-structure-index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(str(md_dir / "_database-structure-index.md"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
