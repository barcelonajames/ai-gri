# Ai-gri

A web dashboard for Filipino farmers with field management, live 5-day
weather forecasts (Open-Meteo), market prices, and AI crop disease
detection powered by Claude's vision capabilities.

## How to run

1. `pip install -r requirements.txt`
2. Add your Anthropic API key to `.streamlit/secrets.toml`:
   ```
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
3. `streamlit run main.py`
4. App opens at http://localhost:8501

## Weather

Open-Meteo is completely free and requires no API key. Weather is
fetched live using the latitude/longitude saved on each field. If a
field has no coordinates (0.0, 0.0), weather won't show for that
field — add coordinates when creating or editing a field (tip: right
click your farm location on Google Maps to copy the coordinates).

## Deploy free on Streamlit Community Cloud

1. Push this code to GitHub (secrets.toml is gitignored — don't commit it)
2. Go to share.streamlit.io
3. Connect your repo, set main file = `main.py`
4. Add `ANTHROPIC_API_KEY` under the app's Secrets settings
5. Click Deploy — live URL in ~2 minutes

## Market prices

Market prices come from `market_prices.py`, which reads a CSV instead
of scraping any site. It checks sources in this order:

1. A remote CSV URL, if you set `MARKET_PRICES_CSV_URL` in
   `.streamlit/secrets.toml` — e.g. a Google Sheet you maintain,
   published via File → Share → Publish to web → CSV.
2. `market_prices.csv` in the project root, which you or a scheduled
   job can overwrite periodically.
3. Built-in defaults, only if neither source above is reachable.

CSV format:
```
commodity,price,unit,change
Palay (dry),23.00,kg,2.5
```
`change` is the percent to show as the delta (use `0` if you don't
track it).

Prices are cached for 1 hour so the dashboard doesn't hammer your CSV
source on every click; there's a "Refresh prices" button on the
dashboard to force an immediate reload.

## Note on storage

`farmers.db` is a local SQLite file and will reset whenever Streamlit
Cloud restarts your app. For persistent storage in production, swap
SQLite for a hosted database (e.g. Supabase) by replacing the
`sqlite3` calls in `db.py` with the Supabase client, and storing
`SUPABASE_URL` / `SUPABASE_KEY` in secrets.toml.
