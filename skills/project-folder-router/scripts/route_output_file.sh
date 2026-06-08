#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ensure_script="$script_dir/ensure_project_output_folder.sh"

output_root="/Users/lynn/项目产出"
source_file=""
customer=""
project=""
output_type=""
reason=""
copy_file=0

usage() {
  cat <<'USAGE'
Usage:
  route_output_file.sh --source-file FILE --customer CUSTOMER --project PROJECT --output-type OUTPUT_TYPE [--reason TEXT] [--output-root PATH] [--copy]

Checks whether FILE already exists anywhere under <output-root> by content.
If the same file exists, records file_exists and does not save a duplicate.
If no same file exists, creates or reuses:
  <output-root>/<客户名称>/<项目名称>/<产出类型名称>

Default: print the folder where the caller should save the file.
With --copy: copy FILE into the routed folder without overwriting same-name different-content files.
USAGE
}

abs_path() {
  /usr/bin/python3 - "$1" <<'PY'
import os
import sys
print(os.path.abspath(sys.argv[1]))
PY
}

sha256_file() {
  /usr/bin/python3 - "$1" <<'PY'
import hashlib
import sys

h = hashlib.sha256()
with open(sys.argv[1], "rb") as f:
    for chunk in iter(lambda: f.read(1024 * 1024), b""):
        h.update(chunk)
print(h.hexdigest())
PY
}

unique_destination() {
  local folder="$1"
  local name="$2"
  local base ext candidate counter
  base="$name"
  ext=""
  if [[ "$name" == *.* ]]; then
    base="${name%.*}"
    ext=".${name##*.}"
  fi
  candidate="$folder/$name"
  counter=1
  while [[ -e "$candidate" ]]; do
    candidate="$folder/${base}_$counter$ext"
    counter=$((counter + 1))
  done
  printf '%s\n' "$candidate"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source-file)
      source_file="${2:-}"
      shift 2
      ;;
    --customer)
      customer="${2:-}"
      shift 2
      ;;
    --project)
      project="${2:-}"
      shift 2
      ;;
    --output-type)
      output_type="${2:-}"
      shift 2
      ;;
    --reason)
      reason="${2:-}"
      shift 2
      ;;
    --output-root)
      output_root="${2:-}"
      shift 2
      ;;
    --copy)
      copy_file=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "$source_file" || -z "$customer" || -z "$project" || -z "$output_type" ]]; then
  echo "Missing required --source-file, --customer, --project, or --output-type." >&2
  usage >&2
  exit 2
fi

if [[ ! -f "$source_file" ]]; then
  echo "Source file does not exist or is not a regular file: $source_file" >&2
  exit 2
fi

if [[ ! -x "$ensure_script" ]]; then
  echo "Folder routing script is not executable: $ensure_script" >&2
  exit 1
fi

output_root="${output_root%/}"
source_abs="$(abs_path "$source_file")"
source_hash="$(sha256_file "$source_abs")"
management_root="$output_root/产出管理"
log_file="$management_root/folder_routing_log.md"
mkdir -p "$management_root"

duplicate_file=""
if [[ -d "$output_root" ]]; then
  while IFS= read -r -d '' candidate; do
    candidate_abs="$(abs_path "$candidate")"
    if [[ "$candidate_abs" == "$source_abs" ]]; then
      continue
    fi
    if [[ "$(sha256_file "$candidate_abs")" == "$source_hash" ]] && cmp -s "$source_abs" "$candidate_abs"; then
      duplicate_file="$candidate_abs"
      break
    fi
  done < <(find "$output_root" -type f -print0)
fi

timestamp="$(date '+%Y-%m-%d %H:%M:%S %z')"

if [[ -n "$duplicate_file" ]]; then
  {
    printf -- '- 时间：%s\n' "$timestamp"
    printf '  客户名称：%s\n' "$customer"
    printf '  项目名称：%s\n' "$project"
    printf '  产出类型名称：%s\n' "$output_type"
    printf '  动作：file_exists\n'
    printf '  源文件：%s\n' "$source_abs"
    printf '  已存在文件：%s\n' "$duplicate_file"
    printf '  文件SHA256：%s\n' "$source_hash"
    if [[ -n "$reason" ]]; then
      printf '  原因：%s\n' "$reason"
    fi
  } >> "$log_file"

  printf 'status=file_exists\n'
  printf 'should_save=0\n'
  printf 'source_file=%s\n' "$source_abs"
  printf 'existing_file=%s\n' "$duplicate_file"
  printf 'sha256=%s\n' "$source_hash"
  printf 'log=%s\n' "$log_file"
  exit 0
fi

route_output="$("$ensure_script" --output-root "$output_root" --customer "$customer" --project "$project" --output-type "$output_type" --reason "$reason")"
save_folder="$(printf '%s\n' "$route_output" | awk -F= '/^path=/{print substr($0, index($0, "=") + 1)}' | tail -n 1)"
folder_action="$(printf '%s\n' "$route_output" | awk -F= '/^action=/{print substr($0, index($0, "=") + 1)}' | tail -n 1)"

if [[ -z "$save_folder" ]]; then
  echo "Could not determine save folder from folder routing output." >&2
  printf '%s\n' "$route_output" >&2
  exit 1
fi

saved_file=""
if [[ "$copy_file" == "1" ]]; then
  source_name="$(basename "$source_abs")"
  destination="$save_folder/$source_name"
  if [[ -e "$destination" ]]; then
    if [[ -f "$destination" ]] && cmp -s "$source_abs" "$destination"; then
      saved_file="$destination"
    else
      saved_file="$(unique_destination "$save_folder" "$source_name")"
      cp "$source_abs" "$saved_file"
    fi
  else
    saved_file="$destination"
    cp "$source_abs" "$saved_file"
  fi
fi

{
  printf -- '- 时间：%s\n' "$timestamp"
  printf '  客户名称：%s\n' "$customer"
  printf '  项目名称：%s\n' "$project"
  printf '  产出类型名称：%s\n' "$output_type"
  printf '  动作：save_needed\n'
  printf '  源文件：%s\n' "$source_abs"
  printf '  保存文件夹：%s\n' "$save_folder"
  printf '  文件SHA256：%s\n' "$source_hash"
  if [[ -n "$saved_file" ]]; then
    printf '  已保存文件：%s\n' "$saved_file"
  fi
  if [[ -n "$reason" ]]; then
    printf '  原因：%s\n' "$reason"
  fi
} >> "$log_file"

printf 'status=save_needed\n'
printf 'should_save=1\n'
printf 'source_file=%s\n' "$source_abs"
printf 'save_folder=%s\n' "$save_folder"
printf 'folder_action=%s\n' "$folder_action"
printf 'sha256=%s\n' "$source_hash"
if [[ -n "$saved_file" ]]; then
  printf 'saved_file=%s\n' "$saved_file"
fi
printf 'log=%s\n' "$log_file"
