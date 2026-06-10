# PDF Learning Planner / PDF 学习计划助手

`pdf-learning-planner` is a reusable AI skill for Codex and Claude. It helps an agent turn education PDFs into subject-aware, evidence-based learning plans with exercise indexes, ability models, daily homework, A4 task-card PDFs, used-page tracking, and Calendar scheduling.

`pdf-learning-planner` 是一个可同时用于 Codex 和 Claude 的通用 Skill。它帮助 AI 助手把教材、练习册、试卷或学习资料 PDF 转化为可执行的学习系统：识别学科、建立题目索引、检索权威学习方法、设计能力模型、安排每日作业、生成 A4 任务卡 PDF、维护已用页面索引，并创建日程。

Enjoy turning study materials into calm daily progress.

祝大家使用愉快。

---

## Quick Summary / 快速了解

| Item | English | 中文 |
| --- | --- | --- |
| Simple name | PDF Learning Planner | PDF 学习计划助手 |
| Skill id | `pdf-learning-planner` | `pdf-learning-planner` |
| Works with | Codex and Claude | Codex 和 Claude |
| Main goal | Convert study PDFs into scheduled learning plans. | 把学习资料 PDF 转成可排期执行的学习计划。 |
| Default output | Index, plan, task cards, and schedule records. | 题目索引、学习计划、任务卡和日程记录。 |
| Risk control | Verify pages, sources, schedule entries, and used-page indexes. | 复核页码、证据来源、日程和已用页面索引。 |

---

## What It Does / 功能概览

| Capability | English | 中文 |
| --- | --- | --- |
| PDF inspection | Read PDF metadata, page count, dimensions, table of contents, text layer, and scan quality. | 读取 PDF 页数、尺寸、目录、文本层和扫描质量。 |
| Subject detection | Identify whether the material is math, language arts, science, history, language learning, or another subject. | 判断资料属于数学、语文/阅读、科学、历史、语言学习或其他学科。 |
| Exercise indexing | Build page-level indexes with topic, level, ability target, suitability, and source traceability. | 建立页级题目索引，记录主题、水平、能力点、适配性和来源页码。 |
| Evidence search | Search current authoritative learning-method sources when the plan claims evidence-based or advanced methods. | 当计划需要科学依据或先进方法时，检索当前权威学习方法来源。 |
| Ability modeling | Build a subject-specific ability model before assigning homework. | 先建立学科能力模型，再安排作业。 |
| Daily planning | Produce daily goals, steps, one-page homework, check standards, notes, review, and ability progress. | 生成每日目标、步骤、1 页作业、检查标准、注意事项、复盘和能力累计。 |
| Task-card PDF | Generate a two-page A4 PDF: page 1 task card, page 2 full worksheet screenshot. | 生成 2 页 A4 PDF：第一页任务卡，第二页完整题页截图。 |
| Scheduling | Create Calendar events and maintain a used-page index to avoid duplicate assignments. | 创建日程并维护已排页面索引，避免重复使用同一页。 |

---

## Why This Skill Exists / 为什么需要这个 Skill

Parents, teachers, and learners often have useful PDFs but still need to decide:

- which pages match the learner's current level;
- which skills the material is actually training;
- how to sequence pages without overwhelming the learner;
- how to apply sound learning methods such as spiral practice, interleaving, retrieval, CPA, project-based learning, and formative assessment;
- how to turn a plan into daily tasks that actually happen.

家长、老师和学习者手里常常有不错的 PDF 资料，但真正困难的是：

- 哪些页面适合当前水平；
- 每页到底训练什么能力；
- 如何排序才不会过难或过于机械；
- 如何把螺旋式学习、交错练习、提取练习、CPA、项目式学习、形成性评价等方法落到具体题目；
- 如何把计划变成每天真的会执行的任务。

This skill makes that workflow explicit and reusable.

这个 Skill 把这套流程沉淀成可复用工作流。

---

## Interaction Model / 交互方式

Typical English interaction:

```text
User: Use this workbook PDF to make a two-week learning plan for my child.
Agent: Inspects the PDF, identifies subject and level, builds an exercise index, searches learning-method evidence, proposes an ability model, and creates a daily plan.

User: Generate the first daily task card and schedule the next tasks.
Agent: Creates a two-page A4 task PDF, writes a Calendar event, and records the used PDF page in the index.
```

典型中文交互：

```text
用户：根据这份 PDF，给孩子做一个两周学习计划。
助手：读取 PDF，识别学科和难度，建立题目索引，检索学习方法依据，设计能力模型，并生成每日计划。

用户：生成第一天任务卡，并把后续任务排进日程。
助手：生成 2 页 A4 任务 PDF，创建日程，并把已用 PDF 页面写入索引。
```

---

## Safety and Quality Rules / 安全与质量规则

- Do not plan from the title alone; inspect the table of contents and sample pages.
- Do not claim "latest", "advanced", or "evidence-based" methods without current web research.
- Do not assign pages without recording source PDF and page number.
- Do not reuse a scheduled page unless the user explicitly asks for review.
- Record a page in the used-page index only after task or Calendar creation succeeds.
- State platform limits clearly, for example Calendar APIs may support a file URL but not a true attachment.

