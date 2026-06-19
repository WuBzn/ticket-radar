# 🎫 Ticket Radar — Official Concert Re-release Monitor

> Big Data Systems · Final Project · National Taiwan University, Spring 2026

Popular concerts sell out in minutes, but tickets keep coming back: refunds,
payment-timeout releases, and added blocks trickle onto the **official** platform
for days. Fans catch them today by manually refreshing a dozen browser tabs at 2am.
**Ticket Radar** watches public availability for you and pushes an instant alert the
moment a sold-out section is re-released — at **face value, on the official site**.

It deliberately does **not** facilitate scalping. Reselling above face value (and
using bots to *buy*) is illegal in Taiwan under the Culture and Creative Industries
Development Act, so the product is positioned squarely on the consumer's side: it
only reads public availability and only points users to the official channel.

- **GitHub repo:** _<add your repo URL here>_
- **Live demo (optional):** _<add deployment URL here, if any>_

---

## What's in this repo

```
ticket-radar/
├── run_demo.py             # one-command end-to-end demo (no setup needed)
├── common/                 # shared models, config, SQLite store
├── ingestion/              # pollers + pluggable sources (mock / real adapter)
│   ├── poller.py
│   ├── adaptive_schedule.py
│   ├── politeness.py       # rate limiting + robots.txt checks
│   └── sources/            # MockTicketSource (default) + real-adapter template
├── processing/             # stream edge-detection + batch pattern mining
│   ├── stream_detector.py  # detects SOLD_OUT -> AVAILABLE, fires alerts
│   ├── batch_analysis.py   # mines release-timing patterns (the data product)
│   └── schema.sql          # Postgres/TimescaleDB DDL for scalable mode
├── delivery/               # notifier (console/Telegram) + Streamlit dashboard
├── demand_research/        # Component 2: demand evidence (reproducible)
│   ├── scrape_forums.py    # offline by default; polite live template
│   ├── analyze_demand.py   # post volume, sentiment, willingness-to-pay
│   ├── survey_questions.md
│   ├── sample_posts.csv    # synthetic sample (clearly labelled)
│   └── survey_results.csv  # synthetic survey responses
├── data/sample/events.json # 3 sample events to track
├── docs/architecture.md    # diagram + design rationale
└── docker-compose.yml      # OPTIONAL Kafka + Redis + Postgres (scalable mode)
```

---

## Quick start (≈30 seconds, no dependencies)

The core demo runs on the **Python standard library only** — no pip install, no Docker.

```bash
python run_demo.py
```

You'll see the pipeline poll a simulated sold-out show, detect re-releases in real
time, fire alerts to the console, and then print a release-timing analysis. State is
written to `data/radar.db`.

### Optional: real push notifications

```bash
cp .env.example .env
# set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env
python run_demo.py        # alerts now go to Telegram instead of the console
```

### Optional: dashboard

```bash
pip install streamlit pandas
streamlit run delivery/dashboard/app.py
```

### Optional: reproduce the demand analysis (Component 2)

```bash
python demand_research/analyze_demand.py
```

### Optional: scalable mode (Kafka + Redis + Postgres)

```bash
docker compose up -d      # see docker-compose.yml and docs/architecture.md
```

---

## How it works

A poller pulls availability **snapshots** from a source and hands each to a **sink**.
The stream detector compares every snapshot with the last known state of that
`(event, section)` and fires an alert on the **SOLD_OUT → AVAILABLE** edge, fanning
it out to everyone subscribed to that event. A batch job replays the snapshot log to
learn *when* releases tend to happen — the insight a manual refresher can't get.

The same code runs in two modes. **Simple mode** (the default) uses an in-process
sink and SQLite. **Scalable mode** swaps the sink for a Kafka topic, the state store
for Redis, and the log for TimescaleDB — without changing the detector. See
[docs/architecture.md](docs/architecture.md) for the diagram and rationale.

---

## Data sources

| Source | What we read | How |
|--------|--------------|-----|
| Ticketing platforms | public per-section availability | adaptive polling (`MockTicketSource` in this repo; real adapter is a template) |
| Secondary market | scalper asking prices | reference only — to warn users, never to facilitate a sale |
| Forums / surveys | demand evidence | `demand_research/` (offline sample here) |

---

## Legal & ethics

This project takes data ethics seriously — it is central to the product, not an
afterthought:

- **No scalping.** We never automate purchasing and never facilitate above-face-value
  resale. Alerts point only to the official platform at face value.
- **Polite collection.** Pollers and the demand collector check `robots.txt`
  (`ingestion/politeness.can_fetch`) and rate-limit (`RateLimiter`). The shipped demo
  hits **no** real site — it uses a local simulator — so running this repo touches
  no one's terms of service.
- **No personal data committed.** `sample_posts.csv` and `survey_results.csv` are
  **synthetic** illustrations of the methodology, not real scraped posts. Real raw
  data is git-ignored; only aggregates would be stored.

---

## Business model (summary)

- **Customer:** fans who missed out on a sold-out show and want official re-releases.
- **Value:** turn "refresh all night" into "get a push the second a ticket returns,"
  plus a data-driven "best time to watch" recommendation.
- **Pricing:** freemium — track one event free; subscription (≈NT$99–199/mo) for
  multiple events, faster polling, and instant push.
- **Moat:** the accumulating history of release-timing patterns, which improves the
  predictions over time and can't be replicated by a fresh competitor.

Full analysis (target customer, demand evidence, go-to-market difficulties) is in the
project report PDF.
