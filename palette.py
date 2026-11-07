"""
Beach, Please! social palette -- v2, "sophisticated fun in the sun."

Bright tropical pink + teal-leaning tropical blue + a light sunny yellow,
grounded by a deep ink and generous white space so it reads as resort-chic
rather than kids'-party bright. Only two colours ever share a card at full
saturation (teal gradient + one accent); the rest is restraint.
"""

TEAL_DEEP = "#0B7C82"       # deep tropical teal -- primary brand colour, backgrounds
TEAL_BRIGHT = "#2FE0D6"     # bright lagoon teal-blue -- gradients
PINK = "#FF4FA0"            # bright tropical pink -- the "fun," used as a deliberate accent
YELLOW = "#FFDE7A"          # light sunny yellow -- secondary accent, warmth in small doses
CREAM = "#FFF8EC"           # warm off-white -- light backgrounds/cards, softer than stark white
INK = "#0B2E33"             # deep teal-black -- body text, keeps it grounded/sophisticated
WHITE = "#FFFFFF"

# Kept as a legacy alias so nothing else needs renaming.
SAND = CREAM


def score_color(score: int) -> str:
    """Status colour for the recommendation score -- deliberately its own
    system (green/yellow/pink), distinct from which brand colours a given
    card uses, exactly like the app's own 'Protected' badge is."""
    if score >= 90:
        return "#3FBF7F"   # protected green
    if score >= 70:
        return YELLOW
    return PINK
