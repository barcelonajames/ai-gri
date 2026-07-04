"""
weather.py
Weather fetching and farm-advisory helper logic using the free
Open-Meteo API (no API key required).
"""

import requests
import streamlit as st

WEATHER_CODES = {
    0: ("Clear sky", "☀"),
    1: ("Mainly clear", "🌤"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁"),
    45: ("Foggy", "🌫"),
    48: ("Icy fog", "🌫"),
    51: ("Light drizzle", "🌦"),
    53: ("Moderate drizzle", "🌦"),
    55: ("Dense drizzle", "🌦"),
    61: ("Slight rain", "🌧"),
    63: ("Moderate rain", "🌧"),
    65: ("Heavy rain", "🌧"),
    71: ("Slight snow", "🌨"),
    73: ("Moderate snow", "🌨"),
    75: ("Heavy snow", "🌨"),
    80: ("Rain showers", "🌦"),
    81: ("Moderate showers", "🌧"),
    82: ("Violent showers", "⛈"),
    95: ("Thunderstorm", "⛈"),
    96: ("Thunderstorm + hail", "⛈"),
    99: ("Thunderstorm + hail", "⛈"),
}

@st.cache_data(ttl=1800)  # cache 30 minutes
def get_weather(lat: float, lng: float):
    """
    Fetch 5-day daily forecast + current weather from Open-Meteo.
    Returns a parsed dict or None on failure.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lng,
        "daily": ",".join([
            "weathercode",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "windspeed_10m_max",
        ]),
        "current_weather": True,
        "timezone": "Asia/Manila",
        "forecast_days": 5,
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()
        daily = data.get("daily", {})
        current = data.get("current_weather", {})

        days = []
        num_days = len(daily.get("time", []))
        for i in range(num_days):
            code = daily["weathercode"][i]
            label, icon = WEATHER_CODES.get(code, ("Unknown", "❓"))
            days.append({
                "date": daily["time"][i],
                "code": code,
                "label": label,
                "icon": icon,
                "temp_max": daily["temperature_2m_max"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "rain_mm": daily["precipitation_sum"][i],
                "rain_pct": daily["precipitation_probability_max"][i],
                "wind_kmh": daily["windspeed_10m_max"][i],
            })

        return {
            "current_temp": current.get("temperature"),
            "current_code": current.get("weathercode"),
            "days": days,
        }
    except Exception:
        return None


def farm_advice(days: list, crop_type: str) -> str:
    """
    Generate a plain-language farm advisory based on the 5-day
    forecast and the farmer's crop type. Returns a short Taglish string.
    """
    heavy_rain_days = [
        d["date"][5:]  # MM-DD
        for d in days
        if d["rain_pct"] >= 70 or d["rain_mm"] >= 20
    ]
    strong_wind_days = [
        d["date"][5:]
        for d in days
        if d["wind_kmh"] >= 40
    ]

    advisories = []
    if heavy_rain_days:
        day_str = ", ".join(heavy_rain_days)
        advisories.append(
            f"Malakas na ulan inaasahan sa {day_str}. "
            f"Iwasang mag-spray ng pesticide at suriin ang drainage ng iyong {crop_type} field."
        )
    if strong_wind_days:
        day_str = ", ".join(strong_wind_days)
        advisories.append(
            f"Malakas na hangin sa {day_str}. "
            f"I-check ang mga halaman at support structures."
        )
    if not advisories:
        advisories.append(
            f"Magandang panahon para sa susunod na 5 araw. "
            f"Pwedeng mag-spray, mag-fertilize, o mag-harvest ng {crop_type}."
        )
    return " ".join(advisories)

# ─────────────────────────────────────────────────────────────
# Seasonal forecast
# ─────────────────────────────────────────────────────────────

@st.cache_data(ttl=86400)  # cache 24 hours — seasonal data barely changes
def get_seasonal_forecast(lat: float, lng: float, months: int = 5):
    """
    Fetch a seasonal outlook from Open-Meteo's seasonal API,
    aggregated into monthly summaries. Returns a list of dicts
    or None on failure.
    """
    url = "https://seasonal-api.open-meteo.com/v1/seasonal"
    params = {
        "latitude": lat,
        "longitude": lng,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "forecast_days": min(months * 30, 274),  # API max ~9 months
        "timezone": "Asia/Manila",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        daily = r.json().get("daily", {})
        dates = daily.get("time", [])
        if not dates:
            return None

       # Group by month (key: "2026-07")
        monthly = {}
        for i, d in enumerate(dates):
            month_key = d[:7]  # "YYYY-MM"
            rain = daily["precipitation_sum"][i]
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            if month_key not in monthly:
                monthly[month_key] = {"rain": [], "tmax": [], "tmin": []}
            if rain is not None:
                monthly[month_key]["rain"].append(rain)
            if tmax is not None:
                monthly[month_key]["tmax"].append(tmax)
            if tmin is not None:
                monthly[month_key]["tmin"].append(tmin)
        month_names = {
            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr",
            "05": "May", "06": "Jun", "07": "Jul", "08": "Aug",
            "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec",
        }

        results = []
        for key in sorted(monthly.keys()):
            m = monthly[key]
            if not m["rain"] or not m["tmax"]:
                continue
            year, month_num = key.split("-")
            results.append({
                "key": key,                       # "2026-07"  ← NEW
                "month": f"{month_names[month_num]} {year}",
                "total_rain_mm": round(sum(m["rain"]), 1),
                "avg_temp_max": round(sum(m["tmax"]) / len(m["tmax"]), 1),
                "avg_temp_min": round(sum(m["tmin"]) / len(m["tmin"]), 1),
                "rainy_days": sum(1 for r in m["rain"] if r >= 1.0),
            })
        return results
    except Exception:
        return None


def get_season_info(month: int) -> dict:
    """
    Wet/dry season classification for Central Mindanao.
    Rainfall peaks roughly May-October.
    """
    if month in (5, 6, 7, 8, 9, 10):
        return {
            "season": "Tag-ulan (Wet season)",
            "icon": "🌧",
            "advice": ("Bantayan ang drainage at posibleng baha.")
        }
    return {
        "season": "Mas tuyong buwan (Drier months)",
        "icon": "☀",
        "advice": ("Magandang panahon para sa pag-aani at pagpapatuyo. "
                   "Siguraduhing may sapat na irigasyon kung magtatanim."),
    }