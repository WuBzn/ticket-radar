"""The poller: pulls snapshots from a source and hands them to a sink.

The sink is just `callable(Snapshot)`. In simple mode the sink is the stream
detector's `process` method. In scalable mode the sink is a Kafka producer
(`producer.send("snapshots", ...)`) and the detector runs as a separate consumer.
Decoupling them via the sink is what lets the same poller scale out.
"""
from __future__ import annotations

import time
from typing import Callable

from common.models import Snapshot
from ingestion.politeness import RateLimiter
from ingestion.sources.base import TicketSource

Sink = Callable[[Snapshot], None]


class Poller:
    def __init__(self, source: TicketSource, sink: Sink, rate_limiter: RateLimiter | None = None):
        self.source = source
        self.sink = sink
        self.rate = rate_limiter or RateLimiter(min_interval=0.0)

    def poll_once(self) -> int:
        self.rate.wait()
        snaps = self.source.poll()
        for snap in snaps:
            self.sink(snap)
        return len(snaps)

    def run(self, ticks: int, interval: float) -> None:
        for _ in range(ticks):
            self.poll_once()
            time.sleep(interval)
