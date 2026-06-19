"""Configuration loaded from environment variables (and an optional .env file).

The core demo runs with no configuration at all: alerts print to the console and
state is kept in a local SQLite file. Set the optional variables to enable
Telegram/LINE push or the scalable Kafka/Redis/Postgres backend.
"""
from __future__ import annotations

import os


def load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (stdlib only) so we avoid a python-dotenv dependency."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def _get(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


load_dotenv()


class Settings:
    # --- Storage (simple mode) ---
    DB_PATH: str = _get("RADAR_DB_PATH", "data/radar.db")  # type: ignore[assignment]

    # --- Notification channels (optional) ---
    TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = _get("TELEGRAM_CHAT_ID")
    LINE_CHANNEL_ACCESS_TOKEN = _get("LINE_CHANNEL_ACCESS_TOKEN")

    # --- Polling cadence (seconds) ---
    BASE_POLL_INTERVAL = int(_get("BASE_POLL_INTERVAL", "30"))  # type: ignore[arg-type]
    HOT_POLL_INTERVAL = int(_get("HOT_POLL_INTERVAL", "5"))  # type: ignore[arg-type]

    # --- Scalable mode (optional) ---
    KAFKA_BOOTSTRAP_SERVERS = _get("KAFKA_BOOTSTRAP_SERVERS")
    REDIS_URL = _get("REDIS_URL")
    DATABASE_URL = _get("DATABASE_URL")


settings = Settings()
