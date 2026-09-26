"""
ROAM — Activities Search Tool
Finds activities and attractions at destinations matching user interests and pace.
"""

from __future__ import annotations

from schemas.models import Activity, Evidence, SourceType
from tools.base import ToolBase


# Curated activities data by destination
ACTIVITIES_DATABASE: dict[str, list[dict]] = {
    "Rishikesh": [
        {"name": "White-water rafting on the Ganges", "description": "16km rafting from Shivpuri to Rishikesh with Class III-IV rapids", "duration": 3.0, "cost_pp": 800, "category": "adventure", "slot": "morning", "pace_min": "moderate"},
        {"name": "Ganga Aarti at Triveni Ghat", "description": "Mesmerizing evening prayer ceremony on the banks of the Ganges", "duration": 1.0, "cost_pp": 0, "category": "culture", "slot": "evening", "pace_min": "relaxed"},
        {"name": "Beatles Ashram (Chaurasi Kutia)", "description": "Abandoned ashram where The Beatles stayed — art, graffiti, and spiritual history", "duration": 2.0, "cost_pp": 150, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Neer Garh Waterfall trek", "description": "Short 2km trek through forest to a beautiful multi-tier waterfall", "duration": 2.5, "cost_pp": 50, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Ram Jhula & Laxman Jhula walk", "description": "Iconic suspension bridges over the Ganges with temple visits", "duration": 1.5, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Bungee jumping at Jumpin Heights", "description": "India's highest bungee jump — 83m plunge over a rocky gorge", "duration": 2.0, "cost_pp": 3500, "category": "adventure", "slot": "morning", "pace_min": "adventure"},
        {"name": "Yoga session at Parmarth Niketan", "description": "Morning yoga and meditation at one of Rishikesh's largest ashrams", "duration": 1.5, "cost_pp": 0, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Camping by the Ganges", "description": "Riverside beach camping with bonfire and star-gazing", "duration": 12.0, "cost_pp": 1200, "category": "nature", "slot": "evening", "pace_min": "relaxed"},
        {"name": "Cliff jumping at Shivpuri", "description": "Jump from 25-35ft cliffs into deep Ganges pools", "duration": 2.0, "cost_pp": 500, "category": "adventure", "slot": "afternoon", "pace_min": "adventure"},
        {"name": "Walk to Patna Waterfall", "description": "Scenic forest walk to a quiet waterfall, less crowded", "duration": 3.0, "cost_pp": 0, "category": "nature", "slot": "morning", "pace_min": "moderate"},
        {"name": "Sunset at Parmarth Ghat", "description": "Watch the Ganges shimmer at sunset before the evening aarti", "duration": 1.0, "cost_pp": 0, "category": "nature", "slot": "evening", "pace_min": "relaxed"},
    ],
    "Manali": [
        {"name": "Solang Valley adventure sports", "description": "Paragliding, zorbing, and zip-lining with snow-capped mountain backdrop", "duration": 4.0, "cost_pp": 1500, "category": "adventure", "slot": "morning", "pace_min": "active"},
        {"name": "Hadimba Temple", "description": "Ancient wooden temple in a cedar forest, dedicated to Hidimbi Devi", "duration": 1.0, "cost_pp": 0, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Old Manali walk & cafes", "description": "Explore the bohemian village, visit riverside cafes and shops", "duration": 3.0, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Jogini Waterfall trek", "description": "3km uphill trek through pine forest to a sacred waterfall", "duration": 3.0, "cost_pp": 0, "category": "nature", "slot": "morning", "pace_min": "moderate"},
        {"name": "Rohtang Pass day trip", "description": "Drive to 13,050ft — snow activities, stunning Himalayan views", "duration": 8.0, "cost_pp": 2000, "category": "adventure", "slot": "morning", "pace_min": "active"},
        {"name": "Manu Temple & hot springs", "description": "Visit the ancient Manu temple and natural hot water springs at Vashisht", "duration": 2.0, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "River crossing via rope bridge", "description": "Cross the Beas river on rope bridges near Manali", "duration": 1.0, "cost_pp": 200, "category": "adventure", "slot": "afternoon", "pace_min": "moderate"},
    ],
    "McLeodganj": [
        {"name": "Triund trek", "description": "6km moderate trek with panoramic Dhauladhar views — one of India's best easy treks", "duration": 6.0, "cost_pp": 100, "category": "nature", "slot": "morning", "pace_min": "moderate"},
        {"name": "Tsuglagkhang Complex (Dalai Lama's temple)", "description": "Tibetan monastery, museum, and Buddhist temple complex", "duration": 2.0, "cost_pp": 0, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Bhagsu Waterfall", "description": "Short 1km walk to a scenic waterfall with chai stalls", "duration": 1.5, "cost_pp": 0, "category": "nature", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Tibet Museum", "description": "Moving history of Tibetan exile and the struggle for freedom", "duration": 1.0, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Dharamkot village walk", "description": "Quiet village above McLeodganj with forest trails and valley views", "duration": 2.0, "cost_pp": 0, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Cooking class — Tibetan cuisine", "description": "Learn to make momos, thukpa, and tingmo from local Tibetan families", "duration": 3.0, "cost_pp": 500, "category": "food", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "St. John in the Wilderness church", "description": "Gothic stone church from 1852 surrounded by pine and deodar forest", "duration": 0.5, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Sunset from Sunset Point", "description": "Walk to the viewpoint for dramatic sunset over the valley", "duration": 1.0, "cost_pp": 0, "category": "nature", "slot": "evening", "pace_min": "relaxed"},
    ],
    "Jaipur": [
        {"name": "Amber Fort", "description": "Majestic hillside fort with Sheesh Mahal mirror palace and elephant ramps", "duration": 3.0, "cost_pp": 200, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Hawa Mahal", "description": "Iconic Palace of Winds with 953 windows — best at sunrise", "duration": 1.0, "cost_pp": 50, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "City Palace", "description": "Royal palace complex with museums, courtyards, and Rajput architecture", "duration": 2.0, "cost_pp": 300, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Jantar Mantar observatory", "description": "UNESCO World Heritage astronomical instruments from 1734", "duration": 1.0, "cost_pp": 50, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Johari Bazaar shopping & food walk", "description": "Historic bazaar for jewelry, textiles, and legendary street food", "duration": 2.5, "cost_pp": 200, "category": "food", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Nahargarh Fort sunset", "description": "Drive up to the fort for panoramic views of the Pink City at sunset", "duration": 2.0, "cost_pp": 200, "category": "culture", "slot": "evening", "pace_min": "relaxed"},
        {"name": "Block printing workshop at Bagru", "description": "Learn traditional Rajasthani block printing from artisans", "duration": 3.0, "cost_pp": 800, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Chokhi Dhani cultural village", "description": "Rajasthani cultural experience with folk dance, puppet shows, and thali dinner", "duration": 4.0, "cost_pp": 1000, "category": "food", "slot": "evening", "pace_min": "relaxed"},
    ],
    "Mussoorie": [
        {"name": "Kempty Falls", "description": "Popular waterfall with bathing pools, 15km from town", "duration": 2.5, "cost_pp": 50, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Mall Road walk", "description": "The iconic promenade with shops, food stalls, and mountain views", "duration": 2.0, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Lal Tibba viewpoint", "description": "Highest point in Mussoorie with Himalayan panorama via telescope", "duration": 1.5, "cost_pp": 50, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Landour heritage walk", "description": "Walk through Ruskin Bond's neighborhood — colonial homes, Char Dukan, Landour Bakehouse", "duration": 3.0, "cost_pp": 0, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Camel's Back Road walk", "description": "Gentle 3km walk along a ridge with views of Doon Valley and Himalayas", "duration": 1.5, "cost_pp": 0, "category": "nature", "slot": "evening", "pace_min": "relaxed"},
    ],
    "Jim Corbett": [
        {"name": "Jungle safari (Dhikala zone)", "description": "Morning or evening jeep safari for tiger spotting in India's oldest national park", "duration": 4.0, "cost_pp": 3000, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Canter safari (Bijrani zone)", "description": "Open-top vehicle safari through dense forest and grasslands", "duration": 3.0, "cost_pp": 1500, "category": "nature", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Corbett Museum", "description": "Jim Corbett's original house — now a museum about his life and work", "duration": 1.0, "cost_pp": 50, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "River crossing & nature walk", "description": "Guided walk along the Ramganga river — birding and wildlife spotting", "duration": 2.0, "cost_pp": 200, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Garjia Devi Temple", "description": "Temple on a large rock in the middle of the Kosi river", "duration": 1.0, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
    ],
    "Kasol": [
        {"name": "Kheerganga trek", "description": "12km trek through Parvati Valley to hot springs at 3,050m — overnight camp", "duration": 10.0, "cost_pp": 500, "category": "nature", "slot": "morning", "pace_min": "active"},
        {"name": "Chalal village walk", "description": "Easy 30-min forest walk to a quiet Himachali village on the river", "duration": 1.5, "cost_pp": 0, "category": "nature", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Malana village trek", "description": "Trek to the ancient village of Malana with unique customs", "duration": 6.0, "cost_pp": 200, "category": "culture", "slot": "morning", "pace_min": "active"},
        {"name": "Riverside picnic & rock bathing", "description": "Relax by the Parvati River, swim in natural rock pools", "duration": 3.0, "cost_pp": 0, "category": "nature", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Manikaran Gurudwara & hot springs", "description": "Sacred Sikh gurudwara with natural hot springs and langar", "duration": 2.0, "cost_pp": 0, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
    ],
    "Nainital": [
        {"name": "Naini Lake boating", "description": "Paddle or row boat on the famous lake surrounded by hills", "duration": 1.5, "cost_pp": 300, "category": "nature", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Snow View Point ropeway", "description": "Cable car ride to see Himalayan snow peaks", "duration": 1.5, "cost_pp": 300, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Tiffin Top trek", "description": "4km walk through oak and deodar forest to Dorothy's Seat viewpoint", "duration": 2.5, "cost_pp": 0, "category": "nature", "slot": "morning", "pace_min": "moderate"},
        {"name": "Mall Road evening walk", "description": "Stroll along the bustling lakeside promenade with street food", "duration": 1.5, "cost_pp": 0, "category": "culture", "slot": "evening", "pace_min": "relaxed"},
        {"name": "Eco Cave Gardens", "description": "Interconnected rocky caves with animal themes, fun exploration", "duration": 1.0, "cost_pp": 75, "category": "nature", "slot": "afternoon", "pace_min": "relaxed"},
    ],
    "Bir Billing": [
        {"name": "Paragliding from Billing to Bir", "description": "World-class tandem paragliding flight — 30-45 min in the air", "duration": 2.0, "cost_pp": 2500, "category": "adventure", "slot": "morning", "pace_min": "active"},
        {"name": "Chokling Monastery", "description": "Tibetan Buddhist monastery with prayer wheels and meditation garden", "duration": 1.0, "cost_pp": 0, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Tea garden walk", "description": "Stroll through Bir's green tea gardens with mountain views", "duration": 1.5, "cost_pp": 0, "category": "nature", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Gunehar waterfall trek", "description": "Short trek to a hidden waterfall near Billing", "duration": 2.0, "cost_pp": 0, "category": "nature", "slot": "afternoon", "pace_min": "moderate"},
        {"name": "Sunset at landing site", "description": "Watch paragliders land against the sunset at the Bir landing area", "duration": 1.0, "cost_pp": 0, "category": "nature", "slot": "evening", "pace_min": "relaxed"},
    ],
    "Udaipur": [
        {"name": "City Palace complex", "description": "Sprawling lakeside palace with balconies, towers, and courtyards", "duration": 2.5, "cost_pp": 300, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Lake Pichola boat ride", "description": "Sunset boat ride with views of Lake Palace, City Palace, and Aravalli hills", "duration": 1.5, "cost_pp": 400, "category": "culture", "slot": "evening", "pace_min": "relaxed"},
        {"name": "Bagore Ki Haveli folk dance show", "description": "Evening Rajasthani dance performance in a restored 18th-century haveli", "duration": 1.5, "cost_pp": 100, "category": "culture", "slot": "evening", "pace_min": "relaxed"},
        {"name": "Sajjangarh Palace (Monsoon Palace)", "description": "Hilltop palace with panoramic views — best at sunset", "duration": 2.0, "cost_pp": 200, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
        {"name": "Old City heritage walk", "description": "Walk through narrow lanes, havelis, ghats, and local markets", "duration": 3.0, "cost_pp": 0, "category": "culture", "slot": "morning", "pace_min": "relaxed"},
        {"name": "Shilpgram crafts village", "description": "Rural arts and crafts village showcasing western Indian folk traditions", "duration": 1.5, "cost_pp": 50, "category": "culture", "slot": "afternoon", "pace_min": "relaxed"},
    ],
}


PACE_LEVELS = {
    "relaxed": 0,
    "moderate": 1,
    "active": 2,
    "adventure": 3,
}


class ActivitiesTool(ToolBase):
    """Search for activities and attractions at a destination."""

    name = "search_activities"
    description = "Find activities and experiences matching user interests and pace."

    def execute(
        self,
        destination: str = "Rishikesh",
        interests: list[str] | None = None,
        pace: str = "relaxed",
    ) -> list[Activity]:
        interests = interests or ["nature", "food"]

        if destination not in ACTIVITIES_DATABASE:
            return []

        activities_data = ACTIVITIES_DATABASE[destination]
        pace_level = PACE_LEVELS.get(pace, 0)
        results = []

        for act_data in activities_data:
            act_pace = PACE_LEVELS.get(act_data.get("pace_min", "relaxed"), 0)

            # Filter: only include activities suitable for the user's pace
            if act_pace > pace_level + 1:  # Allow one level above for variety
                continue

            # Score against interests
            relevance = 0
            cat = act_data["category"]
            for interest in interests:
                if interest.lower() in cat or cat in interest.lower():
                    relevance += 2
                # Broad matches
                if interest.lower() in ("nature", "outdoors") and cat in ("nature", "adventure"):
                    relevance += 1
                if interest.lower() in ("food", "cuisine", "culinary") and cat == "food":
                    relevance += 2
                if interest.lower() in ("culture", "heritage", "history") and cat == "culture":
                    relevance += 1

            activity = Activity(
                name=act_data["name"],
                description=act_data["description"],
                duration_hours=act_data["duration"],
                cost_per_person=act_data["cost_pp"],
                category=act_data["category"],
                time_slot=act_data["slot"],
                location=destination,
                evidence=Evidence(
                    source=f"ROAM curated activities — {destination}",
                    source_type=SourceType.CURATED,
                    confidence=0.85,
                    data=f"{act_data['name']} — {act_data['description'][:80]}, ~{act_data['duration']}h, ₹{act_data['cost_pp']}/person",
                ),
            )
            # Attach relevance score as a note for sorting
            activity.notes = f"relevance:{relevance}"
            results.append(activity)

        # Sort by relevance (high first), then by slot order
        slot_order = {"morning": 0, "afternoon": 1, "evening": 2}
        results.sort(
            key=lambda a: (
                -int((a.notes or "relevance:0").split(":")[1]) if a.notes else 0,
                slot_order.get(a.time_slot, 1),
            )
        )

        return results
