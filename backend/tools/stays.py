"""
ROAM — Accommodation Search Tool
Searches for stays at destinations with realistic Indian hotel/homestay data.
"""

from __future__ import annotations

from schemas.models import Accommodation, Evidence, SourceType
from tools.base import ToolBase


# Curated accommodation data by destination, tiered by budget
STAYS_DATABASE: dict[str, list[dict]] = {
    "Rishikesh": [
        {"name": "Zostel Rishikesh", "type": "hostel", "cost_per_night": 800, "location": "Tapovan", "rating": 4.2, "amenities": ["wifi", "common kitchen", "river view", "cafe"], "tier": "budget"},
        {"name": "The Hosteller Rishikesh", "type": "hostel", "cost_per_night": 1000, "location": "Laxman Jhula", "rating": 4.3, "amenities": ["wifi", "rooftop", "cafe", "yoga deck"], "tier": "budget"},
        {"name": "Hotel Ganga Kinare", "type": "hotel", "cost_per_night": 3200, "location": "Ram Jhula", "rating": 4.0, "amenities": ["wifi", "AC", "restaurant", "Ganga view", "spa"], "tier": "mid"},
        {"name": "Divine Ganga Cottage", "type": "hotel", "cost_per_night": 2500, "location": "Tapovan", "rating": 4.1, "amenities": ["wifi", "AC", "garden", "restaurant"], "tier": "mid"},
        {"name": "Aloha on the Ganges", "type": "resort", "cost_per_night": 5500, "location": "Tapovan", "rating": 4.4, "amenities": ["pool", "spa", "multi-cuisine restaurant", "river view", "yoga"], "tier": "comfort"},
    ],
    "Manali": [
        {"name": "Zostel Manali", "type": "hostel", "cost_per_night": 700, "location": "Old Manali", "rating": 4.1, "amenities": ["wifi", "common area", "cafe", "mountain view"], "tier": "budget"},
        {"name": "The Lazy Dog Lounge", "type": "hostel", "cost_per_night": 900, "location": "Old Manali", "rating": 4.3, "amenities": ["wifi", "cafe", "bonfire", "river view"], "tier": "budget"},
        {"name": "Hotel Manali Inn", "type": "hotel", "cost_per_night": 2200, "location": "Mall Road", "rating": 3.9, "amenities": ["wifi", "heater", "restaurant", "parking"], "tier": "mid"},
        {"name": "Johnson Lodge", "type": "hotel", "cost_per_night": 3500, "location": "Circuit House Road", "rating": 4.2, "amenities": ["wifi", "heater", "restaurant", "garden", "mountain view"], "tier": "mid"},
        {"name": "The Orchard Greens", "type": "resort", "cost_per_night": 5000, "location": "Log Huts", "rating": 4.3, "amenities": ["spa", "restaurant", "garden", "mountain view", "bonfire"], "tier": "comfort"},
    ],
    "McLeodganj": [
        {"name": "Triund Camps Hostel", "type": "hostel", "cost_per_night": 600, "location": "McLeodganj Market", "rating": 4.0, "amenities": ["wifi", "common room", "rooftop"], "tier": "budget"},
        {"name": "Hotel Tibet", "type": "hotel", "cost_per_night": 1500, "location": "Main Square", "rating": 3.8, "amenities": ["wifi", "restaurant", "mountain view"], "tier": "budget"},
        {"name": "Udechee Huts", "type": "homestay", "cost_per_night": 2800, "location": "Dharamkot", "rating": 4.4, "amenities": ["wifi", "home-cooked meals", "valley view", "garden"], "tier": "mid"},
        {"name": "The Birdcage Studio", "type": "hotel", "cost_per_night": 2200, "location": "Near Tsuglagkhang", "rating": 4.1, "amenities": ["wifi", "AC", "restaurant", "terrace"], "tier": "mid"},
        {"name": "Fortune Park Moksha", "type": "hotel", "cost_per_night": 4500, "location": "McLeodganj Road", "rating": 4.2, "amenities": ["pool", "spa", "restaurant", "mountain view"], "tier": "comfort"},
    ],
    "Jaipur": [
        {"name": "Zostel Jaipur", "type": "hostel", "cost_per_night": 700, "location": "C-Scheme", "rating": 4.2, "amenities": ["wifi", "common area", "cafe", "pool"], "tier": "budget"},
        {"name": "Hotel Pearl Palace", "type": "hotel", "cost_per_night": 1800, "location": "Hathroi Fort", "rating": 4.5, "amenities": ["wifi", "AC", "rooftop restaurant", "terrace"], "tier": "budget"},
        {"name": "Umaid Mahal Heritage Hotel", "type": "hotel", "cost_per_night": 3000, "location": "Bani Park", "rating": 4.2, "amenities": ["wifi", "AC", "heritage rooms", "restaurant", "pool"], "tier": "mid"},
        {"name": "Samode Haveli", "type": "heritage hotel", "cost_per_night": 6000, "location": "Gangapole", "rating": 4.6, "amenities": ["pool", "spa", "heritage dining", "courtyard", "garden"], "tier": "comfort"},
    ],
    "Mussoorie": [
        {"name": "Zostel Mussoorie", "type": "hostel", "cost_per_night": 800, "location": "Library End", "rating": 4.0, "amenities": ["wifi", "common room", "mountain view"], "tier": "budget"},
        {"name": "Hotel Padmini Nivas", "type": "hotel", "cost_per_night": 2500, "location": "The Mall", "rating": 4.1, "amenities": ["wifi", "heater", "restaurant", "valley view"], "tier": "mid"},
        {"name": "Rokeby Manor", "type": "boutique hotel", "cost_per_night": 4500, "location": "Landour", "rating": 4.5, "amenities": ["wifi", "restaurant", "garden", "colonial charm", "valley view"], "tier": "comfort"},
    ],
    "Jim Corbett": [
        {"name": "Camp Riverwild", "type": "camp", "cost_per_night": 2500, "location": "Marchula", "rating": 4.1, "amenities": ["tent", "meals included", "river view", "bonfire"], "tier": "budget"},
        {"name": "Corbett Machaan Resort", "type": "resort", "cost_per_night": 4000, "location": "Dhikuli", "rating": 4.0, "amenities": ["pool", "restaurant", "safari booking", "garden"], "tier": "mid"},
        {"name": "Jim's Jungle Retreat", "type": "resort", "cost_per_night": 6500, "location": "Dhela", "rating": 4.4, "amenities": ["pool", "spa", "nature walks", "multi-cuisine", "safari"], "tier": "comfort"},
    ],
    "Kasol": [
        {"name": "Kasol River Camp", "type": "camp", "cost_per_night": 600, "location": "Riverside", "rating": 4.0, "amenities": ["tent", "bonfire", "river access", "meals"], "tier": "budget"},
        {"name": "Parvati Woods Camp", "type": "camp", "cost_per_night": 1200, "location": "Near Bridge", "rating": 4.2, "amenities": ["wooden cottage", "meals", "mountain view", "bonfire"], "tier": "budget"},
        {"name": "The Hosteller Kasol", "type": "hostel", "cost_per_night": 800, "location": "Kasol Market", "rating": 4.1, "amenities": ["wifi", "cafe", "common area", "river view"], "tier": "budget"},
        {"name": "Alpine Guest House", "type": "guesthouse", "cost_per_night": 2000, "location": "Kasol Village", "rating": 4.0, "amenities": ["wifi", "home meals", "garden", "valley view"], "tier": "mid"},
    ],
    "Nainital": [
        {"name": "Zostel Nainital", "type": "hostel", "cost_per_night": 800, "location": "Mallital", "rating": 4.0, "amenities": ["wifi", "common room", "lake view"], "tier": "budget"},
        {"name": "Hotel Alka", "type": "hotel", "cost_per_night": 2200, "location": "The Mall", "rating": 3.9, "amenities": ["wifi", "lake view", "restaurant", "heater"], "tier": "mid"},
        {"name": "Manu Maharani", "type": "resort", "cost_per_night": 4500, "location": "Grasslands", "rating": 4.3, "amenities": ["pool", "spa", "restaurant", "mountain view", "garden"], "tier": "comfort"},
    ],
    "Bir Billing": [
        {"name": "Zostel Bir", "type": "hostel", "cost_per_night": 700, "location": "Bir Village", "rating": 4.2, "amenities": ["wifi", "cafe", "garden", "mountain view"], "tier": "budget"},
        {"name": "Colonel's Highland Retreat", "type": "guesthouse", "cost_per_night": 2000, "location": "Upper Bir", "rating": 4.3, "amenities": ["wifi", "garden", "home meals", "mountain view"], "tier": "mid"},
        {"name": "Bir Paradise Resort", "type": "resort", "cost_per_night": 3500, "location": "Bir", "rating": 4.1, "amenities": ["pool", "restaurant", "garden", "mountain view"], "tier": "comfort"},
    ],
    "Udaipur": [
        {"name": "Zostel Udaipur", "type": "hostel", "cost_per_night": 700, "location": "Chandpole", "rating": 4.2, "amenities": ["wifi", "rooftop", "lake view", "cafe"], "tier": "budget"},
        {"name": "Hotel Udai Niwas", "type": "hotel", "cost_per_night": 2000, "location": "Gangaur Ghat", "rating": 4.0, "amenities": ["wifi", "AC", "lake view", "restaurant"], "tier": "mid"},
        {"name": "Amet Haveli", "type": "heritage hotel", "cost_per_night": 4000, "location": "Lake Pichola", "rating": 4.4, "amenities": ["wifi", "lake-view dining", "heritage rooms", "terrace"], "tier": "mid"},
        {"name": "The Oberoi Udaivilas", "type": "luxury hotel", "cost_per_night": 25000, "location": "Lake Pichola", "rating": 4.9, "amenities": ["pool", "spa", "fine dining", "lake view", "butler service"], "tier": "luxury"},
    ],
}


