---
name: app-count
description: Count how many job applications were logged today, this week, or on any given day. Use when the user asks "how many applications today", "how many did I apply to", "app count", "applications this week", or for a daily breakdown of applications.
---

# App count

Counts rows in the application log CSV, grouped by the "Date Applied" column.

## Run

```bash
python "<this skill's folder>/scripts/count.py"            # today, this week, total, last 14 days
python "<this skill's folder>/scripts/count.py" --date 2026-11-10   # one specific day
python "<this skill's folder>/scripts/count.py" --days 30            # longer breakdown
```

The CSV path comes from the `APPS_CSV` environment variable. If it's unset, tell the
user to set it (for Claude Code: `"env": {"APPS_CSV": "<path>"}` in `~/.claude/settings.json`).

## Reply

One or two short lines, e.g. "10 today, 34 this week (376 total)." Add the per-day list
only if the user asked for a breakdown or a range. If they ask about a day by name
("yesterday", "Monday"), work out the date and use `--date`.
