# Folder Cleanup Archiver / 文件清理归档助手

`folder-cleanup-archiver` is a reusable AI skill for Codex and Claude. It helps an agent safely scan local folders, identify cleanup and archive candidates, move stale files with verification, and keep a searchable record of where files went.

`folder-cleanup-archiver` 是一个可同时用于 Codex 和 Claude 的通用 Skill。它帮助 AI 助手安全地扫描本地文件夹，识别可清理、可备份、可归档的内容，按确认后的规则移动长期未使用文件，并维护可检索的“文件去向台账”。

Happy cleaning, and enjoy using it.

祝大家使用愉快。

---

## What It Does / 功能概览

| Capability | English | 中文 |
| --- | --- | --- |
| Disk and folder scan | Scan a folder or home directory, summarize large folders, large files, file types, and scan errors. | 扫描文件夹或用户目录，汇总大目录、大文件、文件类型和扫描异常。 |
| Cleanup classification | Classify items into cleanup, archive, keep-local, confirm-first, and do-not-touch categories. | 将文件分为可清理、可归档、本机保留、待确认、不建议手动清理等类别。 |
| Exact duplicate detection | Find exact duplicate files by content hash and estimate theoretical savings. | 基于内容哈希查找完全相同的重复文件，并估算理论可释放空间。 |
| Stale archive analysis | Identify files not accessed and not modified for a configurable period, usually six months. | 找出近 N 个月未打开且未修改的文件，默认适合分析“近半年未使用”内容。 |
| Safe archive moves | Move archive candidates into a target folder while preserving the original folder structure. | 将强归档候选移动到指定目录，并保持原始文件夹结构。 |
| Manifest verification | Verify moved files by source existence, destination existence, file size, and modified time. | 通过源路径、目标路径、文件大小和修改时间复核移动结果。 |
| Cleanup task list | Maintain Markdown and CSV task lists for ongoing cleanup work. | 持续维护 Markdown/CSV 清理任务清单。 |
| Searchable file index | Build a CSV index of deleted, archived, backed-up, missing, or user-confirmed cleaned files. | 生成可按文件名检索的 CSV 台账，记录已删除、已归档、已备份、已外移或用户确认清理的文件状态。 |

---

## Why This Skill Exists / 为什么需要这个 Skill

Cleaning a personal or work machine is risky because the agent must balance space recovery, backup discipline, project continuity, and user trust. This skill makes the process explicit and auditable:

- first scan and report;
- then classify and ask for confirmation;
- then dry-run any move;
- then execute only after approval;
- then verify and write durable records.

整理个人或工作电脑时，风险不在“删得不够快”，而在于误删资料、丢失项目上下文、清理后找不到文件去向。这个 Skill 把清理流程做成可复核、可追踪的工作流：

- 先扫描并报告；
- 再分类并等待确认；
- 移动前先 dry-run；
- 只有用户明确同意后才执行；
- 执行后复核，并把文件状态写入长期台账。

---

## Interaction Model / 交互方式

The skill is designed for a conversational agent. A typical interaction looks like this:

```text
User: My disk is almost full. Please inspect my folders first and give me a cleanup report.
Agent: Runs read-only scan, reports major space usage, duplicates, archive candidates, and risks.

User: Analyze files not opened or modified in the last six months.
Agent: Generates stale archive report by count, size, type, and folder.

User: Move the strong archive candidates into a new folder, preserving folder structure.
Agent: Runs dry-run first, reports ready/missing/conflict counts, asks for confirmation, then executes and verifies.

User: I cleaned that archive folder too.
Agent: Updates task list and search index to user-confirmed cleaned status.
```

对应中文交互通常是：

```text
用户：我的硬盘快满了，先整体探查文件，给我报告和清理建议。
助手：只读扫描，报告主要空间占用、重复文件、可归档内容和风险点。

用户：进一步分析近半年未打开或未更改的文件。
助手：按数量、容量、文件类型、所在文件夹生成强归档分析。

用户：把强归档文件移动到新文件夹，保持原文件夹结构。
助手：先 dry-run，报告 ready/missing/conflict，再等待确认，确认后执行移动并复核。

用户：这个归档文件夹我也清理完了。
助手：更新清理任务清单和文件去向索引，标记为用户确认已清理。
```

---

## Safety Rules / 安全规则

This skill is intentionally conservative.

这个 Skill 默认保守执行。

