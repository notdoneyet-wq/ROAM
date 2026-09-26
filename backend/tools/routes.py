"""
ROAM — Route / Distance Tool
Returns travel routes, distances, times, and modes from Delhi to destinations.
"""

from __future__ import annotations

from schemas.models import Evidence, SourceType
from tools.base import ToolBase


# Curated route data from Delhi to destinations
# Includes multiple transport modes with realistic costs and times
ROUTE_DATABASE: dict[str, dict] = {
    "Rishikesh": {
        "distance_km": 240,
        "modes": [
            {
                "mode": "Bus (Volvo AC)",
                "duration_hours": 6.0,
                "cost_per_person": 800,
                "frequency": "Every 30 min from ISBT Kashmere Gate",
                "comfort": "good",
            },
            {
                "mode": "Train (Shatabdi/Jan Shatabdi) to Haridwar + Taxi",
                "duration_hours": 5.5,
                "cost_per_person": 700,
                "frequency": "2-3 trains daily",
                "comfort": "good",
            },
            {
                "mode": "Private Car / Taxi",
                "duration_hours": 5.0,
                "cost_per_person": 2500,  # split between 2
                "frequency": "On demand",
                "comfort": "excellent",
            },
        ],
    },
    "Manali": {
        "distance_km": 530,
        "modes": [
            {
                "mode": "Volvo AC Bus (overnight)",
                "duration_hours": 12.0,
                "cost_per_person": 1200,
                "frequency": "Multiple departures evening",
                "comfort": "good",
            },
            {
                "mode": "Flight to Kullu + Taxi",
                "duration_hours": 3.0,
                "cost_per_person": 5000,
                "frequency": "1-2 flights daily",
                "comfort": "excellent",
            },
            {
                "mode": "Private Car",
                "duration_hours": 11.0,
                "cost_per_person": 4000,
                "frequency": "On demand",
                "comfort": "good",
            },
        ],
    },
    "McLeodganj": {
        "distance_km": 480,
        "modes": [
            {
                "mode": "Volvo AC Bus (overnight)",
                "duration_hours": 10.0,
                "cost_per_person": 1100,
                "frequency": "Evening departures",
                "comfort": "good",
            },
            {
                "mode": "Train to Pathankot + Bus/Taxi",
                "duration_hours": 11.0,
                "cost_per_person": 900,
                "frequency": "Several trains daily",
                "comfort": "moderate",
            },
            {
                "mode": "Flight to Gaggal + Taxi",
                "duration_hours": 2.5,
                "cost_per_person": 4500,
                "frequency": "1-2 flights daily",
                "comfort": "excellent",
            },
        ],
    },
    "Jaipur": {
        "distance_km": 280,
        "modes": [
            {
                "mode": "Train (Shatabdi/Ajmer Express)",
                "duration_hours": 4.5,
                "cost_per_person": 600,
                "frequency": "Multiple daily",
                "comfort": "good",
            },
            {
                "mode": "Volvo AC Bus",
                "duration_hours": 5.0,
                "cost_per_person": 700,
                "frequency": "Every hour",
                "comfort": "good",
            },
            {
                "mode": "Private Car",
                "duration_hours": 4.5,
                "cost_per_person": 2000,
                "frequency": "On demand",
                "comfort": "excellent",
            },
        ],
    },
    "Mussoorie": {
        "distance_km": 280,
        "modes": [
            {
                "mode": "Bus to Dehradun + Taxi/Bus",
                "duration_hours": 6.5,
                "cost_per_person": 850,
                "frequency": "Multiple daily",
                "comfort": "moderate",
            },
            {
                "mode": "Train to Dehradun + Taxi",
                "duration_hours": 6.0,
                "cost_per_person": 750,
                "frequency": "Shatabdi + Mussoorie Express",
                "comfort": "good",
            },
            {
                "mode": "Private Car",
                "duration_hours": 5.5,
                "cost_per_person": 2500,
                "frequency": "On demand",
                "comfort": "excellent",
            },
        ],
    },
    "Jim Corbett": {
        "distance_km": 260,
        "modes": [
            {
                "mode": "Train to Ramnagar",
                "duration_hours": 5.5,
                "cost_per_person": 500,
                "frequency": "2 trains daily",
                "comfort": "moderate",
            },
            {
                "mode": "Bus (Volvo)",
                "duration_hours": 6.0,
                "cost_per_person": 650,
                "frequency": "Several daily",
                "comfort": "good",
            },
            {
                "mode": "Private Car",
                "duration_hours": 5.0,
                "cost_per_person": 2200,
                "frequency": "On demand",
                "comfort": "excellent",
            },
        ],
    },
    "Kasol": {
        "distance_km": 500,
        "modes": [
            {
                "mode": "Bus (overnight to Bhuntar + local bus)",
                "duration_hours": 11.0,
                "cost_per_person": 1000,
                "frequency": "Evening departures",
                "comfort": "moderate",
            },
            {
                "mode": "Flight to Kullu + Taxi",
                "duration_hours": 3.5,
                "cost_per_person": 5500,
                "frequency": "1 flight daily",
                "comfort": "excellent",
            },
        ],
    },
    "Nainital": {
        "distance_km": 300,
        "modes": [
            {
                "mode": "Bus (Volvo AC)",
                "duration_hours": 6.0,
                "cost_per_person": 750,
                "frequency": "Multiple daily",
                "comfort": "good",
            },
            {
                "mode": "Train to Kathgodam + Taxi",
                "duration_hours": 6.5,
                "cost_per_person": 600,
                "frequency": "2-3 daily",
                "comfort": "moderate",
            },
            {
                "mode": "Private Car",
                "duration_hours": 5.5,
                "cost_per_person": 2500,
                "frequency": "On demand",
                "comfort": "excellent",
            },
        ],
    },
    "Bir Billing": {
        "distance_km": 470,
        "modes": [
            {
                "mode": "Bus (overnight to Baijnath + local)",
                "duration_hours": 10.5,
                "cost_per_person": 1000,
                "frequency": "Evening departures",
                "comfort": "moderate",
            },
            {
                "mode": "Flight to Gaggal + Taxi",
                "duration_hours": 3.0,
                "cost_per_person": 5000,
                "frequency": "1-2 daily",
                "comfort": "excellent",
            },
        ],
    },
    "Udaipur": {
        "distance_km": 660,
        "modes": [
            {
                "mode": "Train (Chetak Express / Mewar Express)",
                "duration_hours": 12.0,
                "cost_per_person": 900,
                "frequency": "Daily",
                "comfort": "moderate",
            },
            {
                "mode": "Flight",
                "duration_hours": 1.5,
                "cost_per_person": 4000,
                "frequency": "Multiple daily",
                "comfort": "excellent",
            },
            {
                "mode": "Volvo AC Bus",
                "duration_hours": 13.0,
                "cost_per_person": 1100,
                "frequency": "Evening departures",
                "comfort": "good",
            },
        ],
    },
}


