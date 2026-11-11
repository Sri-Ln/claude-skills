"""Count job applications per day from a CSV log.

Reads the CSV at $APPS_CSV. Expects a "Date Applied" column; dates may be ISO
(2026-11-11) or US style (11/11/2026). Other columns are ignored.
"""
import argparse
import csv
import datetime as dt
import os
import sys
from collections import Counter


def parse_date(s):
    s = (s or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", help="count a single day (YYYY-MM-DD or MM/DD/YYYY)")
    ap.add_argument("--days", type=int, default=14, help="days in the breakdown (default 14)")
    a = ap.parse_args()

    path = os.environ.get("APPS_CSV")
    if not path:
        sys.exit("APPS_CSV is not set. Point it at your applications CSV.")
    if not os.path.exists(path):
        sys.exit(f"No file at APPS_CSV={path}")

    with open(path, encoding="utf-8-sig", newline="") as f:
        days = Counter(d for d in (parse_date(r.get("Date Applied")) for r in csv.DictReader(f)) if d)

    today = dt.date.today()
    if a.date:
        d = parse_date(a.date)
        if not d:
            sys.exit(f"Can't read date: {a.date}")
        print(f"{d.isoformat()}  {days.get(d, 0)}")
        return

    week_start = today - dt.timedelta(days=today.weekday())
    print(f"TODAY={days.get(today, 0)}")
    print(f"THIS_WEEK={sum(n for d, n in days.items() if d >= week_start)}")
    print(f"TOTAL={sum(days.values())}")
    for i in range(a.days - 1, -1, -1):
        d = today - dt.timedelta(days=i)
        print(f"{d.isoformat()} {d.strftime('%a')}  {days.get(d, 0)}")


if __name__ == "__main__":
    main()
