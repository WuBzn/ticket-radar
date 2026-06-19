"""SQLite-backed state and event log for the simple/demo mode.

In scalable mode (see docker-compose.yml) the "last known state" lives in Redis
and the durable log lives in Postgres/TimescaleDB; the method surface here is the
seam where you would swap those in. See processing/schema.sql for the Postgres DDL.
"""
from __future__ import annotations

import os
import sqlite3
from typing import List, Optional

from common.models import Alert, Snapshot

_SCHEMA = """
CREATE TABLE IF NOT EXISTS last_state (
    event_id    TEXT NOT NULL,
    section     TEXT NOT NULL,
    status      TEXT NOT NULL,
    observed_at REAL NOT NULL,
    PRIMARY KEY (event_id, section)
);

CREATE TABLE IF NOT EXISTS snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    TEXT NOT NULL,
    section     TEXT NOT NULL,
    status      TEXT NOT NULL,
    observed_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_snapshots_evt ON snapshots (event_id, section, observed_at);

CREATE TABLE IF NOT EXISTS alerts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id    TEXT NOT NULL,
    event_name  TEXT NOT NULL,
    section     TEXT NOT NULL,
    price       INTEGER NOT NULL,
    detected_at REAL NOT NULL,
    message     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    user_id  TEXT NOT NULL,
    event_id TEXT NOT NULL,
    PRIMARY KEY (user_id, event_id)
);
"""


class Store:
    def __init__(self, db_path: str):
        parent = os.path.dirname(db_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    # --- state (read/compare/update) ---
    def get_last_status(self, event_id: str, section: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT status FROM last_state WHERE event_id=? AND section=?",
            (event_id, section),
        ).fetchone()
        return row["status"] if row else None

    def update_status(self, event_id: str, section: str, status: str, observed_at: float) -> None:
        self.conn.execute(
            """INSERT INTO last_state (event_id, section, status, observed_at)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(event_id, section)
               DO UPDATE SET status=excluded.status, observed_at=excluded.observed_at""",
            (event_id, section, status, observed_at),
        )
        self.conn.commit()

    # --- durable log ---
    def append_snapshot(self, snap: Snapshot) -> None:
        self.conn.execute(
            "INSERT INTO snapshots (event_id, section, status, observed_at) VALUES (?, ?, ?, ?)",
            (snap.event_id, snap.section, snap.status.value, snap.observed_at),
        )
        self.conn.commit()

    def record_alert(self, alert: Alert) -> None:
        self.conn.execute(
            """INSERT INTO alerts (event_id, event_name, section, price, detected_at, message)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (alert.event_id, alert.event_name, alert.section, alert.price,
             alert.detected_at, alert.message),
        )
        self.conn.commit()

    def recent_alerts(self, limit: int = 20) -> List[sqlite3.Row]:
        return self.conn.execute(
            "SELECT * FROM alerts ORDER BY detected_at DESC LIMIT ?", (limit,)
        ).fetchall()

    # --- subscriptions ---
    def add_subscription(self, user_id: str, event_id: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO subscriptions (user_id, event_id) VALUES (?, ?)",
            (user_id, event_id),
        )
        self.conn.commit()

    def subscribers(self, event_id: str) -> List[str]:
        rows = self.conn.execute(
            "SELECT user_id FROM subscriptions WHERE event_id=?", (event_id,)
        ).fetchall()
        return [r["user_id"] for r in rows]

    def close(self) -> None:
        self.conn.close()