class RouteTool(ToolBase):
    """Get route information between origin and destination."""

    name = "get_route"
    description = "Return distance, travel time, available modes, and cost from origin to destination."

    def execute(
        self,
        origin: str = "Delhi",
        destination: str = "Rishikesh",
        budget_preference: str = "budget",  # budget, comfort, fast
    ) -> dict:
        if destination not in ROUTE_DATABASE:
            return {
                "origin": origin,
                "destination": destination,
                "distance_km": 0,
                "modes": [],
                "recommended_mode": None,
                "error": f"No route data for {destination}",
                "evidence": Evidence(
                    source="Route lookup",
                    source_type=SourceType.ESTIMATED,
                    confidence=0.2,
                    data=f"No route data available for {origin} → {destination}",
                ),
            }

        route = ROUTE_DATABASE[destination]

        # Select recommended mode based on budget preference
        modes = route["modes"]
        if budget_preference == "budget":
            recommended = min(modes, key=lambda m: m["cost_per_person"])
        elif budget_preference == "fast":
            recommended = min(modes, key=lambda m: m["duration_hours"])
        else:  # comfort
            comfort_order = {"excellent": 0, "good": 1, "moderate": 2}
            recommended = min(modes, key=lambda m: comfort_order.get(m["comfort"], 3))

        return {
            "origin": origin,
            "destination": destination,
            "distance_km": route["distance_km"],
            "modes": modes,
            "recommended_mode": recommended,
            "evidence": Evidence(
                source=f"ROAM curated routes — {origin} → {destination}",
                source_type=SourceType.CURATED,
                confidence=0.85,
                data=f"{route['distance_km']}km via {recommended['mode']}, ~{recommended['duration_hours']}h, ₹{recommended['cost_per_person']}/person",
            ),
        }