- Scanning and stale analysis are read-only.
- 扫描和长期未使用分析默认只读。
- Duplicate detection only produces candidates; it does not delete files.
- 重复文件检测只输出候选，不自动删除。
- Archive moves require a dry run before execution.
- 归档移动必须先 dry-run。
- Destructive cleanup requires explicit user confirmation in the current conversation.
- 删除、清空缓存、覆盖文件等破坏性操作必须在当前对话中得到用户明确确认。
- macOS protected folders, Docker disk images, git worktrees, databases, credentials, and project environments should be reported separately and handled cautiously.
- macOS 受保护目录、Docker 磁盘镜像、git worktree、数据库、密钥凭据、项目环境应单独报告，谨慎处理。

---

## Repository Layout / 仓库结构

```text
lynnskill/
├── README.md
├── LICENSE
├── packaging/
│   └── package.sh
├── skills/
│   └── folder-cleanup-archiver/
│       ├── SKILL.md
│       ├── agents/
│       │   └── openai.yaml
│       ├── references/
│       │   └── status_taxonomy.md
│       └── scripts/
│           ├── scan_disk.py
│           ├── analyze_stale_archive.py
│           ├── move_archive_candidates.py
│           ├── build_cleanup_index.py
│           └── update_cleanup_task_list.py
└── tests/
    └── run_smoke_test.sh
```

`SKILL.md` is the shared skill entrypoint for Codex and Claude. Codex may also use `agents/openai.yaml` for UI metadata. Claude can ignore `agents/openai.yaml`.

`SKILL.md` 是 Codex 和 Claude 共用的 Skill 入口。Codex 可以读取 `agents/openai.yaml` 作为界面元数据；Claude 可以忽略这个文件。

---

## Install / 安装

Install into Codex:

安装到 Codex：

```bash
cp -R skills/folder-cleanup-archiver ~/.codex/skills/
```

Install into Claude:

安装到 Claude：

```bash
cp -R skills/folder-cleanup-archiver ~/.claude/skills/
```

For development, use symlinks so one repository update affects both agents:

开发时建议使用软链，这样仓库更新后 Codex 和 Claude 可同时使用新版：

```bash
ln -s "$PWD/skills/folder-cleanup-archiver" ~/.codex/skills/folder-cleanup-archiver
ln -s "$PWD/skills/folder-cleanup-archiver" ~/.claude/skills/folder-cleanup-archiver
```

If the destination already exists, remove it, back it up, or replace it intentionally.

如果目标目录已经存在，请先备份、删除或明确替换。

---

## Workflow / 工作流程

Set paths:

设置路径：

```bash
SKILL_DIR="$PWD/skills/folder-cleanup-archiver"
ROOT="/path/to/scan"
AUDIT_DIR="/tmp/folder-cleanup-audit"
ARCHIVE_DIR="/tmp/folder-cleanup-archive"
```

### 1. Scan / 扫描

```bash
python3 "$SKILL_DIR/scripts/scan_disk.py" "$ROOT" --output-dir "$AUDIT_DIR"
```

Outputs include:

输出包括：

- `scan_files.csv`
- `scan_report.md`
- `dir_summary.csv`
- `type_summary.csv`
- `top_files.csv`
- `duplicate_groups.csv`
- `duplicate_files.csv`
- `scan_errors.csv`
- `scan_summary.json`

### 2. Analyze stale archive candidates / 分析长期未使用归档候选

```bash
python3 "$SKILL_DIR/scripts/analyze_stale_archive.py" \
  --scan-files "$AUDIT_DIR/scan_files.csv" \
  --output-dir "$AUDIT_DIR" \
  --months 6
```

A strong archive candidate is a file whose access time and modified time are both older than the cutoff. On macOS, access time can be approximate, so modified time should be treated as the stronger signal.

强归档候选指访问时间和修改时间都早于截止日期的文件。macOS 的访问时间可能不完全稳定，因此修改时间通常是更可靠的判断依据。

### 3. Dry-run archive move / 归档移动预演

```bash
python3 "$SKILL_DIR/scripts/move_archive_candidates.py" \
  --stale-files "$AUDIT_DIR/archive_stale_files_all.csv" \
  --root "$ROOT" \
  --target-dir "$ARCHIVE_DIR" \
  --manifest "$AUDIT_DIR/strict_stale_move_manifest.csv"
```

