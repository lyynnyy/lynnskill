---
name: folder-cleanup-archiver
description: Use in Codex or Claude when the user asks to scan or整理 local folders, audit disk usage, identify files suitable for backup/archive, find exact duplicates, analyze files not opened or modified for months, move archive candidates while preserving folder structure, maintain cleanup task lists, or build a searchable index of deleted/backed-up/archived file status and locations.
---

# Folder Cleanup Archiver

## Purpose

Safely audit, archive, and track local files. This skill turns an ad hoc cleanup session into a repeatable workflow with reports, confirmation gates, move manifests, verification, task lists, and a searchable file-status index.

## Runtime Compatibility

Use this skill in both Codex and Claude. Resolve `SKILL_DIR` as the absolute path to this `folder-cleanup-archiver` folder before running scripts:

```bash
SKILL_DIR="/absolute/path/to/folder-cleanup-archiver"
```

In Claude Code, `${CLAUDE_SKILL_DIR}` may already point to the skill folder. In Codex, use the installed skill path or the repository path. If neither environment variable is available, inspect the loaded skill location and use that folder.

## Safety Rules

- Default to read-only scanning. Do not delete, move, overwrite, or clear caches without explicit user confirmation in the current conversation.
- Treat duplicate-file results as candidates only. Never delete duplicates automatically.
- For move/archive actions, run a dry run first, report missing/conflicting files, then ask for confirmation before running with `--execute`.
- Preserve original folder structure when moving archive candidates. Use a stable root such as `/Users/lynn` or the scanned folder.
- Keep evidence: every run should write CSV/JSON/Markdown artifacts into a timestamped audit directory.
- After execution, verify counts, source/target existence, file sizes, and mtimes before reporting success.
- If a previously recorded file or folder no longer exists, update the task list and search index instead of treating it as an error; mark it as cleaned, offloaded, or user-confirmed when the user says so.
- Be conservative with macOS protected folders, Docker disk images, git worktrees, databases, and project environments. Report them separately and ask before cleanup.

## Standard Workflow

1. Create or reuse an audit directory, for example:

```bash
mkdir -p /Users/lynn/disk_audit_YYYY-MM-DD
```

2. Scan the root folder:

```bash
python3 "${SKILL_DIR}/scripts/scan_disk.py" \
  /Users/lynn \
  --output-dir /Users/lynn/disk_audit_YYYY-MM-DD
```

3. Summarize categories for the user:

- `可直接清理`: models, temporary files, obvious caches, failed downloads, app-generated disposable files.
- `可备份归档`: older documents, PPT/PDF/Excel/media/project materials not actively used.
- `仍需留本机`: active projects, current workspaces, app configs, credentials, databases.
- `待确认`: project folders, V2/worktrees, ambiguous materials, duplicate candidates.
- `不建议手动清理`: Docker raw disk, macOS protected folders, application databases.

4. Analyze stale archive candidates:

```bash
python3 "${SKILL_DIR}/scripts/analyze_stale_archive.py" \
  --scan-files /Users/lynn/disk_audit_YYYY-MM-DD/scan_files.csv \
  --output-dir /Users/lynn/disk_audit_YYYY-MM-DD \
  --months 6
```

`强归档` means both access time and modified time are older than the cutoff. On macOS, access time is approximate; modified time is more reliable.

5. If the user approves moving strong archive files, dry-run first:

```bash
python3 "${SKILL_DIR}/scripts/move_archive_candidates.py" \
  --stale-files /Users/lynn/disk_audit_YYYY-MM-DD/archive_stale_files_all.csv \
  --root /Users/lynn \
  --target-dir /Users/lynn/近半年未打开未更改 \
  --manifest /Users/lynn/disk_audit_YYYY-MM-DD/strict_stale_move_manifest.csv
```

Then execute only after explicit confirmation:

```bash
python3 "${SKILL_DIR}/scripts/move_archive_candidates.py" \
  --stale-files /Users/lynn/disk_audit_YYYY-MM-DD/archive_stale_files_all.csv \
  --root /Users/lynn \
  --target-dir /Users/lynn/近半年未打开未更改 \
  --manifest /Users/lynn/disk_audit_YYYY-MM-DD/strict_stale_move_manifest.csv \
  --execute
```

6. Verify the manifest:

```bash
python3 "${SKILL_DIR}/scripts/move_archive_candidates.py" \
  --verify-manifest /Users/lynn/disk_audit_YYYY-MM-DD/strict_stale_move_manifest.csv
```

7. Maintain the search index:

```bash
python3 "${SKILL_DIR}/scripts/build_cleanup_index.py" \
  --output /Users/lynn/disk_audit_YYYY-MM-DD/cleanup_archive_search_index.csv \
  --archive-manifest /Users/lynn/disk_audit_YYYY-MM-DD/strict_stale_move_manifest.csv
```

When the user confirms a folder has been cleaned after archiving, add `--archive-confirmed-cleaned` so the index records user confirmation.

8. Maintain the task list:

```bash
python3 "${SKILL_DIR}/scripts/update_cleanup_task_list.py" \
  --task-list-md /Users/lynn/disk_audit_YYYY-MM-DD/cleanup_task_list.md \
  --task-list-csv /Users/lynn/disk_audit_YYYY-MM-DD/cleanup_task_list.csv \
  --id CLN-004 \
  --item "近半年未打开未更改强归档文件" \
  --status "已清理释放空间" \
  --current-size "路径当前不存在，用户确认已清理" \
  --cleaned-size "22.3 GiB 已释放/外移" \
  --evidence "move manifest + user confirmation" \
  --note "用户确认归档目录已清理完"
```

## Required Reports

For a full cleanup session, produce at least:

- `scan_report.md`: disk and folder scan summary.
- `cleanup_task_list.md` and `.csv`: durable cleanup task list with status and evidence.
- `archive_stale_report.md`: stale archive analysis.
- `strict_stale_move_manifest.csv`: every moved/missing/conflicting archive candidate.
- `cleanup_archive_search_index.csv`: searchable file-status index for future material lookup.
- `progress.md`: chronological record of actions, confirmations, and verification.

## Status Vocabulary

Use consistent status labels. Read `references/status_taxonomy.md` when adding new statuses or interpreting an old cleanup index.

## User-Facing Reporting

In Chinese, report:

- current capacity pressure and biggest directories;
- what can be cleaned now, what needs backup/archive, and what should stay;
- exact duplicate groups and theoretical savings;
- stale-file counts, sizes, types, and folders;
- every destructive or move action that needs confirmation;
- what was verified afterward;
- where the user can search file names later.

Keep the final answer short, but include links to the main artifacts.
