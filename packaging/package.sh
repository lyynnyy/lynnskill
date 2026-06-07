#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$REPO_ROOT/dist"
mkdir -p "$DIST"

cd "$REPO_ROOT"
ZIP_PATH="$DIST/lynnskill-folder-cleanup-archiver.zip"
rm -f "$ZIP_PATH"
zip -r "$ZIP_PATH" \
  "skills/folder-cleanup-archiver" \
  "README.md" \
  "LICENSE" \
  "tests/run_smoke_test.sh"

echo "$ZIP_PATH"