This does not move files. It reports whether each file is ready, missing, or conflicting.

这一步不会移动文件，只记录每个文件是 ready、missing 还是 conflict。

### 4. Execute move after confirmation / 用户确认后执行移动

```bash
python3 "$SKILL_DIR/scripts/move_archive_candidates.py" \
  --stale-files "$AUDIT_DIR/archive_stale_files_all.csv" \
  --root "$ROOT" \
  --target-dir "$ARCHIVE_DIR" \
  --manifest "$AUDIT_DIR/strict_stale_move_manifest.csv" \
  --execute
```

### 5. Verify move manifest / 复核移动结果

```bash
python3 "$SKILL_DIR/scripts/move_archive_candidates.py" \
  --verify-manifest "$AUDIT_DIR/strict_stale_move_manifest.csv"
```

### 6. Build searchable cleanup index / 生成文件去向检索索引

```bash
python3 "$SKILL_DIR/scripts/build_cleanup_index.py" \
  --output "$AUDIT_DIR/cleanup_archive_search_index.csv" \
  --archive-manifest "$AUDIT_DIR/strict_stale_move_manifest.csv"
```

If the user later confirms that the local archive folder was cleaned, add:

如果用户后续确认本机归档目录也已经清理，添加：

```bash
--archive-confirmed-cleaned
```

### 7. Update cleanup task list / 更新清理任务清单

```bash
python3 "$SKILL_DIR/scripts/update_cleanup_task_list.py" \
  --task-list-md "$AUDIT_DIR/cleanup_task_list.md" \
  --task-list-csv "$AUDIT_DIR/cleanup_task_list.csv" \
  --id CLN-004 \
  --item "stale archive files" \
  --status "已清理释放空间" \
  --current-size "path missing and user confirmed cleaned" \
  --cleaned-size "22.3 GiB released or offloaded" \
  --evidence "$AUDIT_DIR/strict_stale_move_manifest.csv" \
  --note "user confirmed archive folder cleaned"
```

---

## Status Vocabulary / 状态词汇

The skill uses consistent task and file-index statuses. See:

本 Skill 使用统一的任务状态和文件索引状态。详见：

```text
skills/folder-cleanup-archiver/references/status_taxonomy.md
```

Common examples:

常见状态包括：

- `已清理释放空间`
- `已整理待备份/外移`
- `待清理`
- `待确认`
- `不建议手动清理`
- `已归档_本机`
- `已归档_本机副本已清理_用户确认`
- `已删除_模型`
- `已删除_Office临时锁文件`

---

## Test / 测试

Run the smoke test:

运行 smoke test：

```bash
tests/run_smoke_test.sh
```

The test creates a temporary folder, scans four files, detects one exact duplicate group, finds three stale archive candidates, dry-runs a move, executes the move, verifies the manifest, builds a search index, and updates a task list.

测试会创建临时目录，扫描 4 个文件，识别 1 组精确重复文件，找到 3 个长期未使用归档候选，执行 dry-run、移动、manifest 复核、索引生成和任务清单更新。

---

## Package / 打包

Create a zip package:

生成 zip 包：

```bash
packaging/package.sh
```

The zip is written to:

生成位置：

```text
dist/lynnskill-folder-cleanup-archiver.zip
```

---

## Publish / 上传 GitHub

Create a public GitHub repository named `lynnskill`, then push:

创建名为 `lynnskill` 的 public GitHub 仓库，然后推送：

```bash
git remote add origin https://github.com/<your-username>/lynnskill.git
git push -u origin main
```

If GitHub CLI is available:

如果本机有 GitHub CLI：

```bash
gh repo create lynnskill --public --source=. --remote=origin --push
```

---

## Suggested Prompts / 推荐触发方式

English:

- "Use Folder Cleanup Archiver to scan my Downloads folder and tell me what can be archived."
- "Find files I have not opened or modified in the last six months."
- "Move the strong archive candidates to a new folder, preserving folder structure."
- "Update the cleanup task list and searchable file index after I finish cleaning."

中文：

- “用文件清理归档助手扫描我的 Downloads，告诉我哪些可以归档。”
- “找出近半年没有打开也没有修改过的文件。”
- “把强归档候选移动到新文件夹，保持原文件夹结构。”
- “我清理完一部分了，帮我更新清理任务清单和文件去向索引。”

---

## License / 许可证

MIT License.

MIT 许可证。
