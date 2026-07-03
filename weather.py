"""
weather.py
Weather fetching and farm-advisory helper logic using the free
Open-Meteo API (no API key required).
"""

import requests

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
