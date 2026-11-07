"""
Punchy caption generation. No LLM call -- everything is template + real
data, so this stays genuinely free and never depends on an API key you'd
have to pay for. Variety comes from rotating template sets keyed off the
date, not randomness, so a given day+slot always produces the same output
if the workflow retries.
"""

import hashlib
import re

# Tone guide, Safety section: the account ranks comfort, never safety, and never
# comments on sharks or water quality. Any caption text matching this is dropped
# (descriptions) or stands the post down (everything else).
BANNED = re.compile(
    r"\b(safe|safest|safely|unsafe|safety|shark|sharks|rip ?current|rip ?tide|drown\w*|sewage|clean)\b",
    re.I,
)


def is_safe_text(text: str) -> bool:
    return not BANNED.search(text)

HASHTAGS_BEACH = "#BeachPlease #CapeTown #CapeTownBeaches #TableMountain #SouthAfrica"
HASHTAGS_POOL = "#BeachPlease #CapeTown #TidalPool #CapeTownBeaches #SouthAfrica"


def _pick(options: list, seed: str) -> str:
    h = int(hashlib.sha256(seed.encode()).hexdigest(), 16)
    return options[h % len(options)]


def _protected_line(score: int) -> str:
    if score >= 90:
        return "fully protected right now"
    if score >= 75:
        return "holding up well right now"
    if score >= 60:
        return "decent, not perfect"
    return "exposed today — go in with eyes open"


def beach_of_the_slot(entry: dict, slot: str, seed: str, weather_line: "str | None" = None) -> dict:
    """
    entry: {"beach": Beach, "score": int, "water_temp": float|None}
    slot: "morning" | "noon"
    Returns {"headline": str, "caption": str}
    """
    beach = entry["beach"]
    score = entry["score"]
    temp = entry["water_temp"]
    is_pool = beach.type == "pool"
    kind_word = "tidal pool" if is_pool else "beach"

    openers_morning = [
        f"Today's call: {beach.name}.",
        f"{beach.name} is where the day starts.",
        f"First light, best {kind_word}: {beach.name}.",
        f"Start here — {beach.name}.",
    ]
    openers_noon = [
        f"Midday pick: {beach.name}.",
        f"Right now, {beach.name} is the move.",
        f"Lunch-break verdict: {beach.name}.",
        f"{beach.name}, at its best today.",
    ]
    openers = openers_morning if slot == "morning" else openers_noon
    headline = _pick(openers, seed + "headline")

    temp_line = f"{temp:.0f}°C in the water. " if temp is not None else ""
    protection = _protected_line(score)

    closers = [
        "Grab your towel.",
        "Go while it's good.",
        "You've got a window — use it.",
        "No excuses left.",
    ]
    closer = _pick(closers, seed + "closer")

    description = beach.description.split(". ")[0] + "."
    if not is_safe_text(description):
        description = None  # e.g. "safest" / "clean waters" -- not allowed by the tone guide

    lines = [
        headline,
        f"{score}% recommended, {protection}. {temp_line}{closer}",
        *([weather_line] if weather_line else []),
        "",
        *([description, ""] if description else []),
        HASHTAGS_POOL if is_pool else HASHTAGS_BEACH,
    ]
    return {"headline": headline, "caption": "\n".join(lines)}


def fact_caption(fact: dict, seed: str) -> dict:
    openers_beach = [
        "Did you know?",
        "Cape Town trivia:",
        "Local knowledge:",
        "One for the locals:",
    ]
    openers_app = [
        "How Beach, Please! actually works:",
        "Behind the app:",
        "Quick one about the app:",
    ]
    opener = _pick(openers_app if fact["kind"] == "app" else openers_beach, seed)

    lines = [
        opener,
        "",
        fact["text"],
        "",
        HASHTAGS_BEACH,
    ]
    return {"headline": opener, "caption": "\n".join(lines)}
