"""
market_prices.py
Loads market price data for the dashboard from a CSV source instead
of hardcoding it or scraping a website.

Supported sources, tried in this order:
  1. A remote CSV URL (e.g. a Google Sheet published to the web as
     CSV) set via MARKET_PRICES_CSV_URL in .streamlit/secrets.toml
  2. A local CSV file (market_prices.csv in the project root) that
     you or a scheduled job overwrites periodically
  3. Built-in default prices, used only if neither source is available

CSV format (header required):
    commodity,price,unit,change
    Palay (dry),23.00,kg,2.5
    Regular milled rice,51.00,kg,-1.2

Where "change" is the percent change to show as the metric delta
(use 0 if you don't track it).
"""

import csv
import io
import os
from datetime import datetime

import requests
import streamlit as st

LOCAL_CSV_PATH = "market_prices.csv"

# Fallback used only if no CSV source is available or reachable.
DEFAULT_PRICES = {
    "Palay (dry)":         {"price": 23.00, "unit": "kg",  "change": 2.5},
    "Regular milled rice": {"price": 51.00, "unit": "kg",  "change": -1.2},
    "Well milled rice":    {"price": 58.00, "unit": "kg",  "change": 0.8},
    "Corn (dry)":          {"price": 18.00, "unit": "kg",  "change": 1.0},
    "Urea fertilizer":     {"price": 1450,  "unit": "bag", "change": 0.0},
}


def _parse_csv_text(text: str) -> dict:
    """
    Parses CSV text with columns commodity, price, unit, change into
    the {name: {"price":.., "unit":.., "change":..}} shape the
    dashboard expects. Malformed rows are skipped, not fatal.
    """
    prices = {}
    reader = csv.DictReader(io.StringIO(text))
    for row in reader:
        try:
            name = (row.get("commodity") or "").strip()
            price = float(row["price"])
            unit = (row.get("unit") or "").strip()
            change = float(row.get("change") or 0)
        except (KeyError, ValueError, TypeError):
            continue
        if name:
            prices[name] = {"price": price, "unit": unit, "change": change}
    return prices


def _fetch_from_url(url: str) -> dict:
    r = requests.get(url, timeout=8)
    r.raise_for_status()
    return _parse_csv_text(r.text)


def _fetch_from_local_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return _parse_csv_text(f.read())


@st.cache_data(ttl=3600, show_spinner=False)
def _load_prices_cached(csv_url):
    """
    Cached for 1 hour (see ttl) so the dashboard doesn't re-fetch on
    every rerun or widget interaction. Returns
    (prices dict, source label, fetched_at datetime).
    """
    if csv_url:
        try:
            prices = _fetch_from_url(csv_url)
            if prices:
                return prices, "remote CSV", datetime.now()
        except Exception:
            pass  # fall through to local file / defaults

    if os.path.exists(LOCAL_CSV_PATH):
        try:
            prices = _fetch_from_local_file(LOCAL_CSV_PATH)
            if prices:
                return prices, "local CSV", datetime.now()
        except Exception:
            pass

    return DEFAULT_PRICES, "built-in defaults", datetime.now()


def get_market_prices():
    """
    Public entry point used by dashboard.py.
    Returns (prices dict, source label, fetched_at datetime).
    """
    csv_url = st.secrets.get("MARKET_PRICES_CSV_URL", None)
    return _load_prices_cached(csv_url)


def refresh_market_prices():
    """Call from a 'Refresh prices' button to bust the 1-hour cache."""
    _load_prices_cached.clear()
