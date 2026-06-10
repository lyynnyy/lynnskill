# Plan Schema

Use these fields when creating indexes, daily plans, and task cards.

## Exercise Index

Recommended columns:

- `source_pdf`: exact source file
- `pdf_page`: PDF page number
- `book_page`: printed page number, if visible
- `chapter_or_unit`
- `topic`
- `exercise_type`
- `estimated_level`
- `prerequisites`
- `target_abilities`
- `modeling_or_thinking_value`
- `risk_or_skip_reason`
- `suitability`: use values such as `core`, `review`, `stretch`, `skip`
- `notes`

Do not rely only on a table of contents. Spot-check representative pages.

## Ability Model

Include:

- learner starting point
- subject-specific stages
- observable behaviors for each stage
- selected PDF pages mapped to stages
- methods used, with citations when sourced from the web
- progression rule: what must be true before moving forward

## Daily Plan

Each day should include:

- `day`
- `date` if scheduling is requested
- `title`
- `source_pdf`
- `pdf_page`
- `theme`
- `learning_goal`
- `steps`
- `homework`: default one page
- `check_standard`
- `parent_or_teacher_notes`
- `spiral_review`
- `ability_progress`
- `estimated_time`
- `encouragement_or_reflection_prompt`

Keep daily plans small enough for a real child to finish.

## Task Card JSON

The bundled `scripts/create_task_card_pdf.py` accepts JSON in this shape:

```json
{
  "day": 1,
  "title": "From Pictures to Data",
  "source": "workbook.pdf p9",
  "duration": "15-25 min",
  "focus": "Observe, classify, count, and explain.",
  "goal": ["Identify categories", "Count each category"],
  "steps": ["Look first", "Circle categories", "Count", "Explain"],
  "check": ["Names at least two categories", "Counts accurately"],
  "notes": ["Ask the child how they know"],
  "ability": [
    {"name": "Context", "progress": "+1"},
    {"name": "Representation", "progress": "start"}
  ],
  "review": "Can the child explain before calculating?",
  "encouragement": "You are learning to see structure."
}
```

## Quality Gates

Before finalizing:

- every daily assignment traces to a PDF page
- no scheduled page appears twice unless explicitly intended as review
- task PDFs have two pages when that is the chosen format
- worksheet screenshots are legible at A4 size
- Calendar events have the intended date and time
- index updates happen after successful schedule creation
