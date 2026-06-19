"""Core data models shared across ingestion, processing, and delivery."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Availability(str, Enum):
    """Availability of a seating section on the ticketing platform."""

    SOLD_OUT = "SOLD_OUT"
    AVAILABLE = "AVAILABLE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Snapshot:
    """One observation of a section's availability at a point in time.

    Pollers emit a stream of these; the stream detector compares consecutive
    snapshots per (event_id, section) to find the SOLD_OUT -> AVAILABLE edge.
    """

    event_id: str
    section: str
    status: Availability
    observed_at: float  # epoch seconds
    remaining: Optional[int] = None


@dataclass(frozen=True)
class Alert:
    """A re-release event worth notifying a subscriber about."""

    event_id: str
    event_name: str
    section: str
    price: int
    detected_at: float
    message: str
