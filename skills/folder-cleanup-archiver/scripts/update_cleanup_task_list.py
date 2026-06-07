#!/usr/bin/env python3
"""Create or update cleanup task-list CSV/Markdown files."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


FIELDS = [
    "id",
    "priority",
    "item",
    "baseline_size",
    "current_status",
    "current_size",
    "cleaned_or_consolidated_size",
    "next_action",
    "evidence",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def upsert(rows: list[dict[str, str]], args: argparse.Namespace) -> None:
    new_row = {
        "id": args.id,
        "priority": args.priority,
        "item": args.item,
        "baseline_size": args.baseline_size,
        "current_status": args.status,
        "current_size": args.current_size,
        "cleaned_or_consolidated_size": args.cleaned_size,
        "next_action": args.next_action,
        "evidence": args.evidence,
    }
    for i, row in enumerate(rows):
        if row.get("id") == args.id:
            rows[i] = {**row, **{k: v for k, v in new_row.items() if v != ""}}
            return
    rows.append(new_row)


def update_md(path: Path, args: argparse.Namespace) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = "# 磁盘清理任务清单\n\n## 已完成记录\n\n| 时间 | 任务 ID | 动作 | 结果 |\n| --- | --- | --- | --- |\n"
    if "## 已完成记录" not in text:
        text += "\n## 已完成记录\n\n| 时间 | 任务 ID | 动作 | 结果 |\n| --- | --- | --- | --- |\n"
    line = f"| {date.today().isoformat()} | {args.id} | {args.note or args.item} | {args.status}; {args.cleaned_size}; {args.evidence} |\n"
    text = text.rstrip() + "\n" + line
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-list-md", type=Path, required=True)
    parser.add_argument("--task-list-csv", type=Path, required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--item", required=True)
    parser.add_argument("--status", required=True)
    parser.add_argument("--priority", default="P1")
    parser.add_argument("--baseline-size", default="")
    parser.add_argument("--current-size", default="")
    parser.add_argument("--cleaned-size", default="")
    parser.add_argument("--next-action", default="")
    parser.add_argument("--evidence", default="")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    rows = read_csv(args.task_list_csv)
    upsert(rows, args)
    write_csv(args.task_list_csv, rows)
    update_md(args.task_list_md, args)
    print(f"updated {args.task_list_csv}")
    print(f"updated {args.task_list_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
