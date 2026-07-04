"""
harvest.py
Harvest date estimation based on crop maturity duration,
with weather-aware harvest advisories.
"""

from datetime import date, datetime, timedelta

# Days from planting to harvest (typical PH values, adjustable)
CROP_MATURITY = {
    "Rice":      {"min_days": 110, "max_days": 125},   # inbred/hybrid range
    "Corn":      {"min_days": 90,  "max_days": 110},
    "Sugarcane": {"min_days": 300, "max_days": 365},
    # Perennials: first harvest after planting, then continuous
    "Banana":    {"min_days": 270, "max_days": 365, "perennial": True},
    "Coconut":   {"min_days": 2190, "max_days": 2920, "perennial": True},  # 6-8 yrs
}


def estimate_harvest(crop_type: str, date_planted) -> dict | None:
    info = CROP_MATURITY.get(crop_type)
    if not info:
        return None

    # Convert string from SQLite to a date object
    if isinstance(date_planted, str):
        date_planted = datetime.strptime(date_planted[:10], "%Y-%m-%d").date()
    elif isinstance(date_planted, datetime):
        date_planted = date_planted.date()

    early = date_planted + timedelta(days=info["min_days"])
    late = date_planted + timedelta(days=info["max_days"])
    today = date.today()

    days_to_early = (early - today).days
    total = info["max_days"]
    elapsed = (today - date_planted).days
    progress = max(0.0, min(1.0, elapsed / total))

    if today > late:
        status = "overdue"       # past harvest window
    elif today >= early:
        status = "ready"         # within harvest window
    else:
        status = "growing"

    return {
        "early": early,
        "late": late,
        "days_to_early": days_to_early,
        "progress": progress,
        "status": status,
        "perennial": info.get("perennial", False),
    }


def harvest_advice(est: dict, crop_type: str, days: list | None) -> str:
    """Taglish advisory combining harvest window + weather forecast."""
    if est["status"] == "growing":
        msg = (f"Ang iyong {crop_type} ay aanihin sa loob ng "
               f"{est['days_to_early']} araw (mga {est['early'].strftime('%b %d, %Y')}).")
    elif est["status"] == "ready":
        msg = (f"Puwede nang anihin ang iyong {crop_type}! "
               f"Harvest window: {est['early'].strftime('%b %d')} – "
               f"{est['late'].strftime('%b %d, %Y')}.")
    else:
        msg = (f"Lampas na sa inaasahang harvest window ang iyong {crop_type} "
               f"({est['late'].strftime('%b %d, %Y')}). Suriin ang bukid.")

    # Weather-aware add-on: warn if rain during a ready/near-ready window
    if days and est["status"] in ("ready", "growing") and est["days_to_early"] <= 5:
        rainy = [d["date"][5:] for d in days if d["rain_pct"] >= 60]
        if rainy:
            msg += (f" ⚠ May inaasahang ulan sa {', '.join(rainy)} — "
                    f"kung maaari, mag-ani bago o pagkatapos ng ulan para "
                    f"maiwasan ang basang ani at post-harvest losses.")
        else:
            msg += " ☀ Maganda ang panahon — magandang pagkakataon para mag-ani at magpatuyo."

    return msg