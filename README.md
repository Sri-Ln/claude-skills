# claude-skills

Claude Code skills I've built. Each one lives in `skills/<name>/` with a `SKILL.md`
and any scripts it needs.

| Skill | What it does |
|---|---|
| [app-count](skills/app-count) | Counts job applications per day from a CSV log (today, this week, any date) |

## Install

Clone the repo, then link each skill into `~/.claude/skills/`:

```bash
git clone https://github.com/Sri-Ln/claude-skills.git
# Windows (no admin needed):
cmd //c mklink /J "%USERPROFILE%\.claude\skills\app-count" "<clone>\skills\app-count"
# macOS / Linux:
ln -s "<clone>/skills/app-count" ~/.claude/skills/app-count
```

Skills that read local data take the path from an environment variable (for example
`APPS_CSV`), so no personal data lives in this repo.
