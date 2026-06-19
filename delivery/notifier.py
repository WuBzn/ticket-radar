"""Notification channels. Falls back to the console when no token is configured,
so the demo always produces visible output.
"""
from __future__ import annotations

import urllib.parse
import urllib.request

from common.config import settings
from common.models import Alert


class ConsoleNotifier:
    """Prints alerts to stdout. The zero-config default for demos and tests."""

    def send(self, user_id: str, alert: Alert) -> None:
        print(f"\n[PUSH -> {user_id}]\n{alert.message}\n")


class TelegramNotifier:
    """Sends alerts via the Telegram Bot API using only the standard library."""

    def __init__(self, token: str, default_chat: str | None = None):
        self.token = token
        self.default_chat = default_chat

    def send(self, user_id: str, alert: Alert) -> None:
        chat_id = user_id or self.default_chat
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": chat_id, "text": alert.message}).encode()
        try:
            urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=10)
        except Exception as exc:  # noqa: BLE001 - never let a push error kill the pipeline
            print(f"[telegram error] {exc}; falling back to console:\n{alert.message}")


def build_notifier():
    """Pick a notifier from configuration: Telegram if a token is set, else console."""
    if settings.TELEGRAM_BOT_TOKEN:
        return TelegramNotifier(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
    return ConsoleNotifier()
