"""A self-contained ticket source that simulates a hot, sold-out show.

This makes the whole pipeline runnable end-to-end with NO network calls, which is
the right default for a class demo: a grader can reproduce results without
scraping any real site, and we don't touch anyone's terms of service.

Behaviour: every section starts SOLD_OUT (the show sold out at on-sale). On each
poll, a sold-out section has a small chance to flip to AVAILABLE (a refund or a
payment-timeout release); an available section is usually grabbed again quickly.
"""
from __future__ import annotations

import random
import time
from typing import Dict, List, Tuple

from common.models import Availability, Snapshot


class MockTicketSource:
    def __init__(self, events: List[dict], seed: int = 42, release_prob: float = 0.12):
        self.random = random.Random(seed)
        self.release_prob = release_prob
        self._state: Dict[Tuple[str, str], Availability] = {}
        for ev in events:
            for sec in ev["sections"]:
                self._state[(ev["event_id"], sec["section"])] = Availability.SOLD_OUT

    def poll(self) -> List[Snapshot]:
        now = time.time()
        snaps: List[Snapshot] = []
        for (event_id, section), status in self._state.items():
            if status == Availability.SOLD_OUT:
                if self.random.random() < self.release_prob:
                    status = Availability.AVAILABLE
            elif status == Availability.AVAILABLE:
                # Released tickets get snapped up fast.
                if self.random.random() < 0.55:
                    status = Availability.SOLD_OUT
            self._state[(event_id, section)] = status
            snaps.append(Snapshot(event_id, section, status, now))
        return snaps
