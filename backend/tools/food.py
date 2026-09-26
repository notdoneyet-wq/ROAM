"""
ROAM — Food Search Tool
Finds local food experiences, restaurants, and specialties at destinations.
"""

from __future__ import annotations

from schemas.models import Evidence, Meal, SourceType
from tools.base import ToolBase


# Curated food data by destination
FOOD_DATABASE: dict[str, dict] = {
    "Rishikesh": {
        "specialties": ["Aloo Puri", "Kachori", "Fresh fruit juices", "Israeli shakshuka", "Wood-fired pizza"],
        "local_cuisine": "Garhwali + International cafe culture (pure vegetarian city)",
        "restaurants": [
            {"name": "Little Buddha Cafe", "cuisine": "Continental/Israeli", "cost_pp": 350, "type": "cafe", "specialty": "Hummus platter, shakshuka", "dietary": ["veg"], "time": "lunch"},
            {"name": "Beatles Cafe", "cuisine": "Multi-cuisine", "cost_pp": 300, "type": "cafe", "specialty": "Wood-fired pizza, pasta", "dietary": ["veg"], "time": "dinner"},
            {"name": "Chotiwala Restaurant", "cuisine": "North Indian", "cost_pp": 200, "type": "restaurant", "specialty": "Thali, Aloo Puri", "dietary": ["veg"], "time": "lunch"},
            {"name": "Freedom Cafe", "cuisine": "Continental", "cost_pp": 250, "type": "cafe", "specialty": "Pancakes, smoothie bowls", "dietary": ["veg"], "time": "breakfast"},
            {"name": "Madras Cafe", "cuisine": "South Indian", "cost_pp": 150, "type": "restaurant", "specialty": "Dosa, Idli, Filter coffee", "dietary": ["veg"], "time": "breakfast"},
            {"name": "Street food at Laxman Jhula", "cuisine": "Street food", "cost_pp": 80, "type": "street", "specialty": "Aloo tikki, chaat, lassi", "dietary": ["veg", "street-food"], "time": "snack"},
        ],
        "note": "Rishikesh is a pure vegetarian city — no meat or alcohol served.",
    },
    "Manali": {
        "specialties": ["Siddu", "Trout fish", "Dham", "Momos", "Bun samosa"],
        "local_cuisine": "Himachali + Tibetan + International backpacker cafes",
        "restaurants": [
            {"name": "Drifters' Inn", "cuisine": "Continental", "cost_pp": 400, "type": "cafe", "specialty": "Pasta, steak, live music", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Lazy Dog Lounge", "cuisine": "Multi-cuisine", "cost_pp": 350, "type": "cafe", "specialty": "Trout, burgers, bonfire dining", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Johnson's Cafe", "cuisine": "European/Indian", "cost_pp": 450, "type": "restaurant", "specialty": "Trout, continental breakfast", "dietary": ["veg", "non-veg"], "time": "lunch"},
            {"name": "Chopsticks Restaurant", "cuisine": "Tibetan/Chinese", "cost_pp": 200, "type": "restaurant", "specialty": "Thukpa, momos, Tibetan bread", "dietary": ["veg", "non-veg"], "time": "lunch"},
            {"name": "Old Manali Street Food", "cuisine": "Street food", "cost_pp": 100, "type": "street", "specialty": "Momos, maggi, chai", "dietary": ["veg", "street-food"], "time": "snack"},
        ],
        "note": "Old Manali has a vibrant cafe culture. Fresh trout is a local specialty.",
    },
    "McLeodganj": {
        "specialties": ["Thukpa", "Momos", "Thenthuk", "Tibetan bread", "Butter tea"],
        "local_cuisine": "Tibetan + Himachali + International",
        "restaurants": [
            {"name": "Tibet Kitchen", "cuisine": "Tibetan", "cost_pp": 250, "type": "restaurant", "specialty": "Momos, thukpa, Tibetan set meal", "dietary": ["veg", "non-veg"], "time": "lunch"},
            {"name": "Illiterati Books & Coffee", "cuisine": "Cafe", "cost_pp": 350, "type": "cafe", "specialty": "Coffee, baked goods, valley view", "dietary": ["veg"], "time": "breakfast"},
            {"name": "Nick's Italian Kitchen", "cuisine": "Italian", "cost_pp": 400, "type": "restaurant", "specialty": "Wood-fired pizza, pasta", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Woeser Bakery", "cuisine": "Bakery/Cafe", "cost_pp": 150, "type": "cafe", "specialty": "Fresh bread, cinnamon rolls, coffee", "dietary": ["veg"], "time": "breakfast"},
            {"name": "McLeodganj Street Momos", "cuisine": "Street food", "cost_pp": 60, "type": "street", "specialty": "Steamed/fried momos, chowmein", "dietary": ["veg", "non-veg", "street-food"], "time": "snack"},
        ],
        "note": "Tibetan cuisine dominates. Many monastery-run eateries with authentic food.",
    },
    "Jaipur": {
        "specialties": ["Dal Baati Churma", "Laal Maas", "Ghevar", "Pyaaz Kachori", "Mirchi Bada"],
        "local_cuisine": "Rajasthani — rich, spiced, traditional",
        "restaurants": [
            {"name": "Laxmi Mishthan Bhandar (LMB)", "cuisine": "Rajasthani", "cost_pp": 350, "type": "restaurant", "specialty": "Rajasthani thali, ghevar, sweets", "dietary": ["veg"], "time": "lunch"},
            {"name": "Rawat Mishthan Bhandar", "cuisine": "Rajasthani", "cost_pp": 150, "type": "restaurant", "specialty": "Pyaaz kachori (legendary)", "dietary": ["veg", "street-food"], "time": "breakfast"},
            {"name": "1135 AD", "cuisine": "Royal Rajasthani", "cost_pp": 800, "type": "fine dining", "specialty": "Heritage dining inside Amber Fort", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Tapri Central", "cuisine": "Cafe", "cost_pp": 200, "type": "cafe", "specialty": "Chai varieties, snacks, sunset view", "dietary": ["veg"], "time": "snack"},
            {"name": "Johari Bazaar Street Food", "cuisine": "Street food", "cost_pp": 100, "type": "street", "specialty": "Mirchi bada, samosa, lassi, kulfi", "dietary": ["veg", "street-food"], "time": "snack"},
        ],
        "note": "Jaipur is a street food paradise. The kachori from Rawat is iconic.",
    },
    "Mussoorie": {
        "specialties": ["Maggi Point specials", "Landour bakehouse bread", "Tibetan momos"],
        "local_cuisine": "Hill station comfort food + Colonial bakery tradition",
        "restaurants": [
            {"name": "Landour Bakehouse", "cuisine": "Bakery/European", "cost_pp": 400, "type": "cafe", "specialty": "Fresh bread, cinnamon rolls, pasta", "dietary": ["veg"], "time": "breakfast"},
            {"name": "Char Dukan", "cuisine": "Cafe", "cost_pp": 200, "type": "cafe", "specialty": "Maggi, omelette, chai, view point", "dietary": ["veg", "non-veg"], "time": "snack"},
            {"name": "Lovely Omelette Centre", "cuisine": "Street food", "cost_pp": 100, "type": "street", "specialty": "20+ varieties of omelettes", "dietary": ["non-veg", "street-food"], "time": "breakfast"},
            {"name": "Kalsang Friends Corner", "cuisine": "Tibetan", "cost_pp": 200, "type": "restaurant", "specialty": "Momos, thukpa", "dietary": ["veg", "non-veg"], "time": "lunch"},
        ],
        "note": "Landour (upper Mussoorie) has Ruskin Bond-era charm and great bakeries.",
    },
    "Jim Corbett": {
        "specialties": ["Kumaoni raita", "Aloo ke gutke", "Bhatt ki churkani"],
        "local_cuisine": "Kumaoni + Resort dining",
        "restaurants": [
            {"name": "Resort restaurant (in-house)", "cuisine": "Multi-cuisine", "cost_pp": 500, "type": "restaurant", "specialty": "Buffet meals, bonfire dinner", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Dhaba near Ramnagar", "cuisine": "North Indian", "cost_pp": 150, "type": "dhaba", "specialty": "Dal, roti, sabzi, chicken curry", "dietary": ["veg", "non-veg"], "time": "lunch"},
        ],
        "note": "Limited dining options outside resorts. Most stays include meals.",
    },
    "Kasol": {
        "specialties": ["Israeli food", "Fresh trout", "Maggi", "Pancakes"],
        "local_cuisine": "Israeli + Himachali + Backpacker fusion",
        "restaurants": [
            {"name": "Evergreen Cafe", "cuisine": "Israeli/Continental", "cost_pp": 300, "type": "cafe", "specialty": "Falafel, shakshuka, river view", "dietary": ["veg"], "time": "lunch"},
            {"name": "Jim Morrison Cafe", "cuisine": "Multi-cuisine", "cost_pp": 250, "type": "cafe", "specialty": "Music, pancakes, pasta", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Moon Dance Cafe", "cuisine": "Israeli/Italian", "cost_pp": 300, "type": "cafe", "specialty": "Pizza, hummus, mountain view", "dietary": ["veg"], "time": "lunch"},
            {"name": "German Bakery Kasol", "cuisine": "Bakery", "cost_pp": 200, "type": "cafe", "specialty": "Fresh bread, cakes, coffee", "dietary": ["veg"], "time": "breakfast"},
        ],
        "note": "Kasol has a unique Israeli-influenced food scene in the Parvati Valley.",
    },
    "Nainital": {
        "specialties": ["Bal Mithai", "Singal", "Bhatt ki churkani"],
        "local_cuisine": "Kumaoni + North Indian + Lake-side cafes",
        "restaurants": [
            {"name": "Sakley's Restaurant", "cuisine": "Continental/Indian", "cost_pp": 350, "type": "restaurant", "specialty": "Pastries, continental food, lake view", "dietary": ["veg", "non-veg"], "time": "lunch"},
            {"name": "Sonam Momos Corner", "cuisine": "Tibetan", "cost_pp": 100, "type": "street", "specialty": "Steamed momos, thukpa", "dietary": ["veg", "non-veg", "street-food"], "time": "snack"},
            {"name": "Cafe Lakeview", "cuisine": "Multi-cuisine", "cost_pp": 250, "type": "cafe", "specialty": "Coffee, snacks, Naini Lake view", "dietary": ["veg"], "time": "snack"},
        ],
        "note": "Bal Mithai is the signature sweet of the Kumaon region — must try.",
    },
    "Bir Billing": {
        "specialties": ["Tibetan bread", "Momos", "Fresh juice"],
        "local_cuisine": "Tibetan + Himachali + Cafe culture",
        "restaurants": [
            {"name": "Vairagi Cafe", "cuisine": "Continental/Indian", "cost_pp": 300, "type": "cafe", "specialty": "Coffee, meals, tea garden view", "dietary": ["veg"], "time": "breakfast"},
            {"name": "Garden Cafe Bir", "cuisine": "Multi-cuisine", "cost_pp": 250, "type": "cafe", "specialty": "Wood-fired pizza, fresh juice", "dietary": ["veg", "non-veg"], "time": "lunch"},
            {"name": "Tibetan Kitchen Bir", "cuisine": "Tibetan", "cost_pp": 150, "type": "restaurant", "specialty": "Authentic momos, thenthuk", "dietary": ["veg", "non-veg"], "time": "dinner"},
        ],
        "note": "Bir has a growing cafe scene around the paragliding landing area.",
    },
    "Udaipur": {
        "specialties": ["Dal Baati Churma", "Gatte ki sabzi", "Malpua", "Kachori"],
        "local_cuisine": "Mewari Rajasthani — lighter than Jaipur",
        "restaurants": [
            {"name": "Ambrai Restaurant", "cuisine": "Rajasthani/Indian", "cost_pp": 600, "type": "restaurant", "specialty": "Lakeside dining, live music, thali", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Jagat Niwas Palace Rooftop", "cuisine": "Multi-cuisine", "cost_pp": 450, "type": "restaurant", "specialty": "Lake Palace view, Rajasthani food", "dietary": ["veg", "non-veg"], "time": "dinner"},
            {"name": "Natraj Dining Hall", "cuisine": "Rajasthani", "cost_pp": 200, "type": "restaurant", "specialty": "Traditional thali, unlimited", "dietary": ["veg"], "time": "lunch"},
            {"name": "Cafe Edelweiss", "cuisine": "German/European", "cost_pp": 350, "type": "cafe", "specialty": "Fresh baked goods, coffee", "dietary": ["veg"], "time": "breakfast"},
        ],
        "note": "Lakeside dining at sunset is Udaipur's signature experience.",
    },
}


class FoodTool(ToolBase):
    """Search for food experiences and restaurants at a destination."""

    name = "search_food"
    description = "Find food experiences, local specialties, and restaurants matching preferences."

    def execute(
        self,
        destination: str = "Rishikesh",
        preferences: list[str] | None = None,
        dietary: list[str] | None = None,
    ) -> dict:
        preferences = preferences or ["local", "street food"]
        dietary = dietary or []

        if destination not in FOOD_DATABASE:
            return {
                "destination": destination,
                "specialties": [],
                "restaurants": [],
                "note": f"No food data available for {destination}",
                "evidence": Evidence(
                    source="Estimated",
                    source_type=SourceType.ESTIMATED,
                    confidence=0.2,
                    data=f"No curated food data for {destination}",
                ),
            }

        food_data = FOOD_DATABASE[destination]
        restaurants = food_data["restaurants"]

        # Filter by dietary preferences if specified
        if dietary:
            filtered = []
            for r in restaurants:
                r_dietary = r.get("dietary", [])
                # Include if restaurant supports any of the user's dietary tags
                if any(d in r_dietary for d in dietary) or not dietary:
                    filtered.append(r)
            if filtered:
                restaurants = filtered

        meals = []
        for r in restaurants:
            meals.append(
                Meal(
                    name=r["name"],
                    cuisine=r["cuisine"],
                    cost_per_person=r["cost_pp"],
                    time_slot=r.get("time", "lunch"),
                    description=r["specialty"],
                    is_local_specialty=r["type"] in ("street", "dhaba"),
                    dietary_tags=r.get("dietary", []),
                    evidence=Evidence(
                        source=f"ROAM curated food — {destination}",
                        source_type=SourceType.CURATED,
                        confidence=0.8,
                        data=f"{r['name']} — {r['cuisine']}, ₹{r['cost_pp']}/person, known for {r['specialty']}",
                    ),
                )
            )

        return {
            "destination": destination,
            "local_cuisine": food_data["local_cuisine"],
            "specialties": food_data["specialties"],
            "restaurants": meals,
            "note": food_data.get("note", ""),
            "evidence": Evidence(
                source=f"ROAM curated food guide — {destination}",
                source_type=SourceType.CURATED,
                confidence=0.85,
                data=f"{destination} cuisine: {food_data['local_cuisine']}. Specialties: {', '.join(food_data['specialties'][:3])}",
            ),
        }
