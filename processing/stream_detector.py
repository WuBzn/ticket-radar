"""Stream processor: detect the SOLD_OUT -> AVAILABLE edge and fan out alerts.

This is the heart of the system. For every incoming snapshot we compare against
the last known state of that (event_id, section). The only transition we care
about is SOLD_OUT -> AVAILABLE, which means a ticket was just re-released on the
official platform. We then notify every subscriber of that event.

In scalable mode this same class is the body of a Kafka consumer; the only change
is where snapshots come from (a topic instead of a direct call).
"""
from __future__ import annotations

import time
from typing import Dict, Optional

from common.models import Alert, Availability, Snapshot
from common.store import Store


class StreamDetector:
    def __init__(self, store: Store, notifier, events_index: Dict[str, dict]):
        self.store = store
        self.notifier = notifier
        self.events = events_index  # event_id -> {"name": str, "sections": {section: price}}

    def process(self, snap: Snapshot) -> Optional[Alert]:
        prev = self.store.get_last_status(snap.event_id, snap.section)

        # Persist the observation, then advance the state.
        self.store.append_snapshot(snap)
        self.store.update_status(snap.event_id, snap.section, snap.status.value, snap.observed_at)

        if prev == Availability.SOLD_OUT.value and snap.status == Availability.AVAILABLE:
            alert = self._build_alert(snap)
            self.store.record_alert(alert)
            for user_id in self.store.subscribers(snap.event_id):
                self.notifier.send(user_id, alert)
            return alert
        return None

    def _build_alert(self, snap: Snapshot) -> Alert:
        ev = self.events.get(snap.event_id, {})
        name = ev.get("name", snap.event_id)
        price = ev.get("sections", {}).get(snap.section, 0)
        clock = time.strftime("%H:%M:%S", time.localtime(snap.observed_at))
        message = (
            f"\U0001F3AB {name}\n"
            f"Section {snap.section} (face value NT${price}) just became AVAILABLE "
            f"on the OFFICIAL site at {clock}.\n"
            f"Grab it fast — and only buy at face value. Reselling above face value "
            f"is illegal under Taiwan's anti-scalping law."
        )
        return Alert(
            event_id=snap.event_id,
            event_name=name,
            section=snap.section,
            price=price,
            detected_at=snap.observed_at,
            message=message,
        )
