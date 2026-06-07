# Lynn Skill

This repository stores reusable AI skills that Lynn can install into Codex and Claude.

Current skills:

- `folder-cleanup-archiver`: safely scan local folders, identify cleanup/archive candidates, move stale archive files with manifests, verify results, and maintain searchable cleanup indexes.

## Repository Layout

```text
lynnskill/
├── skills/
│   └── folder-cleanup-archiver/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       ├── references/status_taxonomy.md
│       └── scripts/*.py
├── tests/run_smoke_test.sh
└── packaging/package.sh
```

`SKILL.md` is the shared skill entrypoint. Codex reads the standard frontmatter and may also use `agents/openai.yaml` for UI metadata. Claude reads the same `SKILL.md`; it can ignore `agents/openai.yaml`.

## Install Locally

Install into Codex:

```bash
cp -R skills/folder-cleanup-archiver ~/.codex/skills/
```

Install into Claude:

```bash
cp -R skills/folder-cleanup-archiver ~/.claude/skills/
```

For development, symlinks are usually easier because one repository update updates both agents:

```bash
ln -s "$PWD/skills/folder-cleanup-archiver" ~/.codex/skills/folder-cleanup-archiver
ln -s "$PWD/skills/folder-cleanup-archiver" ~/.claude/skills/folder-cleanup-archiver
```

If a destination already exists, remove it or back it up first.

## Skill: Folder Cleanup Archiver

Use this skill when the user asks to:

- scan a local folder or whole home directory for disk usage;
- identify large folders, large files, caches, models, videos, and development dependencies;
- classify files into cleanup, archive, keep-local, confirm-first, and do-not-touch categories;
- find exact duplicate files;
- find files not opened and not modified for a configurable period, usually six months;
- move strong archive candidates into a new archive folder while preserving original folder structure;
- verify move manifests after execution;
- maintain a cleanup task list;
- maintain a searchable index of deleted, backed-up, archived, or missing files.

### Safety Model

The skill is intentionally conservative.

- Scanning and analysis are read-only.
- Moving files requires a dry run first.
- Deleting files is not implemented as a bulk operation; the agent must ask for explicit user confirmation and use system tools carefully.
- Duplicate detection produces candidates, not deletion decisions.
- macOS protected folders, Docker raw disk files, git worktrees, databases, credentials, and project environments are reported separately and should not be manually removed without a specific plan.

### Main Scripts

```text
scripts/scan_disk.py
```

Read-only scanner. Produces `scan_files.csv`, `scan_report.md`, directory summaries, file-type summaries, exact duplicate reports, and scan errors.

```text
scripts/analyze_stale_archive.py
```

Reads `scan_files.csv` and finds files whose access time and modified time are both older than the cutoff.

```text
scripts/move_archive_candidates.py
```

Dry-runs or executes archive moves. It preserves relative paths under a chosen root and writes a manifest. It can also verify a manifest.

```text
scripts/build_cleanup_index.py
```

Builds a CSV search index with file name, status, original path, current path, existence checks, batch, date, type, size, evidence, and notes.

```text
scripts/update_cleanup_task_list.py
```

Creates or updates Markdown and CSV cleanup task lists.

## Typical Workflow

```bash
SKILL_DIR="$PWD/skills/folder-cleanup-archiver"
AUDIT_DIR="/tmp/folder-cleanup-audit"
ROOT="/path/to/scan"
ARCHIVE_DIR="/tmp/folder-cleanup-archive"
```

Scan:

```bash
python3 "$SKILL_DIR/scripts/scan_disk.py" "$ROOT" --output-dir "$AUDIT_DIR"
```

Analyze stale archive candidates:

```bash
python3 "$SKILL_DIR/scripts/analyze_stale_archive.py" \
  --scan-files "$AUDIT_DIR/scan_files.csv" \
  --output-dir "$AUDIT_DIR" \
  --months 6
```

Dry-run archive move:

```bash
python3 "$SKILL_DIR/scripts/move_archive_candidates.py" \
  --stale-files "$AUDIT_DIR/archive_stale_files_all.csv" \
  --root "$ROOT" \
  --target-dir "$ARCHIVE_DIR" \
  --manifest "$AUDIT_DIR/strict_stale_move_manifest.csv"
```

Execute only after explicit user confirmation:

```bash
python3 "$SKILL_DIR/scripts/move_archive_candidates.py" \
  --stale-files "$AUDIT_DIR/archive_stale_files_all.csv" \
  --root "$ROOT" \
  --target-dir "$ARCHIVE_DIR" \
  --manifest "$AUDIT_DIR/strict_stale_move_manifest.csv" \
  --execute
```

Verify:

```bash
python3 "$SKILL_DIR/scripts/move_archive_candidates.py" \
  --verify-manifest "$AUDIT_DIR/strict_stale_move_manifest.csv"
```

Build search index:

```bash
python3 "$SKILL_DIR/scripts/build_cleanup_index.py" \
  --output "$AUDIT_DIR/cleanup_archive_search_index.csv" \
  --archive-manifest "$AUDIT_DIR/strict_stale_move_manifest.csv"
```

Run smoke test:

```bash
tests/run_smoke_test.sh
```

## Publish

Create a public GitHub repository named `lynnskill` and push:

```bash
git init
git add .
git commit -m "feat: add folder cleanup archiver skill"
gh repo create lynnskill --public --source=. --remote=origin --push
```

Use `packaging/package.sh` to create a zip artifact for manual upload or release attachment.
