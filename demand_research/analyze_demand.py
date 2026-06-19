"""Turn the collected posts + survey into demand evidence (Component 2).

Outputs, using only the standard library:
  * Post volume per event and per keyword (how big is the pain?)
  * A crude sentiment split via a small keyword lexicon
  * Willingness-to-pay distribution from the survey

Run:
    python demand_research/analyze_demand.py
"""
from __future__ import annotations

import collections
import csv
import os
import sys

# Make console output UTF-8 safe on Windows (cp950) terminals.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(__file__)
POSTS = os.path.join(HERE, "sample_posts.csv")
SURVEY = os.path.join(HERE, "survey_results.csv")

# Tiny lexicon — enough to illustrate the method, not a real NLP model.
NEGATIVE = ["搶不到", "崩潰", "心累", "好氣", "無言", "瞎", "打仗", "俱疲", "誇張", "難過", "手痛"]
INTENT_TO_PAY = ["願意", "付錢", "付小錢", "願面額"]


def _rows(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def analyze_posts() -> None:
    posts = _rows(POSTS)
    print(f"=== Demand signal from {len(posts)} posts ===")

    by_event = collections.Counter(p["event_id"] for p in posts)
    print("\nPosts per event:")
    for event, n in by_event.most_common():
        print(f"  {event:<22} {n}")

    by_keyword = collections.Counter(p["keyword"] for p in posts)
    print("\nPosts per keyword:")
    for kw, n in by_keyword.most_common():
        print(f"  {kw:<8} {n}")

    negative = sum(any(w in p["text"] for w in NEGATIVE) for p in posts)
    intent = sum(any(w in p["text"] for w in INTENT_TO_PAY) for p in posts)
    print(f"\nPosts expressing frustration: {negative}/{len(posts)} "
          f"({100*negative/len(posts):.0f}%)")
    print(f"Posts hinting at willingness to pay: {intent}/{len(posts)}")


def analyze_survey() -> None:
    if not os.path.exists(SURVEY):
        return
    rows = _rows(SURVEY)
    n = len(rows)
    print(f"\n=== Willingness to pay from {n} survey responses ===")

    willing = sum(r["willing_to_pay"] == "Yes" for r in rows)
    print(f"Would pay for instant re-release alerts: {willing}/{n} ({100*willing/n:.0f}%)")

    price = collections.Counter(r["fair_monthly_ntd"] for r in rows if r["willing_to_pay"] == "Yes")
    print("Fair monthly price (NT$) among willing payers:")
    for band, c in sorted(price.items()):
        print(f"  {band:<10} {c}")

    high_stress = sum(int(r["stress_1to5"]) >= 4 for r in rows)
    print(f"\nReported the experience as stressful (>=4/5): {high_stress}/{n} "
          f"({100*high_stress/n:.0f}%)")


if __name__ == "__main__":
    analyze_posts()
    analyze_survey()
