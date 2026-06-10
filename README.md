# Lynn Skill / Lynn 的 Skill 仓库

This repository collects reusable AI skills for Codex and Claude. Each skill has its own folder, scripts, references, and detailed bilingual documentation.

这个仓库用于收纳 Lynn 可复用的 AI Skills，面向 Codex 和 Claude。每个 skill 都有独立目录、脚本、参考资料和中英文详细说明。

## Skills / Skill 列表

| Skill | Name / 名称 | What it does / 用途 |
| --- | --- | --- |
| [folder-cleanup-archiver](skills/folder-cleanup-archiver/README.md) | Folder Cleanup Archiver / 文件清理归档助手 | Safely scan local folders, identify cleanup/archive candidates, move stale files with verification, and maintain a searchable cleanup index. / 安全扫描本地文件夹，识别可清理和可归档内容，复核归档移动结果，并维护可检索的清理台账。 |
| [project-folder-router](skills/project-folder-router/README.md) | Project Output Manager / 项目产出管理助手 | Route generated deliverables into customer/project/output-type folders, avoid duplicate saved files, and record routing decisions. / 将生成的交付物路由到客户、项目、产出类型文件夹，避免重复保存，并记录路由决策。 |
| [pdf-learning-planner](skills/pdf-learning-planner/README.md) | PDF Learning Planner / PDF 学习计划助手 | Turn study PDFs into subject-aware, evidence-based daily learning plans with task-card PDFs, used-page indexes, and Calendar scheduling. / 将学习资料 PDF 转成学科识别、证据化方法、每日作业、任务卡 PDF、已用页面索引和日程安排。 |

## Repository Layout / 仓库结构

```text
lynnskill/
├── README.md
├── LICENSE
├── packaging/
│   └── package.sh
├── skills/
│   └── <skill-name>/
│       ├── README.md
│       ├── SKILL.md
│       ├── agents/
│       ├── references/
│       └── scripts/
└── tests/
    └── run_smoke_test.sh
```

## Install A Skill / 安装某个 Skill

Install into Codex:

安装到 Codex：

```bash
cp -R skills/<skill-name> ~/.codex/skills/
```

Install into Claude:

安装到 Claude：

```bash
cp -R skills/<skill-name> ~/.claude/skills/
```

For development, use symlinks:

开发时可以用软链：

```bash
ln -s "$PWD/skills/<skill-name>" ~/.codex/skills/<skill-name>
ln -s "$PWD/skills/<skill-name>" ~/.claude/skills/<skill-name>
```

## Notes / 说明

- `SKILL.md` is the agent-facing entrypoint.
- `README.md` is the human-facing documentation page.
- `agents/openai.yaml` is optional Codex UI metadata; Claude can ignore it.
- Scripts use Python standard library whenever possible for portability.

- `SKILL.md` 是给 AI agent 读取的入口文件。
- `README.md` 是给人看的说明页面。
- `agents/openai.yaml` 是 Codex 可用的界面元数据；Claude 可以忽略。
- 脚本尽量只使用 Python 标准库，便于跨环境运行。

Happy building, and enjoy using these skills.

祝大家使用愉快。
