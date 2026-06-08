---
name: project-folder-router
description: Use in Codex or Claude when the user or another skill needs to manage project output folders, route generated deliverables, check whether a file already exists by content, create or reuse customer/project/output-type folders, or record where a solution, PPT, document, workbook, prototype, or other project artifact should be saved.
---

# Project Output Manager

## Purpose

Own the file and folder-routing decision for project deliverables. Given `客户名称 / 项目名称 / 产出类型名称`, and optionally an incoming source file, first check whether the same file already exists under the output root. If the file exists, record that status and avoid saving a duplicate. If it does not exist, choose or create the destination folder and record the routing decision.

## Runtime Compatibility

Use this skill in both Codex and Claude. Resolve `SKILL_DIR` as the absolute path to this `project-folder-router` folder before running scripts:

```bash
SKILL_DIR="/absolute/path/to/project-folder-router"
```

In Claude Code, `${CLAUDE_SKILL_DIR}` may already point to the skill folder. In Codex, use the installed skill path or repository path. If neither environment variable is available, inspect the loaded skill location and use that folder.

## Default Paths

Default output root:

```text
/Users/lynn/项目产出
```

Default management directory:

```text
/Users/lynn/项目产出/产出管理
```

Default routing log:

```text
/Users/lynn/项目产出/产出管理/folder_routing_log.md
```

For tests, demos, or non-Lynn machines, always pass `--output-root`.

## Required Inputs

Callers must provide:

- `客户名称`
- `项目名称`
- `产出类型名称`

Optional but useful:

- source file path
- deliverable title
- deadline or usage occasion
- source skill or conversation context
- reason the file needs saving

If required business context is missing or ambiguous, ask one concise clarification before creating a folder. Do not invent customer, project, or output type names.

## Routing Workflow

1. If an incoming source file path is provided, check exact file duplication before folder creation:
   - compare the source file against every regular file under the output root;
   - use content equality, not just filename equality;
   - if an identical file exists, return `status=file_exists`, record the existing file path, and do not save a duplicate.
2. Normalize folder segments:
   - replace `/`, `:`, and newlines with safe separators;
   - trim leading and trailing spaces;
   - keep Chinese, English, numbers, spaces, `+`, and common business abbreviations.
3. Inspect or create:
   - customer folder;
   - project folder;
   - output-type folder.
4. Do not use a deliverable title as the project name by default. Use business context such as `客户拜访`, `培训项目`, `AI POC`, `销售卖货`, or `CDP+MA`.
5. Record every decision in `folder_routing_log.md`.

## Scripts

Use this script when only a destination folder is needed:

```bash
python3 --version >/dev/null
"${SKILL_DIR}/scripts/ensure_project_output_folder.sh" \
  --customer "客户名称" \
  --project "项目名称" \
  --output-type "产出类型名称" \
  --reason "记录来源或保存原因"
```

It creates or reuses:

```text
<output-root>/<客户名称>/<项目名称>/<产出类型名称>
```

It prints:

- `path`: final absolute folder path
- `action`: `created` or `reused`
- `log`: routing log path

Use this script when a caller has an actual file to route:

```bash
"${SKILL_DIR}/scripts/route_output_file.sh" \
  --source-file "/path/to/generated-file.pptx" \
  --customer "客户名称" \
  --project "项目名称" \
  --output-type "产出类型名称" \
  --reason "记录来源或保存原因"
```

Default behavior is duplicate-aware routing only:

- if the same file already exists under the output root, print `status=file_exists` and `should_save=0`;
- if no same file exists, print `status=save_needed`, `should_save=1`, and `save_folder=<absolute path>`.

If the caller explicitly wants the script to copy the file after routing, add `--copy`:

```bash
"${SKILL_DIR}/scripts/route_output_file.sh" \
  --source-file "/path/to/generated-file.pptx" \
  --customer "客户名称" \
  --project "项目名称" \
  --output-type "产出类型名称" \
  --copy \
  --reason "保存生成文件"
```

When `--copy` is used, the script copies the file into the routed folder and avoids overwriting same-name different-content files.

## Test Command

For dry verification, pass a temporary output root:

```bash
"${SKILL_DIR}/scripts/ensure_project_output_folder.sh" \
  --output-root "/private/tmp/project-output-manager-test" \
  --customer "测试客户" \
  --project "测试项目" \
  --output-type "解决方案" \
  --reason "verification"
```

## Caller Contract

When another skill calls this skill:

1. Provide the three required business fields.
2. If a generated file already exists on disk, provide its absolute source file path.
3. Let this skill inspect existing files first.
4. If `status=file_exists`, do not save or copy another duplicate; record `文件已存在：<existing_file>`.
5. If `status=save_needed`, use `save_folder` as the destination, or use `saved_file` when `--copy` was explicitly requested.
6. Record `项目产出文件夹：<absolute path>` or `文件已存在：<absolute path>` in the caller's task card, ledger, or final delivery note.

Move or copy a generated file only when the caller explicitly requests that operation. This skill never saves a duplicate when the same file already exists under the output root.

## Known Folder Mappings

Prefer these mappings when the context matches:

- 达美乐: customer `达美乐`, project `客户拜访`, output type `项目介绍材料`
- 德克士 AI POC: customer `德克士`, project `AI POC`, output type `解决方案`
- 泸州老窖新增培训人天评估: customer `泸州老窖`, project `培训项目`, output type `人天评估`
- 泸州老窖培训课件 / 作业点评: customer `泸州老窖`, project `培训项目`, output type `培训课件` or `作业点评`
- 无限极材料修改: customer `无限极`, project `客户拜访`, output type `交付材料`
- 伊利销售卖货业务流程埋点更新: customer `伊利`, project `销售卖货`, output type `埋点更新`
- CDP+MA 演示原型: customer `sensors`, project `CDP+MA`, output type `原型`