class StaysTool(ToolBase):
    """Search for accommodation at a destination within budget."""

    name = "search_stays"
    description = "Find suitable accommodation options at a destination."

    def execute(
        self,
        destination: str = "Rishikesh",
        duration_days: int = 5,
        budget_per_night: float = 3000,
        travellers: int = 2,
    ) -> list[Accommodation]:
        if destination not in STAYS_DATABASE:
            return [
                Accommodation(
                    name=f"Estimated stay in {destination}",
                    type="hotel",
                    cost_per_night=budget_per_night,
                    location=destination,
                    rating=None,
                    evidence=Evidence(
                        source="Estimated",
                        source_type=SourceType.ESTIMATED,
                        confidence=0.3,
                        data=f"No accommodation data for {destination}. Estimated ₹{budget_per_night}/night.",
                    ),
                )
            ]

        stays = STAYS_DATABASE[destination]
        results = []

        for stay_data in stays:
            # Include stays within reasonable budget range
            if stay_data["cost_per_night"] <= budget_per_night * 1.3:
                acc = Accommodation(
                    name=stay_data["name"],
                    type=stay_data["type"],
                    cost_per_night=stay_data["cost_per_night"],
                    location=stay_data["location"],
                    rating=stay_data["rating"],
                    amenities=stay_data["amenities"],
                    evidence=Evidence(
                        source=f"ROAM curated stays — {destination}",
                        source_type=SourceType.CURATED,
                        confidence=0.8,
                        data=f"{stay_data['name']} ({stay_data['type']}) — ₹{stay_data['cost_per_night']}/night, {stay_data['location']}, rated {stay_data['rating']}/5",
                    ),
                )
                results.append(acc)

        # Sort by cost
        results.sort(key=lambda a: a.cost_per_night)
        return results
