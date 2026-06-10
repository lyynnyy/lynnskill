---
name: pdf-learning-planner
description: Create evidence-based learning plans from education PDFs and schedule them. Use when Codex is given curriculum, workbook, exam, textbook, or study-material PDFs and asked to identify the subject, inspect tables of contents, index exercises, research current global learning methods, build a learner ability model, choose suitable pages, produce daily homework/task cards, generate A4 worksheet PDFs, maintain used-page indexes, create Calendar events, or set up recurring task-generation automations.
---

# PDF Learning Planner

## Overview

Turn study PDFs into an executable learning system: subject detection, page index, evidence-based ability model, daily plan, A4 task PDFs, scheduling, and used-page tracking.

Use the user's language for final plans. Preserve exact file paths, page numbers, citations, commands, and API names.

## Core Workflow

1. **Set up project state.** Work inside the user's material folder. Create or reuse planning files such as `learning_findings.md`, `learning_plan.md`, `scheduled_pages_index.json`, and an output folder for rendered cards. Do not delete source PDFs.
2. **Inspect PDFs before planning.** Identify page count, dimensions, table-of-contents pages, text layer availability, and scan quality. For large scanned PDFs, render TOC pages and representative samples instead of trying to OCR everything at once.
3. **Detect the subject and level.** Use title, TOC, sample pages, exercise types, vocabulary, and the learner profile. If the learner's level is underspecified, infer conservatively from the material and ask only when a wrong assumption would make the plan unsafe or useless.
4. **Build a page-level exercise index.** Record source PDF, PDF page, book page when known, chapter, topic, exercise type, estimated level, target ability, modeling/thinking value, and suitability notes.
5. **Research current learning methods.** When recommending methods or claiming "advanced", "latest", "best practice", or "evidence-based", browse current web sources. Prefer primary or authoritative sources. See `references/evidence-search-policy.md`.
6. **Create an ability model.** Map the material into a staged model for the detected subject. Use `references/subject-ability-models.md` as a starting point, then adapt to the actual PDF and learner.
7. **Design the plan.** Produce a plan with objectives, daily steps, one-page homework, check standards, parent/teacher notes, spiral review, and cumulative ability progress. Use `references/plan-schema.md`.
8. **Generate task artifacts when requested.** Create A4 portrait PDFs where page 1 is a task card and page 2 is the full worksheet screenshot, unless the user requests a different format. Keep worksheet pages clear and large.
9. **Schedule only after indexing.** Before creating any daily task, check `scheduled_pages_index.json` or the user's chosen index. Skip pages already recorded as scheduled. Record a page only after Calendar/task creation succeeds. See `references/scheduling-workflow.md`.
10. **Verify before finishing.** Check generated PDFs, created events, automation config, and index updates. Report exact paths and any limitations.

## Output Standards

- Keep plans practical: one daily page by default, 15-30 minutes unless the user specifies otherwise.
- Separate learning goals from answer checking. Include process checks such as "can explain why this operation/model applies".
- Prefer spiral and interleaved sequencing over blocks of near-identical pages.
- Avoid overloading the child. Put stretch tasks after confidence-building tasks.
- Cite web sources used for learning-method recommendations.
- Preserve source traceability: every assignment must point back to a source PDF page.

## Resource Guide

- `references/evidence-search-policy.md`: how to search and evaluate learning-method evidence.
- `references/subject-ability-models.md`: reusable ability-model templates by subject.
- `references/plan-schema.md`: fields for indexes, daily plans, task cards, and checks.
- `references/scheduling-workflow.md`: Calendar, automation, and used-page index rules.
- `scripts/build_pdf_page_manifest.py`: create a basic PDF page manifest and optional rendered sample pages.
- `scripts/create_task_card_pdf.py`: generate a 2-page A4 task card PDF from JSON and a worksheet image.
- `scripts/calendar_eventkit.swift`: create cloud Calendar events through macOS EventKit on macOS when Calendar scheduling is requested.

Load only the reference files needed for the current task.
