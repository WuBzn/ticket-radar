"""Adaptive polling cadence.

Refund and payment-timeout releases cluster near the show date, so we poll faster
inside a "hot window" before showtime and slower otherwise. This keeps load (and
the risk of being rate-limited) low while still catching the releases that matter.
"""
from __future__ import annotations


def next_interval(
    now: float,
    show_time: float,
    base: float,
    hot: float,
    hot_window_seconds: float = 48 * 3600,
) -> float:
    """Return the seconds to wait before the next poll for an event."""
    if 0 <= (show_time - now) <= hot_window_seconds:
        return hot
    return base