- 不要只看标题就制定计划；必须检查目录和样本页。
- 没有联网检索时，不要声称使用了“最新”“先进”“科学证据”方法。
- 每日作业必须注明来源 PDF 和页码。
- 除非用户明确要求复习，否则不要重复安排已进入日程的页面。
- 只有任务或日程创建成功后，才把页面写入已用索引。
- 对平台限制要明确说明，例如某些 Calendar API 只能写入文件链接，不能创建真正附件。

---

## Files / 文件结构

```text
pdf-learning-planner/
├── README.md
├── SKILL.md
├── requirements.txt
├── agents/
│   └── openai.yaml
├── assets/
│   └── task-card-template.json
├── references/
│   ├── evidence-search-policy.md
│   ├── plan-schema.md
│   ├── scheduling-workflow.md
│   └── subject-ability-models.md
└── scripts/
    ├── build_pdf_page_manifest.py
    ├── calendar_eventkit.swift
    └── create_task_card_pdf.py
```

`SKILL.md` is the shared skill entrypoint for Codex and Claude. Codex may also use `agents/openai.yaml` for UI metadata. Claude can ignore `agents/openai.yaml`.

`SKILL.md` 是 Codex 和 Claude 共用的 Skill 入口。Codex 可以读取 `agents/openai.yaml` 作为界面元数据；Claude 可以忽略这个文件。

---

## Runtime Notes / 运行环境说明

- `create_task_card_pdf.py` requires Pillow. Install with `python3 -m pip install -r requirements.txt`.
- `build_pdf_page_manifest.py` works without Poppler, but `pdfinfo` and `pdftoppm` improve metadata extraction and page rendering.
- `calendar_eventkit.swift` is macOS-only and requires Calendar permission.

- `create_task_card_pdf.py` 需要 Pillow，可用 `python3 -m pip install -r requirements.txt` 安装。
- `build_pdf_page_manifest.py` 没有 Poppler 也能生成基础 manifest；如果安装了 `pdfinfo` 和 `pdftoppm`，可以读取更多 PDF 元数据并渲染页面。
- `calendar_eventkit.swift` 仅适用于 macOS，并需要 Calendar 权限。

---

## Install / 安装

Install into Codex:

安装到 Codex：

```bash
cp -R skills/pdf-learning-planner ~/.codex/skills/
```

Install into Claude:

安装到 Claude：

```bash
cp -R skills/pdf-learning-planner ~/.claude/skills/
```

For development, use symlinks so one repository update affects both agents:

开发时建议使用软链，这样仓库更新后 Codex 和 Claude 可同时使用新版：

```bash
ln -s "$PWD/skills/pdf-learning-planner" ~/.codex/skills/pdf-learning-planner
ln -s "$PWD/skills/pdf-learning-planner" ~/.claude/skills/pdf-learning-planner
```

If the destination already exists, remove it, back it up, or replace it intentionally.

如果目标目录已经存在，请先备份、删除或明确替换。

---

## Workflow / 工作流程

Set the skill path:

设置 skill 路径：

```bash
SKILL_DIR="$PWD/skills/pdf-learning-planner"
```

### 1. Build a PDF manifest / 建立 PDF 基础清单

```bash
python3 "$SKILL_DIR/scripts/build_pdf_page_manifest.py" \
  "/path/to/workbook.pdf" \
  --sample-pages 1-8,15,20 \
  --render-dir "/tmp/pdf-learning-rendered" \
  --output "/tmp/pdf-learning-manifest.json"
```

Use the rendered pages to inspect the table of contents and representative exercises.

用渲染页面检查目录和代表性题目。

### 2. Create a task-card PDF / 生成任务卡 PDF

Prepare a JSON file using `assets/task-card-template.json`, then run:

先按 `assets/task-card-template.json` 准备 JSON 文件，再运行：

```bash
python3 "$SKILL_DIR/scripts/create_task_card_pdf.py" \
  --plan-json "/path/to/day01.json" \
  --worksheet-image "/path/to/worksheet-page.png" \
  --output-pdf "/path/to/day01-task.pdf"
```

The output is a two-page A4 portrait PDF.

输出是 2 页 A4 竖版 PDF。

### 3. Create a cloud Calendar event on macOS / 在 macOS 创建云日历事件

```bash
xcrun swift "$SKILL_DIR/scripts/calendar_eventkit.swift" create-event \
  "EVA MATH" \
  "EVA MATH Day 1" \
  "Task notes and PDF link" \
  "file:///path/to/day01-task.pdf" \
  2026 6 11 7 30 60
```

This uses EventKit and prefers a cloud source such as iCloud/CalDAV when available.

这个脚本使用 EventKit，并在可用时优先写入 iCloud/CalDAV 等云日历源。

---

## References / 参考资料

- `references/evidence-search-policy.md`: evidence search rules and source priority.
- `references/subject-ability-models.md`: ability-model templates for math, reading, science, history, and language learning.
- `references/plan-schema.md`: index, daily plan, and task-card schema.
- `references/scheduling-workflow.md`: Calendar, automation, and used-page index workflow.

- `references/evidence-search-policy.md`：学习方法证据检索规则和来源优先级。
- `references/subject-ability-models.md`：数学、阅读、科学、历史、语言学习等能力模型模板。
- `references/plan-schema.md`：索引、每日计划和任务卡字段规范。
- `references/scheduling-workflow.md`：日程、自动任务和已用页面索引工作流。
