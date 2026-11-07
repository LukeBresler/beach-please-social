"""
Evening fact bank: alternates between a Cape Town beach/tidal-pool fact and
a Beach, Please! app fact. Plain data -- no API calls, no cost.

Rotation is deterministic (by day-of-year index), so the bot never needs to
remember what it posted last: every run recomputes the same slot for that
calendar day, and re-running the same day is idempotent.
"""

BEACH_FACTS = [
    "St James Tidal Pool's rainbow bathing boxes are one of the most photographed spots in the whole city — and they're only there because Victorian-era beachgoers changed in private, wheeled huts.",
    "Boulders Beach is home to roughly 3,000 African penguins living wild among granite boulders that are over 540 million years old.",
    "Dalebrook Tidal Pool in Kalk Bay was built in 1907 — it's one of the oldest tidal pools still in daily use on the peninsula.",
    "Camps Bay and Muizenberg sit on opposite coasts of the same peninsula, so their water temperature can differ by more than 5°C on the same afternoon.",
    "Muizenberg's gentle break made it the birthplace of South African surfing over 100 years ago — it's still where most Capetonians learn.",
    "The 'Cape Doctor' — that relentless summer southeaster — is named for supposedly blowing pollution and disease out of the old city. Kitesurfers at Bloubergstrand have it to thank.",
    "Maiden's Cove was historically one of the few beaches people of colour were legally allowed to use during apartheid — its tidal pools carry real weight beyond the view.",
    "Smitswinkel Bay has five navy ships deliberately sunk offshore as an artificial reef — a quiet, car-free bay reached only by a 15-minute hike.",
    "False Bay water runs noticeably warmer than the Atlantic side because it's shallower and more sheltered from the cold Benguela current.",
    "Fish Hoek's shark spotters have been watching the bay from the hills on foot since 2004 — one of the oldest volunteer shark-safety programmes in the world.",
    "Llandudno has no streetlights and very limited parking by design — locals have fought to keep it that way for decades.",
    "Clifton's four beaches are separated by granite boulders, and each one has a slightly different personality — 4th is the family one, 2nd draws the crowds.",
    "Oudekraal's kelp forests are dense enough that snorkelling there feels like swimming through a small underwater jungle.",
    "A 'spring tide' has nothing to do with the season — it happens twice a month at full and new moon, when the sun and moon's pull line up.",
    "Bikini Beach in Gordon's Bay got its name from Stellenbosch students who made it their go-to summer spot, not from the swimwear.",
    "Seaforth Beach is the free, walk-in alternative to Boulders — the same penguins wander across from the colony next door.",
    "Windmill Beach near Simon's Town is a near-twin of Boulders in miniature — same boulders, same penguins, a fraction of the visitors.",
    "Blue Flag status isn't just about clean water — beaches have to meet strict standards on safety, facilities, and environmental management to keep it.",
]

APP_FACTS = [
    "Beach, Please! scores every beach and tidal pool fresh using live wind, tide and water temperature data — not a fixed 'best of' list that never changes.",
    "The app's recommendation score checks whether a beach is actually sheltered from today's wind direction, not just whether it's sheltered in general.",
    "Tidal pools get scored differently to open beaches in the app — tide phase matters a lot more for a pool than for a stretch of open sand.",
    "Every beach in Beach, Please! is tagged with which wind directions it's naturally protected from, built from real local knowledge of the coastline.",
    "The app treats spring tides specially — they push tidal pools higher (often a plus) while making tide-sensitive beaches trickier.",
    "Beach, Please! separates Atlantic and False Bay water temperatures, because treating Cape Town's two coastlines as one average would hide a 5°C+ difference.",
    "Behind the scenes, a scheduled worker refreshes wind, tide and water data on its own — so opening the app never means waiting on a slow API call.",
]


def fact_for_day(day_of_year: int) -> dict:
    """
    Alternates beach-fact / app-fact by day, and picks a rotating index
    within each list so nothing repeats until the whole list is exhausted.
    """
    use_app_fact = day_of_year % 3 == 0  # 1 in 3 evenings is an app fact
    if use_app_fact:
        facts = APP_FACTS
        kind = "app"
    else:
        facts = BEACH_FACTS
        kind = "beach"
    idx = day_of_year % len(facts)
    return {"kind": kind, "text": facts[idx]}
