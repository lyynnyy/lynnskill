#!/usr/bin/env python3
"""Build a searchable CSV index for cleaned, deleted, and archived materials."""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path


FIELDS = [
    "record_id",
    "material_name",
    "status",
    "status_detail",
    "original_path",
    "current_path",
    "current_exists",
    "original_exists",
    "batch",
    "action_date",
    "type_group",
    "size_bytes",
    "size_human",
    "evidence_file",
    "notes",
]


def human_size(num: int) -> str:
    value = float(num)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TiB"


def exists_text(path: str) -> str:
    return "yes" if path and Path(path).exists() else ("no" if path else "")


def make_row(
    record_id: str,
    material_name: str,
    status: str,
    status_detail: str,
    original_path: str,
    current_path: str,
    batch: str,
    action_date: str,
    type_group: str = "",
    size_bytes: str = "",
    size_human: str = "",
    evidence_file: str = "",
    notes: str = "",
) -> dict[str, str]:
    return {
        "record_id": record_id,
        "material_name": material_name,
        "status": status,
        "status_detail": status_detail,
        "original_path": original_path,
        "current_path": current_path,
        "current_exists": exists_text(current_path),
        "original_exists": exists_text(original_path),
        "batch": batch,
        "action_date": action_date,
        "type_group": type_group,
        "size_bytes": size_bytes,
        "size_human": size_human or (human_size(int(size_bytes)) if str(size_bytes).isdigit() else ""),
        "evidence_file": evidence_file,
        "notes": notes,
    }


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def add_archive_manifest(out_rows: list[dict[str, str]], manifest: Path, confirmed_cleaned: bool) -> None:
    for i, row in enumerate(read_csv(manifest), start=1):
        status = row.get("status", "")
        if status not in {"moved", "missing", "conflict", "dry_run_ready"}:
            continue
        source = row.get("source", "")
        dest = row.get("destination", "")
        if status == "moved":
            if Path(dest).exists():
                file_status = "已归档_本机"
                detail = "已移动到本机归档目录，保留原始文件夹结构"
                notes = "源路径已移动；当前路径为归档目录内位置"
            elif confirmed_cleaned:
                file_status = "已归档_本机副本已清理_用户确认"
                detail = "此前已移动到本机归档目录；用户已确认归档副本清理完成"
                notes = "源路径已移动；归档目录内本机副本当前不存在，用户确认已清理完"
            else:
                file_status = "已归档_本机副本已清理或外移"
                detail = "此前已移动到本机归档目录；当前该本机归档路径不存在"
                notes = "源路径已移动；归档副本当前不存在，可能已清理、备份或外移"
        elif status == "missing":
            file_status = "已清理或外移_源路径缺失"
            detail = "移动前源路径已不存在"
            notes = row.get("reason", "")
        elif status == "conflict":
            file_status = "待确认_归档目标冲突"
            detail = "目标路径已存在，未移动"
            notes = row.get("reason", "")
        else:
            file_status = "待执行_归档dry-run"
            detail = "dry-run 记录，尚未移动"
            notes = row.get("reason", "")
        out_rows.append(
            make_row(
                record_id=f"ARCHIVE-{len(out_rows)+1:05d}",
                material_name=Path(source).name,
                status=file_status,
                status_detail=detail,
                original_path=source,
                current_path=dest if status == "moved" else "",
                batch=manifest.stem,
                action_date=str(date.today()),
                type_group=row.get("type_group", ""),
                size_bytes=row.get("size_before", ""),
                evidence_file=str(manifest),
                notes=notes,
            )
        )


def add_deletion_records(out_rows: list[dict[str, str]], record_file: Path) -> None:
    for row in read_csv(record_file):
        original = row.get("original_path", "")
        current = row.get("current_path", "")
        out_rows.append(
            make_row(
                record_id=row.get("record_id") or f"DELETE-{len(out_rows)+1:05d}",
                material_name=row.get("material_name") or Path(original).name,
                status=row.get("status", "已删除"),
                status_detail=row.get("status_detail", row.get("status", "已删除")),
                original_path=original,
                current_path=current,
                batch=row.get("batch", record_file.stem),
                action_date=row.get("action_date", str(date.today())),
                type_group=row.get("type_group", ""),
                size_bytes=row.get("size_bytes", ""),
                size_human=row.get("size_human", ""),
                evidence_file=row.get("evidence_file", str(record_file)),
                notes=row.get("notes", ""),
            )
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive-manifest", type=Path, action="append", default=[])
    parser.add_argument("--deletion-records", type=Path, action="append", default=[])
    parser.add_argument("--archive-confirmed-cleaned", action="store_true")
    args = parser.parse_args()

    rows: list[dict[str, str]] = []
    for manifest in args.archive_manifest:
        add_archive_manifest(rows, manifest.expanduser().resolve(), args.archive_confirmed_cleaned)
    for record_file in args.deletion_records:
        add_deletion_records(rows, record_file.expanduser().resolve())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
