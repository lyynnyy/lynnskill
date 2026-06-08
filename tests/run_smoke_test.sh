#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLEANUP_SKILL_DIR="$REPO_ROOT/skills/folder-cleanup-archiver"
ROUTER_SKILL_DIR="$REPO_ROOT/skills/project-folder-router"
BASE="${TMPDIR:-/tmp}/lynnskill-smoke"
ROOT="$BASE/folder-cleanup/root"
AUDIT="$BASE/folder-cleanup/audit"
ARCHIVE="$BASE/folder-cleanup/archive"

rm -rf "$BASE"
mkdir -p "$ROOT/old/slides" "$ROOT/active"

printf 'old deck content\n' > "$ROOT/old/slides/deck.pptx"
printf 'duplicate payload\n' > "$ROOT/old/dup-a.txt"
printf 'duplicate payload\n' > "$ROOT/old/dup-b.txt"
printf 'active notes\n' > "$ROOT/active/notes.md"

python3 - "$ROOT" <<'PY'
import os
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
old = time.mktime((2024, 1, 1, 12, 0, 0, 0, 0, -1))
for path in (root / "old").rglob("*"):
    if path.is_file():
        os.utime(path, (old, old))
PY

python3 "$CLEANUP_SKILL_DIR/scripts/scan_disk.py" "$ROOT" --output-dir "$AUDIT" --min-duplicate-size 1 --no-default-skips
python3 "$CLEANUP_SKILL_DIR/scripts/analyze_stale_archive.py" --scan-files "$AUDIT/scan_files.csv" --output-dir "$AUDIT" --months 6
python3 "$CLEANUP_SKILL_DIR/scripts/move_archive_candidates.py" --stale-files "$AUDIT/archive_stale_files_all.csv" --root "$ROOT" --target-dir "$ARCHIVE" --manifest "$AUDIT/move_manifest_dry.csv"
python3 "$CLEANUP_SKILL_DIR/scripts/move_archive_candidates.py" --stale-files "$AUDIT/archive_stale_files_all.csv" --root "$ROOT" --target-dir "$ARCHIVE" --manifest "$AUDIT/move_manifest.csv" --execute
python3 "$CLEANUP_SKILL_DIR/scripts/move_archive_candidates.py" --verify-manifest "$AUDIT/move_manifest.csv"
python3 "$CLEANUP_SKILL_DIR/scripts/build_cleanup_index.py" --output "$AUDIT/cleanup_archive_search_index.csv" --archive-manifest "$AUDIT/move_manifest.csv"
python3 "$CLEANUP_SKILL_DIR/scripts/update_cleanup_task_list.py" --task-list-md "$AUDIT/cleanup_task_list.md" --task-list-csv "$AUDIT/cleanup_task_list.csv" --id CLN-TEST --item "smoke archive" --status "已整理待备份/外移" --baseline-size "50B" --current-size "archive_exists" --cleaned-size "50B consolidated" --evidence "$AUDIT/move_manifest.csv" --note "smoke test"

python3 - "$AUDIT" <<'PY'
import csv
import json
import sys
from pathlib import Path

audit = Path(sys.argv[1])
summary = json.loads((audit / "scan_summary.json").read_text())
assert summary["file_count"] == 4, summary
assert summary["duplicate_group_count"] == 1, summary
stale = json.loads((audit / "archive_stale_summary.json").read_text())
assert stale["stale_file_count"] == 3, stale
index_rows = list(csv.DictReader((audit / "cleanup_archive_search_index.csv").open()))
assert len(index_rows) == 3, len(index_rows)
task_rows = list(csv.DictReader((audit / "cleanup_task_list.csv").open()))
assert task_rows and task_rows[0]["id"] == "CLN-TEST", task_rows
PY

ROUTER_BASE="$BASE/project-router"
ROUTER_ROOT="$ROUTER_BASE/output"
ROUTER_SOURCE="$ROUTER_BASE/source"
mkdir -p "$ROUTER_SOURCE"
printf 'deliverable payload\n' > "$ROUTER_SOURCE/deck.txt"
printf 'deliverable payload\n' > "$ROUTER_SOURCE/deck-copy.txt"

"$ROUTER_SKILL_DIR/scripts/ensure_project_output_folder.sh" \
  --output-root "$ROUTER_ROOT" \
  --customer "测试客户" \
  --project "测试项目" \
  --output-type "解决方案" \
  --reason "smoke ensure"

"$ROUTER_SKILL_DIR/scripts/route_output_file.sh" \
  --source-file "$ROUTER_SOURCE/deck.txt" \
  --output-root "$ROUTER_ROOT" \
  --customer "测试客户" \
  --project "测试项目" \
  --output-type "解决方案" \
  --copy \
  --reason "smoke copy" > "$ROUTER_BASE/route_copy.out"

"$ROUTER_SKILL_DIR/scripts/route_output_file.sh" \
  --source-file "$ROUTER_SOURCE/deck-copy.txt" \
  --output-root "$ROUTER_ROOT" \
  --customer "测试客户" \
  --project "测试项目" \
  --output-type "解决方案" \
  --reason "smoke duplicate" > "$ROUTER_BASE/route_duplicate.out"

grep -q '^status=save_needed$' "$ROUTER_BASE/route_copy.out"
grep -q '^saved_file=' "$ROUTER_BASE/route_copy.out"
grep -q '^status=file_exists$' "$ROUTER_BASE/route_duplicate.out"
test -f "$ROUTER_ROOT/产出管理/folder_routing_log.md"

echo "smoke test passed: $BASE"
