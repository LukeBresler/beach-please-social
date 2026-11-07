"""
Rain / cloud / storm forecast for a beach, from Open-Meteo (no API key).

Rules from the tone guide, enforced here:
  - Only report what the forecast says, in chances and times, never certainties.
  - A thunderstorm in the window is flagged so the caller can stand the post down.
  - If the forecast can't be fetched, return nothing: the post goes out without
    any weather claim rather than guessing.
Weather is kept separate from the app's score (the score doesn't include it).
"""

import re
from datetime import datetime, timezone, timedelta

import requests

SAST = timezone(timedelta(hours=2))
API = "https://api.open-meteo.com/v1/forecast"

WINDOW_HOURS = 8                 # how far ahead the post is relevant
DAYLIGHT = (6, 19)               # only judge daylight hours
RAIN_PROB_WET = 40               # % at/above which an hour counts as wet
RAIN_PROB_DRY = 30               # % below which an hour counts as dry
CLOUDY_MEAN = 60                 # mean cloud cover % above which we mention cloud
THUNDER_CODES = set(range(95, 100))   # WMO 95-99 = thunderstorm


def fetch_hourly(lat: float, lon: float) -> dict:
    r = requests.get(
        API,
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation_probability,precipitation,cloud_cover,weather_code",
            "timezone": "Africa/Johannesburg",
            "forecast_days": 2,
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["hourly"]


def summarise(hourly: dict, now: datetime, window_hours: int = WINDOW_HOURS) -> dict:
    """Pure function (testable offline): reduce hourly data to what the caption needs."""
    start = now.replace(minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=window_hours)
    rows = []
    for i, t in enumerate(hourly["time"]):
        ts = datetime.fromisoformat(t).replace(tzinfo=SAST)
        if not (start <= ts < end and DAYLIGHT[0] <= ts.hour <= DAYLIGHT[1]):
            continue
        rows.append({
            "hour": ts.hour,
            "prob": hourly["precipitation_probability"][i] or 0,
            "mm": hourly["precipitation"][i] or 0.0,
            "cloud": hourly["cloud_cover"][i] or 0,
            "code": hourly["weather_code"][i],
        })
    if not rows:
        return {}

    wet = [r for r in rows if r["prob"] >= RAIN_PROB_WET or r["mm"] >= 0.2]
    dry_window = None
    run = []
    for r in rows + [None]:
        if r is not None and r["prob"] < RAIN_PROB_DRY and r["mm"] < 0.1:
            run.append(r)
            continue
        if len(run) >= 2 and dry_window is None:
            dry_window = (run[0]["hour"], run[-1]["hour"] + 1)
        run = []

    return {
        "storm": any(r["code"] in THUNDER_CODES for r in rows),
        "wet": bool(wet),
        "max_prob": max(r["prob"] for r in rows),
        "first_wet_hour": wet[0]["hour"] if wet else None,
        "mean_cloud": sum(r["cloud"] for r in rows) / len(rows),
        "dry_window": dry_window,
    }


def weather_line(s: dict) -> "str | None":
    """One short, honest line, or None on a clear/dry day."""
    if not s or s.get("storm"):
        return None
    if s["wet"]:
        line = f"Up to {int(s['max_prob'])}% chance of showers from {s['first_wet_hour']:02d}:00."
        if s["dry_window"] and s["dry_window"][0] < s["first_wet_hour"]:
            line += f" Best window {s['dry_window'][0]:02d}:00 to {s['dry_window'][1]:02d}:00."
        return line
    if s["mean_cloud"] >= CLOUDY_MEAN:
        return "Cloudy for most of the day."
    return None


def get_weather_line(beach, now: "datetime | None" = None) -> "tuple[str | None, bool]":
    """Returns (line_or_None, storm_flag). Never raises: a failed forecast means no weather claim."""
    now = now or datetime.now(SAST)
    try:
        s = summarise(fetch_hourly(beach.latitude, beach.longitude), now)
    except Exception as e:  # noqa: BLE001
        print(f"WARNING: forecast unavailable ({type(e).__name__}); posting without a weather line.")
        return None, False
    return weather_line(s), bool(s.get("storm"))
