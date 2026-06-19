"""End-to-end demo: ingestion -> stream detection -> notification + storage.

Run from the repo root:
    python run_demo.py

No configuration needed. Alerts print to the console and state is written to
data/radar.db. Set TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID (see .env.example) to
receive real push notifications instead.
"""
from __future__ import annotations

import json
import os
import sys

# Make console output UTF-8 safe on Windows (cp950) terminals.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from common.config import settings
from common.store import Store
from delivery.notifier import build_notifier
from ingestion.poller import Poller
from ingestion.politeness import RateLimiter
from ingestion.sources.mock_source import MockTicketSource
from processing import batch_analysis
from processing.stream_detector import StreamDetector

EVENTS_FILE = os.path.join("data", "sample", "events.json")
DEMO_USER = "demo-user"
TICKS = 40
INTERVAL = 0.1  # seconds between polls (fast, for the demo)


def load_events() -> list:
    with open(EVENTS_FILE, encoding="utf-8") as fh:
        return json.load(fh)


def build_events_index(events: list) -> dict:
    index = {}
    for ev in events:
        index[ev["event_id"]] = {
            "name": ev["name"],
            "sections": {s["section"]: s["price"] for s in ev["sections"]},
        }
    return index


def main() -> None:
    # Fresh database each run so the demo is reproducible.
    if os.path.exists(settings.DB_PATH):
        os.remove(settings.DB_PATH)

    events = load_events()
    index = build_events_index(events)

    store = Store(settings.DB_PATH)
    for ev in events:  # the demo user subscribes to every event
        store.add_subscription(DEMO_USER, ev["event_id"])

    notifier = build_notifier()
    detector = StreamDetector(store, notifier, index)
    source = MockTicketSource(events)
    poller = Poller(source, sink=detector.process, rate_limiter=RateLimiter(min_interval=0.0))

    print("Ticket Radar demo — watching for official re-releases...")
    print(f"Tracking {len(events)} events, {sum(len(e['sections']) for e in events)} sections.\n")

    poller.run(ticks=TICKS, interval=INTERVAL)

    alerts = store.recent_alerts(limit=100)
    print(f"\nDemo finished. {len(alerts)} re-release alert(s) fired and stored in {settings.DB_PATH}.")

    batch_analysis.print_report(settings.DB_PATH)
    store.close()


if __name__ == "__main__":
    main()
