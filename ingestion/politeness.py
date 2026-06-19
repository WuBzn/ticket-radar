"""Be a polite scraper: rate limiting and robots.txt checks.

Even though the demo uses a mock source, these helpers are what a real adapter
would call, and they document our stance on responsible data collection.
"""
from __future__ import annotations

import time
import urllib.robotparser
from urllib.parse import urlparse


class RateLimiter:
    """Blocks until at least `min_interval` seconds have passed since the last call."""

    def __init__(self, min_interval: float = 1.0):
        self.min_interval = min_interval
        self._last = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        delta = now - self._last
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self._last = time.monotonic()


def can_fetch(url: str, user_agent: str = "ticket-radar-bot") -> bool:
    """Return True only if robots.txt explicitly allows fetching `url`."""
    parts = urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{parts.scheme}://{parts.netloc}/robots.txt")
    try:
        rp.read()
    except Exception:
        # If we cannot read robots.txt, default to NOT fetching.
        return False
    return rp.can_fetch(user_agent, url)
