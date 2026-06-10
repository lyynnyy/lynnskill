# Scheduling Workflow

Use this reference when the user asks to create daily tasks, reminders, Calendar events, recurring generation, or automations.

## Rules

1. Search for an automation tool first when creating recurring task generation.
2. Keep a used-page index such as `scheduled_pages_index.json`.
3. Check the index before generating a new task.
4. Skip pages whose `page_key` is already recorded as `scheduled`.
5. Generate the PDF/artifact before creating the event.
6. Record the page in the index only after the Calendar/task creation succeeds.
7. Store event identifiers, calendar/source identifiers, generated PDF path, and creation time.
8. If Calendar/task creation fails, leave the page unscheduled.

## Index Entry

```json
{
  "status": "scheduled",
  "day": 1,
  "page_key": "workbook.pdf#p9",
  "source_pdf": "workbook.pdf",
  "pdf_page": 9,
  "scheduled_date": "2026-06-11",
  "event_start_time": "07:30",
  "event_duration_minutes": 60,
  "calendar_name": "EVA MATH",
  "calendar_event_uid": "event id",
  "calendar_source": "iCloud",
  "calendar_source_type": "calDAV",
  "generated_pdf": "/absolute/path/day01.pdf",
  "created_at": "2026-06-10T20:30:00"
}
```

## Calendar Guidance

For macOS Calendar:

- AppleScript can create events but does not expose reliable account/source selection.
- Use EventKit when the user needs iCloud or CalDAV calendars.
- The bundled `scripts/calendar_eventkit.swift` creates events in a cloud source when available.
- Calendar APIs may not expose true file attachments. If so, write the PDF as the event URL and in notes, and state the limitation.

## Recurring Generation

For nightly generation:

- Trigger time is the creation time, not the learning time.
- Example: run at 20:30 to create the next day's 07:30 learning event.
- If an existing schedule already has a latest scheduled date, use the next calendar day after that latest date.
- Include the exact command to run in the automation prompt.
- Make the prompt self-contained: where to run, which index to check, how to handle duplicates, and what to report.

## Verification

Verify:

- automation config is active and points at the correct workspace
- Calendar event time is not accidentally all-day
- the event URL opens the generated PDF path
- the index contains only successful schedule entries
- the next unscheduled page/date is correct
