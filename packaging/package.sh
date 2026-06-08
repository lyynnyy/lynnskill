#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST="$REPO_ROOT/dist"
mkdir -p "$DIST"

cd "$REPO_ROOT"

ALL_ZIP="$DIST/lynnskill-skills.zip"
rm -f "$ALL_ZIP"
zip -r "$ALL_ZIP" \
  "skills" \
  "README.md" \
  "LICENSE" \
  "tests/run_smoke_test.sh"
echo "$ALL_ZIP"

for skill_dir in skills/*; do
  [[ -d "$skill_dir" ]] || continue
  skill_name="$(basename "$skill_dir")"
  zip_path="$DIST/lynnskill-${skill_name}.zip"
  rm -f "$zip_path"
  zip -r "$zip_path" \
    "$skill_dir" \
    "README.md" \
    "LICENSE" \
    "tests/run_smoke_test.sh"
  echo "$zip_path"
done
