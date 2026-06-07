#!/usr/bin/env python3
"""Read-only folder scan for cleanup and archive planning."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable


TYPE_EXTENSIONS = {
    "presentation": {".ppt", ".pptx", ".key"},
    "spreadsheet": {".xls", ".xlsx", ".csv", ".tsv", ".numbers"},
    "document": {".doc", ".docx", ".pdf", ".txt", ".md", ".rtf", ".pages"},
    "image": {".jpg", ".jpeg", ".png", ".gif", ".heic", ".webp", ".tif", ".tiff", ".psd", ".ai"},
    "video": {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"},
    "audio": {".mp3", ".wav", ".m4a", ".aac", ".flac"},
    "archive": {".zip", ".tar", ".gz", ".tgz", ".rar", ".7z", ".dmg", ".iso"},
    "code": {".py", ".js", ".ts", ".tsx", ".jsx", ".swift", ".java", ".go", ".rs", ".sql", ".html", ".css"},
}

DEFAULT_SKIP_PARTS = {
    ".Trash",
    ".git",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "Library/Mail",
    "Library/Messages",
    "Library/Safari",
    "Library/Containers",
    "Library/Group Containers",
    "Pictures/Photos Library.photoslibrary",
}


def human_size(num: int) -> str:
    value = float(num)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            if unit == "B":
                return f"{int(value)} {unit}"
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TiB"


def iso(ts: float) -> str:
    return datetime.fromtimestamp(ts).isoformat(timespec="seconds")


def type_group(path: Path) -> str:
    ext = path.suffix.lower()
    for group, exts in TYPE_EXTENSIONS.items():
        if ext in exts:
            return group
    if ext:
        return "other_with_extension"
    return "no_extension"


def should_skip(path: Path, root: Path, skip_parts: set[str]) -> bool:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.as_posix()
    if path.name in skip_parts:
        return True
    return any(rel == part or rel.startswith(part + "/") for part in skip_parts)


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def scan_files(root: Path, skip_parts: set[str]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    rows: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    stack = [root]
    while stack:
        current = stack.pop()
        if should_skip(current, root, skip_parts) and current != root:
            continue
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    path = Path(entry.path)
                    if entry.is_dir(follow_symlinks=False):
                        if not should_skip(path, root, skip_parts):
                            stack.append(path)
                        continue
                    if not entry.is_file(follow_symlinks=False):
                        continue
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except OSError as exc:
                        errors.append({"path": str(path), "error": repr(exc)})
                        continue
                    rel = path.relative_to(root).as_posix()
                    parts = rel.split("/")
                    rows.append(
                        {
                            "path": str(path),
                            "relative_path": rel,
                            "size_bytes": str(st.st_size),
                            "size_human": human_size(st.st_size),
                            "mtime": str(st.st_mtime),
                            "mtime_iso": iso(st.st_mtime),
                            "atime": str(st.st_atime),
                            "atime_iso": iso(st.st_atime),
                            "extension": path.suffix.lower(),
                            "type_group": type_group(path),
                            "top_dir": parts[0] if parts else "",
                            "second_dir": "/".join(parts[:2]) if len(parts) > 1 else (parts[0] if parts else ""),
                        }
                    )
        except OSError as exc:
            errors.append({"path": str(current), "error": repr(exc)})
    return rows, errors


def write_csv(path: Path, rows: Iterable[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def duplicate_reports(rows: list[dict[str, str]], min_size: int) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    by_size: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        size = int(row["size_bytes"])
        if size >= min_size:
            by_size[size].append(row)

    by_digest: dict[str, list[dict[str, str]]] = defaultdict(list)
    for same_size in by_size.values():
        if len(same_size) < 2:
            continue
        for row in same_size:
            try:
                digest = sha256_file(Path(row["path"]))
            except OSError:
                continue
            by_digest[digest].append(row)

    groups: list[dict[str, str]] = []
    files: list[dict[str, str]] = []
    group_id = 0
    for digest, members in by_digest.items():
        if len(members) < 2:
            continue
        group_id += 1
        size = int(members[0]["size_bytes"])
        savings = size * (len(members) - 1)
        groups.append(
            {
                "group_id": str(group_id),
                "sha256": digest,
                "file_count": str(len(members)),
                "file_size_bytes": str(size),
                "file_size_human": human_size(size),
                "theoretical_savings_bytes": str(savings),
                "theoretical_savings_human": human_size(savings),
            }
        )
        for member in members:
            files.append({"group_id": str(group_id), "sha256": digest, **member})
    return groups, files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path.cwd() / f"folder_cleanup_{datetime.now():%Y%m%d_%H%M%S}")
    parser.add_argument("--min-duplicate-size", type=int, default=10 * 1024 * 1024)
    parser.add_argument("--no-default-skips", action="store_true")
    parser.add_argument("--skip-part", action="append", default=[])
    args = parser.parse_args()

    root = args.root.expanduser().resolve()
    out = args.output_dir.expanduser().resolve()
    skip_parts = set(args.skip_part)
    if not args.no_default_skips:
        skip_parts |= DEFAULT_SKIP_PARTS

    rows, errors = scan_files(root, skip_parts)
    rows.sort(key=lambda r: int(r["size_bytes"]), reverse=True)

    fields = [
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
    ]
    write_csv(out / "scan_files.csv", rows, fields)
    write_csv(out / "top_files.csv", rows[:300], fields)
    write_csv(out / "scan_errors.csv", errors, ["path", "error"])

    dir_sizes: dict[tuple[str, str], int] = defaultdict(int)
    type_sizes: dict[str, int] = defaultdict(int)
    for row in rows:
        size = int(row["size_bytes"])
        dir_sizes[("top", row["top_dir"])] += size
        dir_sizes[("second", row["second_dir"])] += size
        type_sizes[row["type_group"]] += size

    dir_rows = [
        {"level": level, "folder": folder, "size_bytes": str(size), "size_human": human_size(size)}
        for (level, folder), size in sorted(dir_sizes.items(), key=lambda item: item[1], reverse=True)
    ]
    write_csv(out / "dir_summary.csv", dir_rows, ["level", "folder", "size_bytes", "size_human"])

    type_rows = [
        {"type_group": group, "size_bytes": str(size), "size_human": human_size(size)}
        for group, size in sorted(type_sizes.items(), key=lambda item: item[1], reverse=True)
    ]
    write_csv(out / "type_summary.csv", type_rows, ["type_group", "size_bytes", "size_human"])

    duplicate_groups, duplicate_files = duplicate_reports(rows, args.min_duplicate_size)
    write_csv(
        out / "duplicate_groups.csv",
        duplicate_groups,
        [
            "group_id",
            "sha256",
            "file_count",
            "file_size_bytes",
            "file_size_human",
            "theoretical_savings_bytes",
            "theoretical_savings_human",
        ],
    )
    write_csv(out / "duplicate_files.csv", duplicate_files, ["group_id", "sha256", *fields])

    total_size = sum(int(r["size_bytes"]) for r in rows)
    summary = {
        "root": str(root),
        "output_dir": str(out),
        "file_count": len(rows),
        "total_size_bytes": total_size,
        "total_size_human": human_size(total_size),
        "error_count": len(errors),
        "duplicate_group_count": len(duplicate_groups),
        "duplicate_file_count": len(duplicate_files),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }
    (out / "scan_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Folder Cleanup Scan Report",
        "",
        f"- Root: `{root}`",
        f"- Files scanned: {len(rows)}",
        f"- Total size: {human_size(total_size)}",
        f"- Scan errors: {len(errors)}",
        f"- Exact duplicate groups: {len(duplicate_groups)}",
        "",
        "## Largest Folders",
        "",
    ]
    for row in dir_rows[:30]:
        report.append(f"- `{row['folder']}` ({row['level']}): {row['size_human']}")
    report.extend(["", "## Largest File Types", ""])
    for row in type_rows:
        report.append(f"- {row['type_group']}: {row['size_human']}")
    (out / "scan_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"wrote scan artifacts to {out}")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
