"""
dashboard.py
Main dashboard shell: sidebar navigation + overview page.
AI-gri themed (theme.py). Keeps price-trend graph + harvest-ready structure.
"""

import streamlit as st
import pandas as pd
from datetime import  datetime, date

from harvest import estimate_harvest
from db import get_fields, get_scans, get_scan_count
from weather import (
    get_weather,
    farm_advice,
    WEATHER_CODES,
    get_seasonal_forecast,
    get_season_info,
)
from fields import show_fields
from disease import show_disease
from market_prices import (
    get_market_prices,
    get_price_trend,
    get_commodity_list,
    refresh_market_prices,
)
from theme import inject_theme, current, theme_toggle, logo_sidebar, GREEN


def show_dashboard(farmer):
    inject_theme()
    render_sidebar(farmer)
    nav = st.session_state.get("nav", "Overview")

    if nav == "My Fields":
        show_fields(farmer)
    elif nav == "Disease Detection":
        show_disease(farmer)
    else:
        show_overview(farmer)


def render_sidebar(farmer):
    t = current()
    with st.sidebar:
        initials = (farmer["first_name"][:1] + farmer["last_name"][:1]).upper()
        st.markdown(
            f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div style="
                    width:48px;height:48px;border-radius:50%;
                    background-color:{GREEN};color:white;
                    display:flex;align-items:center;justify-content:center;
                    font-weight:bold;font-size:18px;">
                    {initials}
                </div>
                <div>
                    <div style="font-weight:700;color:{t['text']};">
                        {farmer['first_name']} {farmer['last_name']}
                    </div>
                    <div style="color:{t['text2']};font-size:0.85em;">
                        @{farmer['username']}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.radio(
            "Navigation",
            ["Overview", "My Fields", "Disease Detection"],
            key="nav",
            label_visibility="collapsed",
        )

        st.divider()

        theme_toggle(where="sidebar")

        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.farmer = None
            st.session_state.page = "login"
            st.rerun()

        # AI-gri logo pinned at the bottom of the sidebar
        logo_sidebar(width=130)


def show_overview(farmer):
    fields = get_fields(farmer["id"])

    # All fields that have usable coordinates
    geo_fields = [f for f in fields if f[8] and f[9] and f[8] != 0.0]

    # Which one is currently selected for the weather cards (persists in session)
    geo_field = None
    if geo_fields:
        options = {f[2]: f for f in geo_fields}  # field_number -> field row
        prev_choice = st.session_state.get("weather_field_choice")
        default_label = prev_choice if prev_choice in options else list(options)[0]

        col_greet, col_weather, col_select = st.columns([2, 1, 1.2])
        with col_greet:
            st.title(f"Kumusta, {farmer['first_name']}!")

        with col_select:
            if len(geo_fields) > 1:
                chosen_label = st.selectbox(
                    "Weather field",
                    list(options.keys()),
                    index=list(options.keys()).index(default_label),
                    key="weather_field_choice",
                )
            else:
                chosen_label = default_label
                st.session_state["weather_field_choice"] = chosen_label

        geo_field = options[chosen_label]
    else:
        col_greet, col_weather = st.columns([2, 1])
        with col_greet:
            st.title(f"Kumusta, {farmer['first_name']}!")

    weather = None
    lat = lng = None

    with col_weather:
        if geo_field:
            lat, lng = geo_field[8], geo_field[9]
            weather = get_weather(lat, lng)
            if weather:
                code = weather["current_code"]
                _, icon = WEATHER_CODES.get(code, ("", "\u2753"))
                temp = weather["current_temp"]
                st.metric(
                    label=f"{icon} Current weather \u2014 {geo_field[7]}",
                    value=f"{temp}\u00b0C",
                )
            else:
                st.caption("Weather unavailable")
        else:
            st.caption("Add field coordinates to see weather")

    # Metric cards
    total_fields = len(fields)
    total_area = sum(f[5] for f in fields) if fields else 0.0
    crop_types = len({f[3] for f in fields}) if fields else 0
    total_scans = get_scan_count(farmer["id"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Fields", total_fields)
    m2.metric("Total Area", f"{total_area:.1f} ha")
    m3.metric("Crop Types", crop_types)
    m4.metric("Total Scans", total_scans)

    st.divider()

    # Weather forecast card
    st.subheader("5-Day Weather Forecast")

    if geo_field and weather:
        crop = geo_field[3]
        advice = farm_advice(weather["days"], crop)
        max_rain = max(d["rain_pct"] for d in weather["days"])

        if max_rain >= 70:
            st.warning(f"Farm advisory: {advice}")
        elif max_rain >= 40:
            st.info(f"Farm advisory: {advice}")
        else:
            st.success(f"Farm advisory: {advice}")

        day_cols = st.columns(5)
        for i, day in enumerate(weather["days"]):
            with day_cols[i]:
                date_label = datetime.strptime(
                    day["date"], "%Y-%m-%d"
                ).strftime("%a %b %d")
                with st.container(border=True):
                    st.markdown(f"**{date_label}**")
                    st.markdown(f"{day['icon']} {day['label']}")
                    st.markdown(f"**{day['temp_max']}\u00b0 / {day['temp_min']}\u00b0C**")
                    st.caption(f"Rain: {day['rain_pct']}%")
                    st.caption(f"Wind: {day['wind_kmh']} km/h")

        st.caption(
            f"Based on coordinates of {geo_field[7]} "
            f"({lat:.4f}, {lng:.4f}) \u00b7 Source: Open-Meteo"
        )
    else:
        with st.container(border=True):
            st.info(
                "Add latitude and longitude to a field in "
                "My Fields to see the weather forecast for your farm."
            )

    st.divider()


    # Seasonal outlook
    st.subheader("6-Months Seasonal Outlook")

    season = get_season_info(datetime.now().month)
    st.info(f"{season['icon']} **{season['season']}** — {season['advice']}")

    if geo_field and lat and lng:
        months_data = get_seasonal_forecast(lat, lng, months=6)
        if months_data:
            # ── #1: Tag best months ──────────────────────────
            best_plant = min(months_data, key=lambda m: abs(m["total_rain_mm"] - 150))
            best_dry = min(months_data, key=lambda m: m["total_rain_mm"])

            month_cols = st.columns(len(months_data))
            for col, m in zip(month_cols, months_data):
                if m["total_rain_mm"] >= 200:
                    icon = "🌧"
                elif m["total_rain_mm"] >= 100:
                    icon = "🌦"
                else:
                    icon = "☀"

                tag = ""
                if m["key"] == best_plant["key"]:
                    tag = "🌱 Best to Plant"
                elif m["key"] == best_dry["key"]:
                    tag = "🌾 Best to Harvest"

                with col:
                    with st.container(border=True):
                        st.markdown(f"**{m['month']}**")
                        st.markdown(
                            f"<div style='font-size:2em;text-align:center;'>{icon}</div>",
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"<div style='text-align:center;font-weight:bold;'>{m['total_rain_mm']} mm</div>",
                            unsafe_allow_html=True,
                        )
                        st.caption(f"🌡 {m['avg_temp_min']}–{m['avg_temp_max']}°C")
                        if tag:
                            st.markdown(
                                f"<div style='text-align:center;color:{GREEN};"
                                f"font-size:0.8em;font-weight:bold;'>{tag}</div>",
                                unsafe_allow_html=True,
                            )

            # ── #2: Cross-check harvest window vs rainfall ───
            est = estimate_harvest(geo_field[3], geo_field[4])  # crop_type, date_planted
            if est and est["status"] == "growing":
                harvest_key = est["early"].strftime("%Y-%m")
                match = next(
                    (m for m in months_data if m["key"] == harvest_key), None
                )
                if match:
                    if match["total_rain_mm"] >= 200:
                        st.warning(
                            f"⚠ Ang inaasahang anihan ng iyong {geo_field[3]} "
                            f"({est['early']:%b %Y}) ay tumatapat sa maulang buwan "
                            f"({match['total_rain_mm']} mm). Maghanda ng drying at "
                            f"storage plan, o pag-isipang mag-ani nang mas maaga "
                            f"kung hinog na."
                        )
                    elif match["total_rain_mm"] < 100:
                        st.success(
                            f"✅ Ang inaasahang anihan ng iyong {geo_field[3]} "
                            f"({est['early']:%b %Y}) ay tumatapat sa tuyong buwan — "
                            f"magandang kondisyon para sa pag-ani at pagpapatuyo."
                        )

            st.caption(
                "🌧 Maulan (200+ mm) · 🌦 May ulan (100–200 mm) · ☀ Tagtuyo (below 100 mm) "
                "· Ito ay tantiya lamang · Source: Open-Meteo Seasonal"
            )
        else:
            st.caption(
                "Hindi ma-load ang seasonal forecast ngayon — "
                "makikita pa rin ang season advisory sa itaas."
            )
    else:
        st.caption("Magdagdag ng coordinates sa isang field para makita ang seasonal chart.")

    st.divider()

    # Market prices
    header_col, refresh_col = st.columns([4, 1])
    with header_col:
        st.subheader("Market Prices")
    with refresh_col:
        if st.button("Refresh prices", use_container_width=True):
            refresh_market_prices()
            st.rerun()

    prices, price_source, fetched_at = get_market_prices()
    st.caption(
        f"Source: {price_source} \u00b7 "
        f"Last loaded {fetched_at.strftime('%b %d, %I:%M %p')}"
    )

    if not prices:
        st.info("No market price data available yet.")
    else:
        items = list(prices.items())
        cards_per_row = 4
        for row_start in range(0, len(items), cards_per_row):
            row_items = items[row_start:row_start + cards_per_row]
            row_cols = st.columns(cards_per_row)
            for col, (name, info) in zip(row_cols, row_items):
                with col:
                    st.metric(
                        label=name,
                        value=f"\u20b1{info['price']}/{info['unit']}",
                        delta=f"{info['change']:+.1f}%",
                    )

        st.write("")
        st.markdown("**Price Trend**")
        commodities = get_commodity_list()
        selected_commodity = st.selectbox(
            "Select commodity", commodities, key="price_trend_commodity"
        )
        trend = get_price_trend(selected_commodity)
        if len(trend) < 2:
            st.caption("Not enough historical data yet to plot a trend.")
        else:
            df = pd.DataFrame(trend, columns=["Date", "Price"]).set_index("Date")
            st.line_chart(df)

    st.divider()

    # Recent scans
    st.subheader("Recent Disease Scans")
    scans = get_scans(farmer["id"], limit=5)

    if not scans:
        st.info("No scans yet. Use Disease Detection to scan your crops.")
    else:
        for scan in scans:
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 2])
                with c1:
                    st.write(f"**{scan[3]}**")
                with c2:
                    sev = scan[6]
                    if sev == "Healthy":
                        st.success(sev)
                    elif sev == "Mild":
                        st.info(sev)
                    elif sev == "Moderate":
                        st.warning(sev)
                    else:
                        st.error(sev)
                with c3:
                    st.caption(str(scan[7])[:10])