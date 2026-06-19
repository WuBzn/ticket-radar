"""Demand-evidence collector (Component 2).

By default this runs OFFLINE on a small synthetic sample (sample_posts.csv) so the
methodology is fully reproducible without scraping anyone. The `--live` path shows
the responsible shape of a real collector — it checks robots.txt and rate-limits —
but is intentionally left as a stub so this repo never hammers a real forum.

Usage:
    python demand_research/scrape_forums.py            # offline, uses the sample
    python demand_research/scrape_forums.py --live URL # template only (raises)
"""
from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.politeness import RateLimiter, can_fetch  # noqa: E402

SAMPLE = os.path.join(os.path.dirname(__file__), "sample_posts.csv")


def collect_offline(path: str = SAMPLE) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def collect_live(base_url: str) -> list[dict]:
    """Template for a polite live collector. Not implemented on purpose."""
    if not can_fetch(base_url):
        raise SystemExit(f"robots.txt disallows {base_url} — aborting.")
    _ = RateLimiter(min_interval=2.0)  # would gate every request
    raise NotImplementedError(
        "Live scraping is a template only. Implement against a source whose terms "
        "of service permit it, keep the rate conservative, and store only aggregates."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect demand-evidence posts.")
    parser.add_argument("--live", metavar="URL", help="(template) live collector base URL")
    args = parser.parse_args()

    posts = collect_live(args.live) if args.live else collect_offline()
    out = os.path.join(os.path.dirname(__file__), "collected_posts.csv")
    with open(out, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(posts[0].keys()))
        writer.writeheader()
        writer.writerows(posts)
    print(f"Collected {len(posts)} posts -> {out}")


if __name__ == "__main__":
    main()
