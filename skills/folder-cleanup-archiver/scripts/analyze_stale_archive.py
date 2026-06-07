#!/usr/bin/env python3
"""Analyze files not accessed and not modified for an archive cutoff."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def human_size(num: int) -> str:
    value = float(num)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TiB"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scan-files", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--months", type=int, default=6)
    parser.add_argument("--scope-prefix", action="append", default=[])
    parser.add_argument("--min-size", type=int, default=0)
    args = parser.parse_args()

    out = args.output_dir.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    cutoff = datetime.now() - timedelta(days=round(args.months * 30.4375))
    cutoff_ts = cutoff.timestamp()

    rows = read_rows(args.scan_files)
    stale: list[dict[str, str]] = []
    for row in rows:
        path = row["path"]
        if args.scope_prefix and not any(path.startswith(prefix) for prefix in args.scope_prefix):
            continue
        size = int(row.get("size_bytes") or 0)
        if size < args.min_size:
            continue
        atime = float(row.get("atime") or 0)
        mtime = float(row.get("mtime") or 0)
        if atime < cutoff_ts and mtime < cutoff_ts:
            stale.append(
                {
                    **row,
                    "archive_scope": "strong_archive",
                    "cutoff_iso": cutoff.isoformat(timespec="seconds"),
                }
            )

    stale.sort(key=lambda r: int(r["size_bytes"]), reverse=True)
    fields = list(stale[0].keys()) if stale else [
        "path",
        "relative_path",
        "size_bytes",
        "size_human",
        "mtime",
        "mtime_iso",
        "atime",
        "atime_iso",
        "extension",
        "type_group",
        "top_dir",
        "second_dir",
        "archive_scope",
        "cutoff_iso",
    ]
    write_csv(out / "archive_stale_files_all.csv", stale, fields)
    write_csv(out / "archive_stale_files_top300.csv", stale[:300], fields)

    by_type: dict[str, int] = defaultdict(int)
    by_folder: dict[str, int] = defaultdict(int)
    for row in stale:
        size = int(row["size_bytes"])
        by_type[row.get("type_group", "")] += size
        by_folder[row.get("second_dir") or row.get("top_dir", "")] += size

    type_rows = [
        {"type_group": k, "size_bytes": str(v), "size_human": human_size(v)}
        for k, v in sorted(by_type.items(), key=lambda item: item[1], reverse=True)
    ]
    folder_rows = [
        {"folder": k, "size_bytes": str(v), "size_human": human_size(v)}
        for k, v in sorted(by_folder.items(), key=lambda item: item[1], reverse=True)
    ]
    write_csv(out / "archive_stale_by_type.csv", type_rows, ["type_group", "size_bytes", "size_human"])
    write_csv(out / "archive_stale_by_folder.csv", folder_rows, ["folder", "size_bytes", "size_human"])

    total_size = sum(int(r["size_bytes"]) for r in stale)
    summary = {
        "scan_files": str(args.scan_files),
        "months": args.months,
        "cutoff_iso": cutoff.isoformat(timespec="seconds"),
        "stale_file_count": len(stale),
        "stale_size_bytes": total_size,
        "stale_size_human": human_size(total_size),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    (out / "archive_stale_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    report = [
        "# Stale Archive Report",
        "",
        f"- Cutoff: `{summary['cutoff_iso']}`",
        f"- Strong archive files: {len(stale)}",
        f"- Strong archive size: {human_size(total_size)}",
        "",
        "Note: macOS access time can be approximate. Modified time is usually more reliable.",
        "",
        "## By Type",
        "",
    ]
    for row in type_rows:
        report.append(f"- {row['type_group']}: {row['size_human']}")
    report.extend(["", "## Top Folders", ""])
    for row in folder_rows[:50]:
        report.append(f"- `{row['folder']}`: {row['size_human']}")
    (out / "archive_stale_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"wrote stale archive artifacts to {out}")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
