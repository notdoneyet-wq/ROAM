"""
ROAM — Destination Search Tool
Searches for candidate travel destinations based on user constraints.
Uses curated, researched data for Indian destinations from Delhi.
"""

from __future__ import annotations

from schemas.models import CandidateDestination, Evidence, SourceType
from tools.base import ToolBase


# ── Curated destination database ────────────────────────────────────────
# All data is realistic and researched. Distances/times from Delhi.
# Scores are relative assessments based on each destination's strengths.

DESTINATION_DATABASE: dict[str, dict] = {
    "Rishikesh": {
        "state": "Uttarakhand",
        "travel_time_hours": 6.0,
        "travel_distance_km": 240,
        "travel_modes": ["bus", "train+taxi", "car"],
        "nature_score": 9.0,
        "food_score": 7.5,
        "relaxation_score": 8.5,
        "adventure_score": 9.0,
        "culture_score": 7.0,
        "weather_summer": "Warm, 25-35°C, pre-monsoon humidity",
        "weather_winter": "Cool, 10-20°C, clear skies",
        "weather_monsoon": "Heavy rain, river swells, some activities closed",
        "best_season": "Sep-Nov, Feb-May",
        "base_daily_cost": 1800,
        "description": "Adventure capital on the Ganges — rafting, yoga, trekking, waterfalls, and vibrant cafe culture.",
    },
    "Manali": {
        "state": "Himachal Pradesh",
        "travel_time_hours": 12.0,
        "travel_distance_km": 530,
        "travel_modes": ["bus", "car", "flight+taxi"],
        "nature_score": 9.5,
        "food_score": 7.0,
        "relaxation_score": 7.5,
        "adventure_score": 9.5,
        "culture_score": 6.5,
        "weather_summer": "Pleasant, 15-25°C, ideal",
        "weather_winter": "Cold, -5 to 10°C, snowfall",
        "weather_monsoon": "Rain, landslide risk on highways",
        "best_season": "Mar-Jun, Sep-Nov",
        "base_daily_cost": 2500,
        "description": "Himalayan hill station — snow peaks, Solang Valley, Old Manali cafes, Rohtang Pass.",
    },
    "McLeodganj": {
        "state": "Himachal Pradesh",
        "travel_time_hours": 10.0,
        "travel_distance_km": 480,
        "travel_modes": ["bus", "car", "flight+taxi"],
        "nature_score": 8.5,
        "food_score": 8.0,
        "relaxation_score": 9.0,
        "adventure_score": 7.0,
        "culture_score": 9.0,
        "weather_summer": "Pleasant, 18-28°C",
        "weather_winter": "Cold, 2-12°C, occasional snow",
        "weather_monsoon": "Heavy rain",
        "best_season": "Mar-Jun, Sep-Nov",
        "base_daily_cost": 1600,
        "description": "Little Lhasa — Tibetan culture, Triund trek, Bhagsu waterfall, momos and thukpa.",
    },
    "Jaipur": {
        "state": "Rajasthan",
        "travel_time_hours": 5.0,
        "travel_distance_km": 280,
        "travel_modes": ["bus", "train", "car"],
        "nature_score": 4.0,
        "food_score": 9.0,
        "relaxation_score": 6.5,
        "adventure_score": 4.0,
        "culture_score": 9.5,
        "weather_summer": "Very hot, 35-45°C",
        "weather_winter": "Pleasant, 10-25°C, ideal",
        "weather_monsoon": "Hot and humid, occasional rain",
        "best_season": "Oct-Mar",
        "base_daily_cost": 2200,
        "description": "Pink City — Amber Fort, Hawa Mahal, street food paradise, bazaars, Rajasthani thali.",
    },
    "Mussoorie": {
        "state": "Uttarakhand",
        "travel_time_hours": 6.5,
        "travel_distance_km": 280,
        "travel_modes": ["bus", "train+taxi", "car"],
        "nature_score": 8.0,
        "food_score": 6.5,
        "relaxation_score": 9.0,
        "adventure_score": 5.5,
        "culture_score": 6.0,
        "weather_summer": "Cool, 20-30°C",
        "weather_winter": "Cold, 2-12°C, occasional snow",
        "weather_monsoon": "Heavy rain, misty",
        "best_season": "Mar-Jun, Sep-Nov",
        "base_daily_cost": 2000,
        "description": "Queen of Hills — Mall Road, Kempty Falls, Lal Tibba, colonial charm, mountain views.",
    },
    "Jim Corbett": {
        "state": "Uttarakhand",
        "travel_time_hours": 5.5,
        "travel_distance_km": 260,
        "travel_modes": ["bus", "train", "car"],
        "nature_score": 9.5,
        "food_score": 5.5,
        "relaxation_score": 8.0,
        "adventure_score": 7.5,
        "culture_score": 4.0,
        "weather_summer": "Hot, 30-40°C",
        "weather_winter": "Cool, 5-20°C, ideal for safaris",
        "weather_monsoon": "Park closed (Jul-Sep)",
        "best_season": "Nov-Jun",
        "base_daily_cost": 2800,
        "description": "India's oldest national park — tiger safari, Ramganga river, dense forests, birding.",
    },
    "Kasol": {
        "state": "Himachal Pradesh",
        "travel_time_hours": 11.0,
        "travel_distance_km": 500,
        "travel_modes": ["bus", "car"],
        "nature_score": 9.0,
        "food_score": 7.5,
        "relaxation_score": 8.5,
        "adventure_score": 8.0,
        "culture_score": 6.0,
        "weather_summer": "Pleasant, 15-25°C",
        "weather_winter": "Cold, 0-10°C",
        "weather_monsoon": "Heavy rain, landslide risk",
        "best_season": "Mar-Jun, Sep-Nov",
        "base_daily_cost": 1500,
        "description": "Mini Israel of India — Parvati Valley, Kheerganga trek, riverside camps, Israeli cafes.",
    },
    "Nainital": {
        "state": "Uttarakhand",
        "travel_time_hours": 6.0,
        "travel_distance_km": 300,
        "travel_modes": ["bus", "train+taxi", "car"],
        "nature_score": 8.0,
        "food_score": 6.0,
        "relaxation_score": 8.5,
        "adventure_score": 5.0,
        "culture_score": 5.5,
        "weather_summer": "Cool, 15-27°C",
        "weather_winter": "Cold, 1-12°C",
        "weather_monsoon": "Rain, misty, scenic",
        "best_season": "Mar-Jun, Sep-Nov",
        "base_daily_cost": 2000,
        "description": "Lake District — Naini Lake boating, Snow View Point, Tiffin Top, colonial architecture.",
    },
    "Bir Billing": {
        "state": "Himachal Pradesh",
        "travel_time_hours": 10.5,
        "travel_distance_km": 470,
        "travel_modes": ["bus", "car", "flight+taxi"],
        "nature_score": 8.5,
        "food_score": 6.5,
        "relaxation_score": 7.5,
        "adventure_score": 9.5,
        "culture_score": 7.0,
        "weather_summer": "Pleasant, 18-28°C",
        "weather_winter": "Cold, 2-15°C",
        "weather_monsoon": "Rain, limited paragliding",
        "best_season": "Mar-Jun, Sep-Nov",
        "base_daily_cost": 1800,
        "description": "Paragliding capital of India — Tibetan monasteries, tea gardens, hiking trails.",
    },
    "Udaipur": {
        "state": "Rajasthan",
        "travel_time_hours": 10.0,
        "travel_distance_km": 660,
        "travel_modes": ["bus", "train", "flight", "car"],
        "nature_score": 5.5,
        "food_score": 8.5,
        "relaxation_score": 8.0,
        "adventure_score": 4.0,
        "culture_score": 9.5,
        "weather_summer": "Hot, 30-42°C",
        "weather_winter": "Pleasant, 10-28°C",
        "weather_monsoon": "Humid, lakes fill up, scenic",
        "best_season": "Sep-Mar",
        "base_daily_cost": 2500,
        "description": "City of Lakes — Lake Pichola, City Palace, sunset boat rides, Rajasthani cuisine.",
    },
}


