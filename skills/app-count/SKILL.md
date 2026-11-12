---
name: app-count
description: Count job applications submitted in a day from Gmail confirmation receipts, plus rejections and assessment/interview invites received that day. Use for the nightly 11:50pm ET count and whenever the user asks "how many applications today", "how many did I apply to", "app count", "applications so far", or for a count on a specific date.
---

# Applications count

Counts the job applications submitted during one **America/New_York calendar day**,
verified from Gmail confirmation receipts, and tallies that day's rejections and
assessment/interview invites separately.

Two modes, same method:
- **Nightly:** at 11:50pm ET, count the ET day that is ending. Deliver the minimal
  format only (see Output).
- **On demand:** whenever the user asks. Always recount **from scratch** (never
  restate an earlier number) and state the as-of time, e.g. "as of 7:20pm ET".

Settings (environment variables, all optional except Gmail access):

| Variable | Meaning | Default |
|---|---|---|
| `APPS_TARGET` | Daily target | `50` |
| `APPS_LOG_DIR` | Folder for daily logs (`YYYY-MM-DD.md`) | none: skip the log and say so once |
| `APPS_CSV` | The user's own application log, used as the submission tracker | none: skip the tracker cross-check |

`Target% = applied / APPS_TARGET * 100`, rounded to a whole percent.

Cost: a verified count reads many email bodies (tens of thousands of tokens).
LinkedIn and Greenhouse bodies are mostly tracking links, so strip URLs before
reading. A subjects-only count is cheap but unreliable; never deliver one as verified.

## 1. Requirements

- **Gmail read access** to all mail and sent mail, with search (`in:anywhere`,
  `after:`/`before:`) and message bodies. Use whatever Gmail integration the session
  has (a Gmail connector or MCP server). If none is available, say so and stop.
- **Tracker (optional):** `APPS_CSV`, a CSV with a `Date Applied` column (ISO or
  `MM/DD/YYYY`) plus `Company` and `Role`. `scripts/count.py` prints per-day totals
  from it.

## 2. Collect

1. Gmail's `after:`/`before:` filters are UTC-based. For ET day `D`, run **both**
   adjacent windows and merge:
   - `in:anywhere after:D before:D+1`
   - `in:anywhere after:D+1 before:D+2`
2. Keep only messages whose **ET local date equals D**. Messages in the windows that
   carry D-1's ET date belong to D-1 (early-UTC receipts are the usual trap).
3. Dedupe by message ID.
4. Also search **sent mail** for D: direct email applications never produce a receipt.
5. Typical senders: Greenhouse (`no-reply@us.greenhouse-mail.io`), Ashby
   (`no-reply@ashbyhq.com`), Workday, Lever, Oracle HCM, Workable, ZipRecruiter,
   LinkedIn (`jobs-noreply@linkedin.com`), and company domains.
6. Read **bodies**, not just subjects, for every candidate.

## 3. Classify

### Applied (new applications only)
- One count per distinct **company + role**. Same company, different role counts
  separately, but verify with the job ID, Ashby ID, Greenhouse token, location, or
  the tracker. Never assume a same-subject pair is a resend, and never assume it's two roles.
- **Word-for-word resends count once** (some ATSs resend; ZipRecruiter sends two
  emails per apply).
- **LinkedIn + ATS pairs count once.** An Easy Apply often yields a LinkedIn receipt
  and a company-ATS receipt minutes apart for the same application.
- **Receipt date governs.** A receipt arriving on day D counts on D, even if the
  application was submitted earlier.
- **Already counted means done.** A resend of a receipt counted on an earlier day
  doesn't count again; check prior daily logs. Submitting the same requisition twice is
  one application.

### Rejections (separate tally, never inside Applied)
- Count every rejection **received on D**, for any application, old or new.
- **Role closures are not rejections.** "Position filled", "no longer available",
  "requisition cancelled", "we've closed the position": excluded. The test: does the
  email judge *the applicant's fit*, or only say *the role is gone*?
- **Application-limit bounces are rejections** ("N roles in M days" limits). The
  application was closed because of past applications.
- **"Thank you" subjects are often rejections.** Body-check every "Thank you for your
  interest / for applying" email.
- **LinkedIn trap:** "Your application to <role> at <company>" can be a rejection
  (body contains `email_jobs_application_rejected` or rejection wording). "Your
  application was sent to <company>" is the confirmation. Always body-check the first.

### Assessment / Interview pending
- Count assessment invites, screening requests, interview invites, and next-step
  bot/screening emails **received on D**, one line each: `Company — Role — type`.
- A **reminder** about an invite counted on an earlier day is not new.
- A receipt that merely **mentions** a possible next step (e.g. "you may receive a
  video interview") is not an invite.
- A request to **complete an application** is an incomplete application, not a
  screening.

### Always excluded
Follow-ups (EEO forms, hiring-process overviews, next-steps for already-counted
items), incomplete applications ("please complete"), withdrawals, job alerts,
marketing, newsletters, verification-code and identity-confirmation emails that are
steps of a counted application, program enrollments, recruiter-match/link emails,
social notifications.

## 4. Tracker gap check

If `APPS_CSV` is set, list the tracker's rows dated D that have **no Gmail receipt**.
They are not added to Applied. Report them as a gap note: "true submitted-today
total is likely X (receipts + N no-receipt)". Use the tracker the other way too: to
confirm whether a same-company pair is two roles.

## 5. Error checklist (run before delivering)

1. Distinct same-company roles collapsed into one?
2. A duplicate submission counted as new? (check tracker + prior logs)
3. A rejection counted as an application? ("Thank you…" and LinkedIn "Your application to…")
4. A role closure counted as a rejection?
5. A later-day resend counted as new?
6. A reminder counted as a new pending item?
7. Evening receipts missed? The nightly count re-triages from scratch, never reuses an in-day list.
8. No-receipt submissions left out of the gap note?
9. Boundary errors: UTC-window messages with D-1's ET date included?

If Gmail fails (rate limit, connection error), **don't guess**: report the counts as
unverified with one short note.

## 6. Output

**Nightly: exactly this, nothing else.** A one-line note is allowed only when this
count corrects a manual count given shortly before.

```
Applied today: {count}
Target%: {x}%
Rejections today: {count}
Assessment/Interview pending: {count}
```

If pending > 0, one line per item underneath: `Company — Role — assessment/screening/interview`.
If 0, add nothing.

**On demand:** the same four numbers, plus the full applied list with **every role on
its own line**, grouped by source (LinkedIn / Greenhouse / Ashby / other ATS / direct),
and the as-of time. Example header: "Today so far, as of ~7:20pm ET: 43, 86% of your
50 target."

**Daily log:** if `APPS_LOG_DIR` is set, append to `APPS_LOG_DIR/YYYY-MM-DD.md` under a
`## Nightly applications count` heading: the four lines, then bullets with the itemized
applied list, itemized rejections, dedupe/exclusion notes, the no-receipt gap with the
true-total estimate, and any correction to an earlier count with the reason. These logs
are what later days check resends against.
