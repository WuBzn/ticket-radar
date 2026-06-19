"""Streamlit dashboard: recent alerts + availability timeline.

Run from the repo root:
    streamlit run delivery/dashboard/app.py
"""
from __future__ import annotations

import os
import sqlite3
import sys

# Make the repo root importable when launched via `streamlit run`.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from common.config import settings  # noqa: E402

st.set_page_config(page_title="Ticket Radar", page_icon="🎫", layout="wide")
st.title("🎫 Ticket Radar — official re-release monitor")

db_path = settings.DB_PATH
if not os.path.exists(db_path):
    st.warning(f"No database at {db_path}. Run `python run_demo.py` first.")
    st.stop()

conn = sqlite3.connect(db_path)

st.subheader("Recent re-release alerts")
alerts = pd.read_sql_query(
    "SELECT datetime(detected_at, 'unixepoch', 'localtime') AS time, "
    "event_name, section, price FROM alerts ORDER BY detected_at DESC LIMIT 50",
    conn,
)
st.dataframe(alerts, use_container_width=True)

st.subheader("Availability snapshots over time")
snaps = pd.read_sql_query(
    "SELECT datetime(observed_at, 'unixepoch', 'localtime') AS time, "
    "event_id, section, status FROM snapshots ORDER BY observed_at DESC LIMIT 1000",
    conn,
)
st.dataframe(snaps, use_container_width=True)

events = sorted(snaps["event_id"].unique()) if not snaps.empty else []
if events:
    chosen = st.selectbox("Event", events)
    view = snaps[snaps["event_id"] == chosen].copy()
    view["available"] = (view["status"] == "AVAILABLE").astype(int)
    chart = view.pivot_table(index="time", columns="section", values="available", aggfunc="max")
    st.line_chart(chart)

conn.close()
