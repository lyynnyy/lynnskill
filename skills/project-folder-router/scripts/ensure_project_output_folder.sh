#!/usr/bin/env bash
set -euo pipefail

output_root="/Users/lynn/项目产出"
customer=""
project=""
output_type=""
reason=""

usage() {
  cat <<'USAGE'
Usage:
  ensure_project_output_folder.sh --customer CUSTOMER --project PROJECT --output-type OUTPUT_TYPE [--reason TEXT] [--output-root PATH]

Creates or reuses:
  <output-root>/<客户名称>/<项目名称>/<产出类型名称>

Prints path, action, and log entries.
USAGE
}

sanitize_segment() {
  local raw="$1"
  raw="${raw//$'\n'/ }"
  raw="${raw//$'\r'/ }"
  raw="${raw//\//-}"
  raw="${raw//:/-}"
  raw="${raw#"${raw%%[![:space:]]*}"}"
  raw="${raw%"${raw##*[![:space:]]}"}"
  if [[ -z "$raw" ]]; then
    echo "未命名"
  else
    echo "$raw"
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
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

if [[ -z "$customer" || -z "$project" || -z "$output_type" ]]; then
  echo "Missing required --customer, --project, or --output-type." >&2
  usage >&2
  exit 2
fi

customer="$(sanitize_segment "$customer")"
project="$(sanitize_segment "$project")"
output_type="$(sanitize_segment "$output_type")"
output_root="${output_root%/}"

target="$output_root/$customer/$project/$output_type"
if [[ -d "$target" ]]; then
  action="reused"
else
  action="created"
fi

mkdir -p "$target"

management_root="$output_root/产出管理"
log_file="$management_root/folder_routing_log.md"
mkdir -p "$management_root"

timestamp="$(date '+%Y-%m-%d %H:%M:%S %z')"
{
  printf -- '- 时间：%s\n' "$timestamp"
  printf '  客户名称：%s\n' "$customer"
  printf '  项目名称：%s\n' "$project"
  printf '  产出类型名称：%s\n' "$output_type"
  printf '  动作：%s\n' "$action"
  printf '  保存文件夹：%s\n' "$target"
  if [[ -n "$reason" ]]; then
    printf '  原因：%s\n' "$reason"
  fi
} >> "$log_file"

printf 'path=%s\n' "$target"
printf 'action=%s\n' "$action"
printf 'log=%s\n' "$log_file"
