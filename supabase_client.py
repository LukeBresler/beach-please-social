"""
Reads the latest cached conditions row from the same Supabase table the
iOS app reads (`conditions`), written by your existing Cloudflare Worker.
Uses the anon key -- the same one already compiled into the shipped app,
so this doesn't expose anything the app doesn't already expose. Read-only:
this script never writes to Supabase.
"""

import os
import requests

# `or` (not a get() default): GitHub Actions passes an UNSET secret as an empty
# string, which must fall back to the built-in default rather than be used as-is.
SUPABASE_URL = os.environ.get("SUPABASE_URL") or "https://dwqsxoozhoeaojhodckk.supabase.co"
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") or (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR3cXN4b296aG9lYW9qaG9kY2trIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEyMjMwNjMsImV4cCI6MjA4Njc5OTA2M30.-ZvHDG3l0rNuF482FRy_Ia3FgsyGoNHjxEFDg9xvx6E"
)


class NoConditionsData(Exception):
    pass


def fetch_latest_conditions() -> dict:
    """
    Returns a normalized dict:
    {
      wind_speed, wind_direction,
      tide_phase, tide_status, spring_tide,
      water_temp_atlantic, water_temp_falsebay,
      timestamp
    }
    Raises NoConditionsData if the table is empty or unreachable.
    """
    url = f"{SUPABASE_URL}/rest/v1/conditions"
    params = {"select": "*", "order": "timestamp.desc", "limit": "1"}
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    }
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    rows = resp.json()
    if not rows:
        raise NoConditionsData("`conditions` table returned no rows")

    row = rows[0]
    weather = row["weather_data"]
    tide = row.get("tide_data") or {}

    return {
        "wind_speed": weather["windSpeed"],
        "wind_direction": weather["windDirection"],
        "tide_phase": tide.get("phase"),
        "tide_status": tide.get("status"),
        "spring_tide": tide.get("springTide", False),
        "water_temp_atlantic": weather.get("waterTemperature"),
        "water_temp_falsebay": weather.get("falseBayWaterTemperature")
        or (round((weather.get("waterTemperature", 0) + 3) * 10) / 10
            if weather.get("waterTemperature") is not None else None),
        "timestamp": row.get("timestamp"),
    }


# Realistic fallback used only in --dry-run/testing when Supabase is
# unreachable (e.g. this sandbox's outbound network is restricted).
FALLBACK_CONDITIONS = {
    "wind_speed": 14,
    "wind_direction": "SE",
    "tide_phase": "mid",
    "tide_status": "rising",
    "spring_tide": False,
    "water_temp_atlantic": 16.2,
    "water_temp_falsebay": 19.5,
    "timestamp": None,
}
