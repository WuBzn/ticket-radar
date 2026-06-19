"""Batch job: mine release-timing patterns from the snapshot log.

This is the actual *data product* — the insight a fan can't get by manually
refreshing. By replaying the snapshot history we find every SOLD_OUT ->
AVAILABLE transition and ask: when do releases happen? (hour of day, and minutes
after the on-sale time). The output drives a "best time to watch" recommendation.

Runs on the standard library; if matplotlib is installed it also saves a chart.
In scalable mode this is a Spark/Flink batch job over the Parquet/Timescale log.
"""
from __future__ import annotations

import collections
import sqlite3
import sys
import time
from typing import Dict, List, Tuple

from common.config import settings
from common.models import Availability


def find_releases(db_path: str) -> List[Tuple[str, str, float]]:
    """Return (event_id, section, observed_at) for every SOLD_OUT -> AVAILABLE edge."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT event_id, section, status, observed_at FROM snapshots "
        "ORDER BY event_id, section, observed_at"
    ).fetchall()
    conn.close()

    releases: List[Tuple[str, str, float]] = []
    prev: Dict[Tuple[str, str], str] = {}
    for r in rows:
        key = (r["event_id"], r["section"])
        if prev.get(key) == Availability.SOLD_OUT.value and r["status"] == Availability.AVAILABLE.value:
            releases.append((r["event_id"], r["section"], r["observed_at"]))
        prev[key] = r["status"]
    return releases


def hour_histogram(releases: List[Tuple[str, str, float]]) -> Dict[int, int]:
    hist = collections.Counter()
    for _, _, ts in releases:
        hist[time.localtime(ts).tm_hour] += 1
    return dict(sorted(hist.items()))


def print_report(db_path: str) -> None:
    releases = find_releases(db_path)
    print(f"\n=== Release-pattern analysis ===")
    print(f"Total re-releases observed: {len(releases)}")
    if not releases:
        print("(no releases yet — run the demo first)")
        return

    hist = hour_histogram(releases)
    peak_hour = max(hist, key=hist.get)
    print(f"Peak release hour: {peak_hour:02d}:00  ({hist[peak_hour]} releases)")
    print("\nHour-of-day histogram:")
    top = max(hist.values())
    for hour, count in hist.items():
        bar = "#" * int(round(20 * count / top))
        print(f"  {hour:02d}:00 | {bar} {count}")

    _maybe_plot(hist)


def _maybe_plot(hist: Dict[int, int]) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(list(hist.keys()), list(hist.values()), color="#3b82f6")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Re-releases")
    ax.set_title("When do tickets get re-released?")
    fig.tight_layout()
    out = "docs/release_pattern.png"
    fig.savefig(out, dpi=120)
    print(f"\nSaved chart -> {out}")


if __name__ == "__main__":
    db = sys.argv[1] if len(sys.argv) > 1 else settings.DB_PATH
    print_report(db)
