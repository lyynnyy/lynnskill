# Project Output Manager / 项目产出管理助手

`project-folder-router` is a reusable AI skill for Codex and Claude. It helps an agent decide where project deliverables should be saved, avoid duplicate files, create or reuse customer/project/output-type folders, and record every routing decision.

`project-folder-router` 是一个可同时用于 Codex 和 Claude 的通用 Skill。它帮助 AI 助手管理项目产出目录：判断交付物应该保存在哪里，避免重复保存，按客户、项目、产出类型创建或复用文件夹，并记录每一次路由决策。

Enjoy managing outputs with less folder chaos.

祝大家使用愉快。

---

## Quick Summary / 快速了解

| Item | English | 中文 |
| --- | --- | --- |
| Simple name | Project Output Manager | 项目产出管理助手 |
| Skill id | `project-folder-router` | `project-folder-router` |
| Works with | Codex and Claude | Codex 和 Claude |
| Main goal | Route project files into a stable output folder system. | 将项目产出文件稳定路由到规范文件夹体系。 |
| Default root | `/Users/lynn/项目产出` | `/Users/lynn/项目产出` |
| Risk control | Check duplicates before saving. | 保存前先查重，避免重复文件。 |

---

## What It Does / 功能概览

| Capability | English | 中文 |
| --- | --- | --- |
| Folder routing | Choose or create a folder from customer, project, and output type. | 根据客户、项目、产出类型选择或创建保存文件夹。 |
| Duplicate-aware saving | Compare file content under the output root before saving. | 保存前按文件内容检查项目产出目录下是否已存在相同文件。 |
| Reuse existing folders | Reuse existing customer/project/output-type folders when appropriate. | 优先复用已有客户、项目、产出类型文件夹。 |
| Safe copying | Copy files only when explicitly requested with `--copy`. | 只有明确使用 `--copy` 时才复制文件。 |
| Routing log | Record every decision in `folder_routing_log.md`. | 将每次路由决策记录到 `folder_routing_log.md`。 |
| Caller contract | Return machine-readable status for other skills to consume. | 输出结构化状态，便于其他 skill 接入。 |

---

## Why This Skill Exists / 为什么需要这个 Skill

Project deliverables often arrive from many workflows: solution decks, PPT files, documents, spreadsheets, prototypes, output plans, WeWork attachments, and generated artifacts. Without a routing rule, files scatter across Downloads, desktop folders, chat caches, and temporary output paths.

项目产出通常来自很多入口：解决方案、PPT、文档、表格、原型、产出计划、企微附件、AI 生成文件等。如果没有统一路由规则，文件很容易散落在 Downloads、桌面、聊天缓存和临时目录里。

This skill makes the destination decision explicit:

- know the business context;
- check whether the same file already exists;
- choose the right customer/project/output-type folder;
- copy only when explicitly requested;
- record the decision for future lookup.

这个 Skill 把“文件应该放哪里”变成可复核流程：

- 先明确业务上下文；
- 再检查相同文件是否已存在；
- 决定客户、项目、产出类型文件夹；
- 只有明确要求时才复制；
- 记录路由决策，方便后续查找。

---

## Interaction Model / 交互方式

Typical English interaction:

```text
User: Save this generated solution deck under the right project output folder.
Agent: Asks for or infers customer, project, and output type.
Agent: Checks whether the same file already exists under the output root.
Agent: If duplicate exists, returns existing_file and does not save another copy.
Agent: If no duplicate exists, returns save_folder or copies the file when explicitly requested.
```

典型中文交互：

```text
用户：把这个生成的解决方案保存到正确的项目产出文件夹。
助手：确认客户名称、项目名称、产出类型。
助手：检查项目产出目录下是否已经有相同文件。
助手：如果已存在，返回 existing_file，不重复保存。
助手：如果不存在，返回 save_folder；只有用户明确要求时才复制文件。
```

---

## Required Inputs / 必填信息

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

调用时必须提供：

- 客户名称
- 项目名称
- 产出类型名称

可选但有帮助的信息：

- 源文件路径
- 交付物标题
- 截止时间或使用场景
- 来源 skill 或对话上下文
- 保存原因

If required business context is missing, the agent should ask one concise clarification before creating folders.

如果必要业务信息缺失，助手应先问一个简短澄清问题，再创建文件夹。

---

