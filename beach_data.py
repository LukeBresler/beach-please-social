"""
Beach data + scoring, ported 1:1 from the real Beach, Please! iOS app
(BeachScoring.swift / WeatherDataModel.swift / AppState.swift), so the
Instagram bot ranks beaches exactly the way the app does.

If you add/edit beaches in the app's `capeTownBeaches` array, mirror the
change here too -- this is a deliberate duplicate, not a shared import,
because the app is Swift and this bot is Python.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Beach:
    id: int
    name: str
    latitude: float
    longitude: float
    sheltered: bool
    sheltered_from: list       # e.g. ["SE", "S"]
    description: str
    exposure: str
    type: str                  # "beach" | "pool"
    tide_relevance: str        # "low" | "medium" | "high" | "critical"
    ocean_side: str            # "atlantic" | "falsebay"
    blue_flag: bool = False
    facilities: bool = False
    accessible: bool = False
    lifeguards: bool = False
    dog_policy: str = ""


# Ported verbatim from capeTownBeaches in WeatherDataModel.swift
CAPE_TOWN_BEACHES = [
    Beach(1, "Bikini Beach", -34.1619, 18.8668, True, ["SE", "S", "SW"],
          "A compact Blue Flag beach tucked beside Gordon's Bay harbour on the far eastern shore of False Bay, with panoramic views of the Hottentots Holland mountains. Warm, calm and clear water; named after the Stellenbosch students who have long made it their summer haunt.",
          "NW, W", "beach", "low", "falsebay", blue_flag=True, facilities=False, accessible=False, lifeguards=False),
    Beach(2, "Bloubergstrand", -33.8097, 18.4347, False, ["E", "SE"],
          "Home to the most iconic postcard view of Table Mountain across Table Bay, and Cape Town's premier kitesurfing destination. The Cape Doctor SE wind blows strong and constant, making this one of the world's top spots for kiteboarders and windsurfers.",
          "All directions", "beach", "low", "atlantic", blue_flag=False, facilities=True, accessible=True, lifeguards=True),
    Beach(3, "Boulders Beach", -34.1974, 18.4507, True, ["NW", "W", "N"],
          "A world-famous penguin sanctuary within Table Mountain National Park, where a colony of around 3,000 endangered African penguins lives freely among 540-million-year-old granite boulders. Wooden boardwalks allow close-up observation; entry fee applies.",
          "SE, S", "beach", "high", "falsebay", blue_flag=False, facilities=True, accessible=True, lifeguards=False),
    Beach(4, "Camps Bay", -33.9503, 18.3777, False, ["E"],
          "Cape Town's iconic 'see and be seen' beach, backed by the Twelve Apostles and fronted by a palm-lined strip of upscale bars and restaurants. Wide white sand with strong Atlantic waves and a legendary sundowner culture.",
          "SE, S, SW, W, NW", "beach", "low", "atlantic", blue_flag=True, facilities=True, accessible=True, lifeguards=True),
    Beach(5, "Camps Bay Tidal Pool", -33.9512, 18.3774, False, ["E"],
          "A bracing Atlantic tidal pool at the southern end of Camps Bay beach, with spectacular views of the Twelve Apostles. The cold water is a refreshing contrast to the glamorous strip just steps away; a favourite with locals for sunrise and sunset swims.",
          "W, NW, SE", "pool", "critical", "atlantic", blue_flag=False, facilities=True, accessible=True, lifeguards=True),
    Beach(6, "Clifton 4th Beach", -33.9393, 18.376, True, ["SE", "S"],
          "Cape Town's glamour beach, sheltered from SE wind by Lion's Head. Powdery white sand, icy Atlantic water and yachts anchoring offshore in summer. The most family-friendly of Clifton's four granite-boulder-separated coves.",
          "W, NW", "beach", "low", "atlantic", blue_flag=True, facilities=True, accessible=False, lifeguards=True),
    Beach(7, "Dalebrook Tidal Pool", -34.1115, 18.4693, True, ["NW", "W", "SW", "S"],
          "Built in 1907, one of Cape Town's oldest and most beloved tidal pools in Kalk Bay, facing east to catch the morning sunrise over False Bay. A large central boulder is a landmark for the strong swimming community here; maintained using eco-friendly methods since 2017.",
          "SE, E", "pool", "critical", "falsebay", blue_flag=False, facilities=True, accessible=False, lifeguards=False),
    Beach(8, "Dias Beach", -34.3569, 18.4972, False, ["N", "NE"],
          "One of the Cape's most remote and spectacular beaches, accessible only by a steep hike inside Cape Point Nature Reserve. Powerful Atlantic swells crash beneath towering cliffs. Swimming is unsafe, but the raw, end-of-the-world scenery is unforgettable.",
          "W, SW, S, SE", "beach", "high", "atlantic", blue_flag=False, facilities=False, accessible=False, lifeguards=False),
    Beach(9, "Fish Hoek", -34.1363, 18.4324, True, ["NW", "W"],
          "One of False Bay's safest and most family-friendly beaches. 1.5km of flat white sand in a sheltered bay with warmer waters than the Atlantic side. Colourful Victorian bathing boxes, shark spotters on duty, and the scenic Jager Walk leading to coastal rock pools.",
          "S, SE", "beach", "low", "falsebay", blue_flag=True, facilities=True, accessible=True, lifeguards=True),
    Beach(10, "Glen Cairn", -34.1275, 18.4367, True, ["NW", "W", "SW"],
          "A relaxed, locals-favourite False Bay beach between Fish Hoek and Simon's Town, reachable by train. Gentle seas suit swimmers and bodyboarders; a tidal pool sits on the southern end and the wide bay offers excellent whale watching from June to November.",
          "S, SE", "beach", "medium", "falsebay", blue_flag=False, facilities=False, accessible=False, lifeguards=False),
    Beach(11, "Hout Bay", -34.0447, 18.3501, True, ["N", "NE", "E"],
          "A broad arc of white sand framed by the towering cliffs of Chapman's Peak and the Sentinel in a historic fishing village bay. Calm swimming and watersports, with a working harbour nearby full of seafood restaurants and the popular Bay Harbour craft market.",
          "S, SW, W", "beach", "low", "atlantic", blue_flag=False, facilities=True, accessible=True, lifeguards=True),
    Beach(12, "Kalk Bay Tidal Pool", -34.1286, 18.4481, True, ["NW", "W"],
          "A charming tidal pool set within the eclectic harbour village of Kalk Bay, tucked between St James and Dalebrook. Sheltered enough for calm swimming and surrounded by the antique shops, galleries and seafood restaurants that give Kalk Bay its unmistakable character.",
          "S, SE", "pool", "critical", "falsebay", blue_flag=False, facilities=False, accessible=False, lifeguards=True),
    Beach(13, "Llandudno", -34.0047, 18.3431, True, ["SE", "E", "NE"],
          "A secluded cove between Camps Bay and Hout Bay, framed by giant granite boulders and fynbos-covered mountains. No shops or streetlights; limited parking keeps it peacefully uncrowded. Powerful waves attract experienced surfers; Sunset Rocks is a classic sundowner spot.",
          "W, SW", "beach", "medium", "atlantic", blue_flag=True, facilities=True, accessible=False, lifeguards=True),
    Beach(14, "Maiden's Cove Tidal Pool", -33.9467, 18.3758, True, ["SE", "S", "E"],
          "Two sheltered tidal pools among granite boulders between Clifton and Camps Bay, with views of the Twelve Apostles and grassy braai and picnic lawns. Historically significant as one of few beaches accessible to people of colour during apartheid; magical at sunset.",
          "W, NW", "pool", "critical", "atlantic", blue_flag=False, facilities=True, accessible=True, lifeguards=True),
    Beach(15, "Melkbosstrand", -33.7245, 18.4392, False, ["E", "SE"],
          "A long Atlantic beach 30km north of Cape Town, offering classic views of Table Mountain and Robben Island across Table Bay. Wide, flat sands with a promenade and restaurants; popular for kitesurfing, family outings, and watching spectacular west-facing sunsets.",
          "W, SW, NW", "beach", "low", "atlantic", blue_flag=True, facilities=True, accessible=True, lifeguards=True),
    Beach(16, "Muizenberg", -34.1032, 18.4742, True, ["NW", "W", "SW"],
          "Cape Town's legendary beginner surf beach on the warmer False Bay side, home to Surfer's Corner and over 100 years of surfing history. Gentle rolling waves, colourful Victorian bathing boxes, and shark spotters on the hills above.",
          "S, SE", "beach", "medium", "falsebay", blue_flag=True, facilities=True, accessible=True, lifeguards=True),
    Beach(17, "Oudekraal Tidal Pool", -33.9722, 18.3631, True, ["SE", "E", "NE"],
          "A secluded SANParks picnic spot within Table Mountain National Park, with a rock pool set among milkwood trees and ancient Atlantic boulders. Known for superb snorkelling through rich kelp forests and diverse marine life; a peaceful escape with mountain and ocean views.",
          "W, SW", "pool", "critical", "atlantic", blue_flag=False, facilities=True, accessible=True, lifeguards=True),
    Beach(18, "Scarborough", -34.1986, 18.3697, False, [],
          "A wild, unhurried conservation village beach at the edge of Cape Point Nature Reserve, backed by low fynbos dunes and craggy peaks. Beloved by surfers, dog walkers, and those seeking unspoiled Atlantic scenery, and rarely crowded even at peak season.",
          "All directions", "beach", "medium", "atlantic", blue_flag=False, facilities=False, accessible=False, lifeguards=False),
    Beach(19, "Seaforth Beach", -34.1932, 18.4523, True, ["NW", "W", "N"],
          "The 'free alternative' to Boulders Beach. A beautiful, granite-boulder-framed cove in Simon's Town where African penguins regularly venture across from the nearby colony. Grassy slopes perfect for picnics, calm water safe for children, and a beachfront restaurant.",
          "S, SE", "beach", "medium", "falsebay", blue_flag=False, facilities=True, accessible=False, lifeguards=False),
    Beach(20, "Silwerstroomstrand", -33.5560, 18.3430, False, ["E", "SE"],
          "A wide, open Atlantic beach 65km north of Cape Town, prized for its vast space and clean Blue Flag waters. The Silwerstroom Resort provides braai facilities and a beach pool, making it a popular family day-trip escape; strong westerlies attract kitesurfers.",
          "W, SW, NW", "beach", "low", "atlantic", blue_flag=True, facilities=True, accessible=True, lifeguards=True),
    Beach(21, "Smitswinkel Bay", -34.2156, 18.4513, True, ["NW", "W", "N", "NE"],
          "One of Cape Town's best-kept secrets - a remote, car-free bay reached by a steep 15-minute hike just before Cape Point Reserve. Famous among divers for five deliberately-sunk navy wrecks forming an artificial reef; pristine rock pools and sweeping False Bay views.",
          "SE, S", "beach", "medium", "falsebay", blue_flag=False, facilities=False, accessible=False, lifeguards=False),
    Beach(22, "St James Tidal Pool", -34.1186, 18.4583, True, ["NW", "W", "SW"],
          "Cape Town's most photographed tidal pool, framed by iconic multicoloured Victorian bathing huts against a backdrop of mountains. Large, calm and family-friendly with easy wade-in access; right beside the train station and one of the False Bay coast's most cheerful spots.",
          "S, SE", "pool", "critical", "falsebay", blue_flag=False, facilities=True, accessible=False, lifeguards=True),
    Beach(23, "Windmill Beach", -34.2386, 18.4728, True, ["NW", "W"],
          "A tranquil boulder-sheltered beach tucked behind Simon's Town's golf course, very similar in character to nearby Boulders. Penguins from the adjacent colony regularly wander across; calm False Bay water and a grassy picnic slope make it ideal for families.",
          "SE, S, E", "beach", "medium", "falsebay", blue_flag=False, facilities=False, accessible=False, lifeguards=False),
]


def recommendation_score(beach: Beach, wind_speed: float, wind_direction: str,
                          tide_phase: Optional[str], tide_status: Optional[str],
                          spring_tide: bool) -> int:
    """Ported 1:1 from BeachScoring.recommendationScore (BeachScoring.swift)."""
    score = 50
    protected_now = wind_direction in beach.sheltered_from

    if protected_now:
        score += 30
    if beach.sheltered:
        score += 20
    if beach.blue_flag:
        score += 5
    if wind_speed < 15:
        score += 10
    if wind_speed > 25 and not protected_now:
        score -= 30

    if tide_phase is not None:
        if beach.tide_relevance == "critical":
            if tide_phase == "high" or (tide_phase == "mid" and tide_status == "rising"):
                score += 15
            elif tide_phase == "low":
                score -= 25
        elif beach.tide_relevance == "high":
            if tide_phase == "low":
                score += 10
            elif tide_phase == "high":
                score -= 10

        if spring_tide:
            if beach.type == "pool":
                score += 5
            elif beach.tide_relevance == "high":
                score -= 5

    return max(0, min(100, score))


def water_temp_label(temp: float) -> str:
    """Ported from AppState.waterTempColorAndLabel."""
    if temp < 14:
        return "Cold"
    if temp < 17:
        return "Cool"
    if temp < 20:
        return "Moderate"
    return "Warm"


def rank_all(conditions: dict) -> list:
    """
    Returns every beach scored + ranked under current conditions, sorted
    best-first. `conditions` = {wind_speed, wind_direction, tide_phase,
    tide_status, spring_tide, water_temp_atlantic, water_temp_falsebay}.
    """
    results = []
    for b in CAPE_TOWN_BEACHES:
        score = recommendation_score(
            b,
            conditions["wind_speed"],
            conditions["wind_direction"],
            conditions.get("tide_phase"),
            conditions.get("tide_status"),
            conditions.get("spring_tide", False),
        )
        temp = (conditions.get("water_temp_falsebay") if b.ocean_side == "falsebay"
                else conditions.get("water_temp_atlantic"))
        results.append({"beach": b, "score": score, "water_temp": temp})
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def top_of_type(ranked: list, beach_type: str, n: int = 1) -> list:
    return [r for r in ranked if r["beach"].type == beach_type][:n]
