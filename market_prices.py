"""
market_prices.py
Loads market price history for the dashboard from a CSV source and
derives current prices, % change, and full trend lines from it,
instead of hardcoding a single snapshot or scraping a website.

Supported sources, tried in this order:
  1. A remote CSV URL (e.g. a Google Sheet published to the web as
     CSV) set via MARKET_PRICES_CSV_URL in .streamlit/secrets.toml
  2. A local CSV file (market_prices.csv in the project root) that
     you overwrite periodically (e.g. with reshaped PSA OpenSTAT data)
  3. A small built-in sample, used only if neither source above is
     available or reachable — clearly not real PSA figures, just so
     the dashboard renders something out of the box.

CSV format (long/tidy shape — one row per commodity per date):
    date,commodity,price,unit
    2021-01-01,Palay (dry),18.50,kg
    2021-02-01,Palay (dry),18.70,kg
    2021-01-01,Corn (dry),16.20,kg
    ...

"date" accepts YYYY-MM-DD, YYYY-MM, or YYYY (monthly or annual data
both work — the chart just plots whatever points exist). "change"
is no longer a CSV column: it's computed automatically as the
percent difference between the latest two data points for each
commodity.
"""

import csv
import io
import os
from datetime import datetime

import requests
import streamlit as st

LOCAL_CSV_PATH = "market_prices.csv"

# Minimal built-in sample so the dashboard renders something before
# you've plugged in a real CSV. NOT real PSA data — replace it.
DEFAULT_HISTORY_ROWS = [
    ("2026-04-01", "Palay (dry)", 22.50, "kg"),
    ("2026-05-01", "Palay (dry)", 22.90, "kg"),
    ("2026-06-01", "Palay (dry)", 23.00, "kg"),
    ("2026-04-01", "Regular milled rice", 51.80, "kg"),
    ("2026-05-01", "Regular milled rice", 51.40, "kg"),
    ("2026-06-01", "Regular milled rice", 51.00, "kg"),
    ("2026-04-01", "Well milled rice", 57.60, "kg"),
    ("2026-05-01", "Well milled rice", 57.90, "kg"),
    ("2026-06-01", "Well milled rice", 58.00, "kg"),
    ("2026-04-01", "Corn (dry)", 17.80, "kg"),
    ("2026-05-01", "Corn (dry)", 17.90, "kg"),
    ("2026-06-01", "Corn (dry)", 18.00, "kg"),
    ("2026-04-01", "Urea fertilizer", 1450, "bag"),
    ("2026-05-01", "Urea fertilizer", 1450, "bag"),
    ("2026-06-01", "Urea fertilizer", 1450, "bag"),
]


def _parse_date(raw: str):
    raw = (raw or "").strip()
    for fmt in ("%Y-%m-%d", "%Y-%m", "%m/%d/%Y", "%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _parse_csv_text(text: str) -> dict:
    """
    Parses long-format CSV (date, commodity, price, unit) into:
        {commodity: [(date, price, unit), ...]}  sorted ascending by date
    Malformed rows are skipped rather than crashing the dashboard.
    """
    history = {}
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        try:
            d = _parse_date(row.get("date", ""))
            name = (row.get("commodity") or "").strip()
            price = float(row["price"])
            unit = (row.get("unit") or "").strip()
        except (KeyError, ValueError, TypeError):
            continue
        if d and name:
            history.setdefault(name, []).append((d, price, unit))

    for name in history:
        history[name].sort(key=lambda r: r[0])

    return history


def _fetch_from_url(url: str) -> dict:
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return _parse_csv_text(r.text)


def _fetch_from_local_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return _parse_csv_text(f.read())


def _default_history() -> dict:
    history = {}
    for raw_date, name, price, unit in DEFAULT_HISTORY_ROWS:
        history.setdefault(name, []).append((_parse_date(raw_date), price, unit))
    for name in history:
        history[name].sort(key=lambda r: r[0])
    return history


@st.cache_data(ttl=3600, show_spinner=False)
def _load_history_cached(csv_url):
    """
    Cached for 1 hour so the dashboard doesn't re-fetch on every
    rerun or widget interaction. Returns
    (history dict, source label, fetched_at datetime).
    history shape: {commodity: [(date, price, unit), ...]} ascending.
    """
    if csv_url:
        try:
            history = _fetch_from_url(csv_url)
            if history:
                return history, "remote CSV", datetime.now()
        except Exception:
            pass  # fall through to local file / sample data

    if os.path.exists(LOCAL_CSV_PATH):
        try:
            history = _fetch_from_local_file(LOCAL_CSV_PATH)
            if history:
                return history, "local CSV", datetime.now()
        except Exception:
            pass

    return _default_history(), "built-in sample data", datetime.now()


def _get_history():
    csv_url = st.secrets.get("MARKET_PRICES_CSV_URL", None)
    return _load_history_cached(csv_url)


def get_market_prices():
    """
    Public entry point for the metric cards.
    Returns (prices dict, source label, fetched_at datetime) where
    prices = {commodity: {"price":.., "unit":.., "change":..}} using
    the latest data point and % change vs the previous data point.
    """
    history, source, fetched_at = _get_history()
    prices = {}
    for name, points in history.items():
        if not points:
            continue
        _, latest_price, unit = points[-1]
        if len(points) >= 2:
            prev_price = points[-2][1]
            change = ((latest_price - prev_price) / prev_price * 100) if prev_price else 0.0
        else:
            change = 0.0
        prices[name] = {"price": latest_price, "unit": unit, "change": change}
    return prices, source, fetched_at


def get_price_trend(commodity: str):
    """
    Returns [(date, price), ...] ascending for one commodity, for
    charting. Empty list if the commodity isn't in the data.
    """
    history, _, _ = _get_history()
    points = history.get(commodity, [])
    return [(d, p) for d, p, _ in points]


def get_commodity_list():
    """Returns the list of commodity names currently available."""
    history, _, _ = _get_history()
    return list(history.keys())


def refresh_market_prices():
    """Call from a 'Refresh prices' button to bust the 1-hour cache."""
    _load_history_cached.clear()