## Safety Rules / 安全规则

- Do not invent customer, project, or output type names when the business meaning is unclear.
- Do not save duplicate files when the same content already exists under the output root.
- Do not copy a source file unless the user explicitly asks or the caller passes `--copy`.
- Do not overwrite same-name different-content files.
- Always record routing decisions in the routing log.

- 业务含义不清楚时，不要编造客户、项目或产出类型名称。
- 项目产出目录下已有相同内容文件时，不要重复保存。
- 除非用户明确要求或调用方传入 `--copy`，否则不要复制源文件。
- 不覆盖同名但内容不同的文件。
- 每次路由决策都要写入路由日志。

---

## Files / 文件结构

```text
project-folder-router/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
└── scripts/
    ├── ensure_project_output_folder.sh
    └── route_output_file.sh
```

---

## Workflow / 工作流程

Set the skill path:

设置 skill 路径：

```bash
SKILL_DIR="$PWD/skills/project-folder-router"
```

### 1. Ensure a destination folder / 创建或复用保存文件夹

```bash
"$SKILL_DIR/scripts/ensure_project_output_folder.sh" \
  --customer "客户名称" \
  --project "项目名称" \
  --output-type "产出类型名称" \
  --reason "记录来源或保存原因"
```

Output:

输出：

```text
path=<final folder>
action=created|reused
log=<routing log path>
```

### 2. Route a generated file without copying / 路由文件但不复制

```bash
"$SKILL_DIR/scripts/route_output_file.sh" \
  --source-file "/path/to/generated-file.pptx" \
  --customer "客户名称" \
  --project "项目名称" \
  --output-type "产出类型名称" \
  --reason "记录来源或保存原因"
```

If the same file already exists:

如果相同文件已经存在：

```text
status=file_exists
should_save=0
existing_file=<path>
```

If no same file exists:

如果不存在相同文件：

```text
status=save_needed
should_save=1
save_folder=<path>
```

### 3. Route and copy after explicit request / 明确要求后路由并复制

```bash
"$SKILL_DIR/scripts/route_output_file.sh" \
  --source-file "/path/to/generated-file.pptx" \
  --customer "客户名称" \
  --project "项目名称" \
  --output-type "产出类型名称" \
  --copy \
  --reason "保存生成文件"
```

When `--copy` is used, the script copies the file into the routed folder. If a same-name different-content file already exists, it writes to a unique file name.

使用 `--copy` 时，脚本会把文件复制到路由后的文件夹。如果同名但内容不同的文件已经存在，会自动生成不冲突的新文件名。

---

## Known Folder Mappings / 已知目录映射

Prefer these mappings when context matches:

上下文匹配时优先使用这些映射：

- 达美乐: customer `达美乐`, project `客户拜访`, output type `项目介绍材料`
- 德克士 AI POC: customer `德克士`, project `AI POC`, output type `解决方案`
- 泸州老窖新增培训人天评估: customer `泸州老窖`, project `培训项目`, output type `人天评估`
- 泸州老窖培训课件 / 作业点评: customer `泸州老窖`, project `培训项目`, output type `培训课件` or `作业点评`
- 无限极材料修改: customer `无限极`, project `客户拜访`, output type `交付材料`
- 伊利销售卖货业务流程埋点更新: customer `伊利`, project `销售卖货`, output type `埋点更新`
- CDP+MA 演示原型: customer `sensors`, project `CDP+MA`, output type `原型`

---

## Test / 测试

Run the repository smoke test from the repository root:

在仓库根目录运行 smoke test：

```bash
tests/run_smoke_test.sh
```

The smoke test verifies both folder creation and duplicate-aware file routing with a temporary output root.

smoke test 会使用临时目录验证文件夹创建、文件复制、重复文件识别和路由日志。

---

## Suggested Prompts / 推荐触发方式

English:

- "Use Project Output Manager to route this generated PPT to the right customer/project folder."
- "Check whether this file already exists under my project output folder before saving it."
- "Create a project output folder for customer X, project Y, output type Z."

中文：

- “用项目产出管理助手把这个生成的 PPT 路由到正确的客户/项目文件夹。”
- “保存前先检查项目产出目录下是否已经有相同文件。”
- “帮我为客户 X、项目 Y、产出类型 Z 创建项目产出文件夹。”

---

## License / 许可证

MIT License.

MIT 许可证。
