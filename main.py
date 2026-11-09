"""
Orchestrator. Run as:  python3 main.py render|publish morning|noon|evening
                       python3 main.py verify

Split into two phases on purpose:
  render  -> fetches conditions + forecast, scores beaches, generates the image
             and caption, writes both to posts/, and saves a small metadata
             JSON alongside so `publish` doesn't re-derive anything.
  publish -> reads that metadata JSON and posts to Instagram (or prints a dry run).
  verify  -> checks the Instagram token can see the account, then exits.

Stand-down rules (the post is SKIPPED with a warning, never faked):
  - live conditions unavailable, unparseable or older than MAX_CONDITIONS_AGE_HOURS
  - thunderstorm in the forecast window
  - the caption trips the tone-guide safety filter
A skipped slot exits 0 and shows up as a warning on the Actions run.
The old behaviour of silently posting FALLBACK_CONDITIONS is now dry-run only.
"""

import sys
import os
import re
import json
from datetime import datetime, timezone, timedelta

from beach_data import rank_all, top_of_type
from copy_gen import beach_of_the_slot, fact_caption, _protected_line, is_safe_text
from facts import fact_for_day
from forecast import get_weather_line
from image_gen import render_spot_card, render_fact_card, pick_theme
from supabase_client import fetch_latest_conditions, FALLBACK_CONDITIONS
from instagram_api import publish_or_dry_run, verify_token, is_live

SAST = timezone(timedelta(hours=2))
REPO = os.environ.get("GITHUB_REPOSITORY", "your-username/beach-please-social")
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main"
MAX_CONDITIONS_AGE_HOURS = float(os.environ.get("MAX_CONDITIONS_AGE_HOURS", "3"))


class SkipPost(Exception):
    """Stand this slot down. Not an error: the reason is logged and shown as a warning."""


def _today_sast() -> datetime:
    return datetime.now(SAST)


def _paths(slot: str) -> dict:
    today = _today_sast().strftime("%Y-%m-%d")
    os.makedirs("posts", exist_ok=True)
    stem = f"{today}-{slot}"
    return {
        "image_local": f"posts/{stem}.jpg",
        "image_url": f"{RAW_BASE}/posts/{stem}.jpg",
        "meta": f"posts/{stem}.json",
    }


def _parse_ts(ts):
    if not ts:
        return None
    s = ts.replace("Z", "+00:00")
    s = re.sub(r"\.(\d+)", lambda m: "." + m.group(1)[:6].ljust(6, "0"), s)
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _check_fresh(conditions: dict) -> None:
    ts = _parse_ts(conditions.get("timestamp"))
    if ts is None:
        msg = "conditions timestamp missing or unreadable, cannot tell how fresh the data is"
    else:
        age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
        if age_h <= MAX_CONDITIONS_AGE_HOURS:
            return
        msg = f"conditions are {age_h:.1f}h old (limit {MAX_CONDITIONS_AGE_HOURS:g}h)"
    if is_live():
        raise SkipPost(msg)
    print(f"WARNING (dry run, continuing): {msg}")


def _get_conditions() -> dict:
    try:
        conditions = fetch_latest_conditions()
    except Exception as e:  # noqa: BLE001
        if is_live():
            raise SkipPost(f"could not fetch live conditions ({type(e).__name__})") from None
        print(f"WARNING: could not fetch live conditions ({e}); using fallback data (dry run only).")
        return FALLBACK_CONDITIONS
    _check_fresh(conditions)
    return conditions


def _write_meta(paths: dict, payload: dict) -> None:
    with open(paths["meta"], "w") as f:
        json.dump(payload, f)


def render_morning_or_noon(slot: str) -> None:
    conditions = _get_conditions()
    ranked = rank_all(conditions)

    beach_type = "beach" if slot == "morning" else "pool"
    top = top_of_type(ranked, beach_type, 1) or ranked[:1]
    entry = top[0]

    weather_line, storm = get_weather_line(entry["beach"])
    if storm:
        raise SkipPost(
            f"thunderstorm in the forecast for {entry['beach'].name}: needs a human decision "
            "(tone guide: stay off the beach, name no pick)"
        )

    seed = f"{_today_sast():%Y-%m-%d}-{slot}"
    copy = beach_of_the_slot(entry, slot, seed, weather_line)
    if not is_safe_text(copy["caption"]):
        raise SkipPost("caption tripped the safety filter")
    paths = _paths(slot)

    render_spot_card(
        beach_name=entry["beach"].name,
        kind_label="Tidal Pool" if entry["beach"].type == "pool" else "Beach",
        score=entry["score"],
        temp=entry["water_temp"],
        protection_text=_protected_line(entry["score"]),
        headline=copy["headline"],
        out_path=paths["image_local"],
        theme=pick_theme(_today_sast().date(), slot),
    )
    _write_meta(paths, {"image_url": paths["image_url"], "caption": copy["caption"], "slot": slot})
    print(f"Rendered {paths['image_local']} -> will publish as {paths['image_url']}")
    print(f"Weather line: {weather_line or '(none: clear/dry or forecast unavailable)'}")


def render_evening() -> None:
    day_of_year = _today_sast().timetuple().tm_yday
    seed = f"{_today_sast():%Y-%m-%d}-evening"
    for offset in range(15):  # skip facts the tone guide doesn't allow (sharks, "clean water", ...)
        fact = fact_for_day(day_of_year + offset)
        if is_safe_text(fact["text"]):
            break
    else:
        raise SkipPost("no fact passed the safety filter")
    copy = fact_caption(fact, seed)
    paths = _paths("evening")

    render_fact_card(opener=copy["headline"], fact_text=fact["text"], out_path=paths["image_local"],
                     theme=pick_theme(_today_sast().date(), "evening"))
    _write_meta(paths, {"image_url": paths["image_url"], "caption": copy["caption"], "slot": "evening"})
    print(f"Rendered {paths['image_local']} -> will publish as {paths['image_url']}")


def publish(slot: str) -> None:
    paths = _paths(slot)
    with open(paths["meta"]) as f:
        meta = json.load(f)
    if meta.get("skip"):
        print(f"::warning::[{slot}] SKIPPED, nothing posted: {meta['skip']}")
        return
    publish_or_dry_run(meta["image_url"], meta["caption"], meta["slot"])


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "verify":
        print(f"Token OK: can see @{verify_token()}")
        sys.exit(0)

    if len(sys.argv) != 3 or sys.argv[1] not in ("render", "publish") or sys.argv[2] not in ("morning", "noon", "evening"):
        print("Usage: python3 main.py render|publish morning|noon|evening   |   python3 main.py verify")
        sys.exit(1)

    action, slot = sys.argv[1], sys.argv[2]
    if action == "render":
        try:
            if slot == "evening":
                render_evening()
            else:
                render_morning_or_noon(slot)
        except SkipPost as why:
            _write_meta(_paths(slot), {"skip": str(why), "slot": slot})
            print(f"::warning::[{slot}] SKIPPED, nothing will be posted: {why}")
    else:
        publish(slot)
