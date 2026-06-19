"""Skeleton for a real ticketing-platform adapter (disabled by default).

This file is intentionally a template. Hitting a live platform raises real legal
and terms-of-service questions (see README "Legal & ethics"), so the demo ships
with MockTicketSource instead. If you adapt this for a real source:

  * Only read PUBLIC availability state — never automate purchases or checkout.
  * Honour robots.txt (ingestion.politeness.can_fetch) and a conservative rate.
  * Identify your bot honestly via the User-Agent; cache aggressively.
  * Prefer an official/JSON endpoint over HTML scraping where one exists.
"""
from __future__ import annotations

from typing import List

from common.models import Snapshot


class TixcraftAdapter:
    def __init__(self, event_id: str, status_url: str, user_agent: str = "ticket-radar-bot"):
        self.event_id = event_id
        self.status_url = status_url
        self.user_agent = user_agent

    def poll(self) -> List[Snapshot]:
        raise NotImplementedError(
            "Real-platform polling is disabled in this template. "
            "Implement responsibly: read only public availability, respect robots.txt "
            "and rate limits, and never automate purchasing."
        )
