"""The contract every ticket source must satisfy."""
from __future__ import annotations

from typing import List, Protocol

from common.models import Snapshot


class TicketSource(Protocol):
    """A source returns the current availability of every tracked section.

    Implementations may read a mock generator (demo), a public JSON endpoint, or
    a scraped page. Whatever the backend, `poll()` returns one Snapshot per
    (event_id, section) observed on this call.
    """

    def poll(self) -> List[Snapshot]:
        ...
