#!/usr/bin/env python3
"""Dry-run, execute, and verify archive-candidate moves."""

from __future__ import annotations

import argparse
import csv
import os
import shutil
from datetime import datetime
from pathlib import Path


FIELDS = [
    "source",
    "destination",
    "relative_path",
    "status",
    "reason",
    "size_before",
    "size_after",
    "mtime_before",
    "mtime_after",
    "type_group",
    "processed_at",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_manifest(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def stat_info(path: Path) -> tuple[str, str]:
    st = path.stat()
    return str(st.st_size), str(st.st_mtime)


def verify_manifest(path: Path) -> int:
    rows = read_rows(path)
    problems: list[str] = []
    moved = 0
    for row in rows:
        if row.get("status") != "moved":
            continue
        moved += 1
        src = Path(row["source"])
        dst = Path(row["destination"])
        if src.exists():
            problems.append(f"source still exists: {src}")
        if not dst.exists():
            problems.append(f"destination missing: {dst}")
            continue
        size, mtime = stat_info(dst)
        if size != row.get("size_before"):
            problems.append(f"size mismatch: {dst}")
        if row.get("mtime_before") and abs(float(mtime) - float(row["mtime_before"])) > 1:
            problems.append(f"mtime mismatch: {dst}")
    print(f"verified moved rows: {moved}")
    print(f"problems: {len(problems)}")
    for problem in problems[:50]:
        print(problem)
    return 1 if problems else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stale-files", type=Path)
    parser.add_argument("--root", type=Path)
    parser.add_argument("--target-dir", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--verify-manifest", type=Path)
    args = parser.parse_args()

    if args.verify_manifest:
        return verify_manifest(args.verify_manifest.expanduser().resolve())

    required = [args.stale_files, args.root, args.target_dir, args.manifest]
    if any(value is None for value in required):
        parser.error("--stale-files, --root, --target-dir, and --manifest are required unless --verify-manifest is used")

    root = args.root.expanduser().resolve()
    target = args.target_dir.expanduser().resolve()
    rows = read_rows(args.stale_files)
    if args.limit:
        rows = rows[: args.limit]

    manifest_rows: list[dict[str, str]] = []
    for row in rows:
        src = Path(row["path"]).expanduser()
        try:
            rel = src.resolve().relative_to(root).as_posix()
        except Exception:
            rel = row.get("relative_path") or src.name
        dst = target / rel
        status = "dry_run_ready"
        reason = "ready to move; rerun with --execute after user confirmation"
        size_before = ""
        mtime_before = ""
        size_after = ""
        mtime_after = ""

        if not src.exists():
            status = "missing"
            reason = "source path does not exist"
        elif dst.exists():
            status = "conflict"
            reason = "destination already exists"
            size_before, mtime_before = stat_info(src)
        else:
            size_before, mtime_before = stat_info(src)
            if args.execute:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                os.utime(dst, (float(row.get("atime") or mtime_before), float(mtime_before)))
                size_after, mtime_after = stat_info(dst)
                status = "moved"
                reason = "moved preserving relative path"

        manifest_rows.append(
            {
                "source": str(src),
                "destination": str(dst),
                "relative_path": rel,
                "status": status,
                "reason": reason,
                "size_before": size_before,
                "size_after": size_after,
                "mtime_before": mtime_before,
                "mtime_after": mtime_after,
                "type_group": row.get("type_group", ""),
                "processed_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

    write_manifest(args.manifest, manifest_rows)
    counts: dict[str, int] = {}
    for row in manifest_rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"wrote manifest to {args.manifest}")
    print(counts)
    if not args.execute:
        print("dry run only; no files moved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
