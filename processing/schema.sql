-- Postgres / TimescaleDB DDL for scalable mode.
-- The simple/demo mode uses the equivalent SQLite schema in common/store.py.

CREATE TABLE IF NOT EXISTS last_state (
    event_id    TEXT NOT NULL,
    section     TEXT NOT NULL,
    status      TEXT NOT NULL,
    observed_at DOUBLE PRECISION NOT NULL,
    PRIMARY KEY (event_id, section)
);

-- High-volume append-only observation log. Make it a TimescaleDB hypertable:
--   SELECT create_hypertable('snapshots', 'observed_at');
CREATE TABLE IF NOT EXISTS snapshots (
    id          BIGSERIAL PRIMARY KEY,
    event_id    TEXT NOT NULL,
    section     TEXT NOT NULL,
    status      TEXT NOT NULL,
    observed_at DOUBLE PRECISION NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_snapshots_evt ON snapshots (event_id, section, observed_at);

CREATE TABLE IF NOT EXISTS alerts (
    id          BIGSERIAL PRIMARY KEY,
    event_id    TEXT NOT NULL,
    event_name  TEXT NOT NULL,
    section     TEXT NOT NULL,
    price       INTEGER NOT NULL,
    detected_at DOUBLE PRECISION NOT NULL,
    message     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    user_id  TEXT NOT NULL,
    event_id TEXT NOT NULL,
    PRIMARY KEY (user_id, event_id)
);