class SearchDestinationsTool(ToolBase):
    """Search for candidate travel destinations matching user constraints."""

    name = "search_destinations"
    description = "Search for suitable travel destinations based on origin, interests, duration, and budget."

    def execute(
        self,
        origin: str = "Delhi",
        interests: list[str] | None = None,
        duration_days: int = 5,
        budget_inr: float = 50000,
        pace: str = "relaxed",
    ) -> list[CandidateDestination]:
        interests = interests or ["nature", "food"]
        candidates = []
        budget_per_day = budget_inr / max(duration_days, 1) / 2  # per person per day rough

        for name, data in DESTINATION_DATABASE.items():
            # Filter by travel feasibility: if trip is short, avoid very long travel
            if duration_days <= 3 and data["travel_time_hours"] > 8:
                continue
            if duration_days <= 5 and data["travel_time_hours"] > 12:
                continue

            # Score against interests
            interest_score = 0.0
            score_fields = {
                "nature": data["nature_score"],
                "food": data["food_score"],
                "relaxation": data["relaxation_score"],
                "adventure": data["adventure_score"],
                "culture": data["culture_score"],
                "relaxed": data["relaxation_score"],
            }
            for interest in interests:
                key = interest.lower().strip()
                if key in score_fields:
                    interest_score += score_fields[key]

            # Normalize interest score
            if interests:
                interest_score /= len(interests)

            # Travel time penalty (prefer closer destinations for short trips)
            travel_penalty = 0
            if data["travel_time_hours"] > 8:
                travel_penalty = 1.0
            elif data["travel_time_hours"] > 6:
                travel_penalty = 0.5

            # Budget fit (estimated daily cost vs available budget per day)
            cost_fit = 1.0
            if data["base_daily_cost"] > budget_per_day * 1.5:
                cost_fit = 0.5

            # Pace bonus
            pace_bonus = 0
            if pace in ("relaxed", "moderate"):
                pace_bonus = data["relaxation_score"] * 0.3
            elif pace in ("active", "adventure"):
                pace_bonus = data["adventure_score"] * 0.3

            overall = (interest_score * 0.5) + (pace_bonus * 0.2) + (cost_fit * 2) - travel_penalty

            candidate = CandidateDestination(
                name=name,
                state=data["state"],
                travel_time_hours=data["travel_time_hours"],
                travel_distance_km=data["travel_distance_km"],
                travel_modes=data["travel_modes"],
                estimated_total_cost=data["base_daily_cost"] * duration_days * 2,  # rough estimate for 2 people
                nature_score=data["nature_score"],
                food_score=data["food_score"],
                relaxation_score=data["relaxation_score"],
                adventure_score=data["adventure_score"],
                culture_score=data["culture_score"],
                weather_info=data.get("weather_summer", ""),
                best_season=data["best_season"],
                overall_score=round(overall, 2),
                evidence=[
                    Evidence(
                        source=f"ROAM curated database — {name}",
                        source_type=SourceType.CURATED,
                        confidence=0.85,
                        data=data["description"],
                    )
                ],
            )
            candidates.append(candidate)

        # Sort by overall score descending
        candidates.sort(key=lambda c: c.overall_score, reverse=True)
        return candidates
