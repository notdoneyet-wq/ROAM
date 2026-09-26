"""
ROAM — Weather Tool
Returns realistic weather information for Indian destinations.
"""

from __future__ import annotations

from schemas.models import Evidence, SourceType
from tools.base import ToolBase


# Seasonal weather data for destinations (curated, realistic)
WEATHER_DATA: dict[str, dict[str, dict]] = {
    "Rishikesh": {
        "jan": {"temp_min": 7, "temp_max": 20, "condition": "Cool and clear", "suitable": True},
        "feb": {"temp_min": 10, "temp_max": 23, "condition": "Pleasant, warming up", "suitable": True},
        "mar": {"temp_min": 14, "temp_max": 28, "condition": "Warm, dry", "suitable": True},
        "apr": {"temp_min": 18, "temp_max": 33, "condition": "Hot, dry", "suitable": True},
        "may": {"temp_min": 22, "temp_max": 37, "condition": "Hot", "suitable": True},
        "jun": {"temp_min": 24, "temp_max": 36, "condition": "Hot, pre-monsoon", "suitable": False},
        "jul": {"temp_min": 24, "temp_max": 33, "condition": "Monsoon, heavy rain", "suitable": False},
        "aug": {"temp_min": 23, "temp_max": 32, "condition": "Monsoon, rain", "suitable": False},
        "sep": {"temp_min": 21, "temp_max": 31, "condition": "Post-monsoon, clearing", "suitable": True},
        "oct": {"temp_min": 16, "temp_max": 29, "condition": "Pleasant, clear", "suitable": True},
        "nov": {"temp_min": 10, "temp_max": 25, "condition": "Cool, dry", "suitable": True},
        "dec": {"temp_min": 6, "temp_max": 20, "condition": "Cold, clear", "suitable": True},
    },
    "Manali": {
        "jan": {"temp_min": -3, "temp_max": 8, "condition": "Cold, snowfall", "suitable": True},
        "feb": {"temp_min": -2, "temp_max": 10, "condition": "Cold, snow", "suitable": True},
        "mar": {"temp_min": 2, "temp_max": 15, "condition": "Cold, snow melting", "suitable": True},
        "apr": {"temp_min": 6, "temp_max": 20, "condition": "Cool, pleasant", "suitable": True},
        "may": {"temp_min": 10, "temp_max": 25, "condition": "Pleasant, ideal", "suitable": True},
        "jun": {"temp_min": 13, "temp_max": 27, "condition": "Warm, pre-monsoon", "suitable": True},
        "jul": {"temp_min": 15, "temp_max": 25, "condition": "Monsoon, rain", "suitable": False},
        "aug": {"temp_min": 14, "temp_max": 24, "condition": "Monsoon, rain", "suitable": False},
        "sep": {"temp_min": 11, "temp_max": 22, "condition": "Post-monsoon", "suitable": True},
        "oct": {"temp_min": 5, "temp_max": 18, "condition": "Cool, clear, autumn colors", "suitable": True},
        "nov": {"temp_min": 0, "temp_max": 13, "condition": "Cold, dry", "suitable": True},
        "dec": {"temp_min": -4, "temp_max": 7, "condition": "Very cold, snowfall", "suitable": True},
    },
    "McLeodganj": {
        "jan": {"temp_min": 1, "temp_max": 10, "condition": "Cold, occasional snow", "suitable": True},
        "feb": {"temp_min": 3, "temp_max": 12, "condition": "Cold, clear", "suitable": True},
        "mar": {"temp_min": 7, "temp_max": 17, "condition": "Cool, pleasant", "suitable": True},
        "apr": {"temp_min": 11, "temp_max": 22, "condition": "Pleasant", "suitable": True},
        "may": {"temp_min": 15, "temp_max": 27, "condition": "Warm, ideal", "suitable": True},
        "jun": {"temp_min": 18, "temp_max": 28, "condition": "Warm, pre-monsoon", "suitable": True},
        "jul": {"temp_min": 18, "temp_max": 25, "condition": "Heavy monsoon rain", "suitable": False},
        "aug": {"temp_min": 17, "temp_max": 24, "condition": "Monsoon", "suitable": False},
        "sep": {"temp_min": 14, "temp_max": 23, "condition": "Clearing, pleasant", "suitable": True},
        "oct": {"temp_min": 9, "temp_max": 20, "condition": "Cool, clear", "suitable": True},
        "nov": {"temp_min": 4, "temp_max": 15, "condition": "Cold, dry", "suitable": True},
        "dec": {"temp_min": 1, "temp_max": 10, "condition": "Cold", "suitable": True},
    },
    "Jaipur": {
        "jan": {"temp_min": 8, "temp_max": 22, "condition": "Cool, dry, pleasant", "suitable": True},
        "feb": {"temp_min": 11, "temp_max": 25, "condition": "Warming, pleasant", "suitable": True},
        "mar": {"temp_min": 17, "temp_max": 32, "condition": "Warm", "suitable": True},
        "apr": {"temp_min": 22, "temp_max": 38, "condition": "Hot", "suitable": False},
        "may": {"temp_min": 27, "temp_max": 42, "condition": "Very hot", "suitable": False},
        "jun": {"temp_min": 28, "temp_max": 41, "condition": "Very hot, pre-monsoon", "suitable": False},
        "jul": {"temp_min": 26, "temp_max": 35, "condition": "Monsoon, humid", "suitable": False},
        "aug": {"temp_min": 25, "temp_max": 33, "condition": "Monsoon", "suitable": False},
        "sep": {"temp_min": 23, "temp_max": 34, "condition": "Post-monsoon, humid", "suitable": False},
        "oct": {"temp_min": 18, "temp_max": 33, "condition": "Warm, clearing", "suitable": True},
        "nov": {"temp_min": 12, "temp_max": 28, "condition": "Pleasant, ideal", "suitable": True},
        "dec": {"temp_min": 8, "temp_max": 23, "condition": "Cool, pleasant", "suitable": True},
    },
    "Mussoorie": {
        "jan": {"temp_min": 1, "temp_max": 10, "condition": "Cold, occasional snow", "suitable": True},
        "feb": {"temp_min": 2, "temp_max": 12, "condition": "Cold, clear", "suitable": True},
        "mar": {"temp_min": 6, "temp_max": 17, "condition": "Cool, pleasant", "suitable": True},
        "apr": {"temp_min": 10, "temp_max": 22, "condition": "Pleasant", "suitable": True},
        "may": {"temp_min": 14, "temp_max": 27, "condition": "Warm, ideal", "suitable": True},
        "jun": {"temp_min": 17, "temp_max": 27, "condition": "Warm, pre-monsoon", "suitable": True},
        "jul": {"temp_min": 17, "temp_max": 23, "condition": "Heavy rain", "suitable": False},
        "aug": {"temp_min": 16, "temp_max": 22, "condition": "Rain, misty", "suitable": False},
        "sep": {"temp_min": 13, "temp_max": 22, "condition": "Clearing", "suitable": True},
        "oct": {"temp_min": 8, "temp_max": 19, "condition": "Cool, clear", "suitable": True},
        "nov": {"temp_min": 4, "temp_max": 14, "condition": "Cold, dry", "suitable": True},
        "dec": {"temp_min": 1, "temp_max": 10, "condition": "Cold", "suitable": True},
    },
    "Jim Corbett": {
        "jan": {"temp_min": 5, "temp_max": 18, "condition": "Cool, clear, safari season", "suitable": True},
        "feb": {"temp_min": 8, "temp_max": 22, "condition": "Cool, ideal for safaris", "suitable": True},
        "mar": {"temp_min": 13, "temp_max": 28, "condition": "Warm, safari season", "suitable": True},
        "apr": {"temp_min": 18, "temp_max": 34, "condition": "Hot, last safari month", "suitable": True},
        "may": {"temp_min": 22, "temp_max": 38, "condition": "Hot", "suitable": True},
        "jun": {"temp_min": 24, "temp_max": 38, "condition": "Hot, park closing", "suitable": False},
        "jul": {"temp_min": 24, "temp_max": 33, "condition": "Park closed, monsoon", "suitable": False},
        "aug": {"temp_min": 23, "temp_max": 32, "condition": "Park closed", "suitable": False},
        "sep": {"temp_min": 21, "temp_max": 31, "condition": "Park closed", "suitable": False},
        "oct": {"temp_min": 15, "temp_max": 29, "condition": "Park reopening", "suitable": True},
        "nov": {"temp_min": 8, "temp_max": 24, "condition": "Cool, safari season", "suitable": True},
        "dec": {"temp_min": 4, "temp_max": 19, "condition": "Cool, clear", "suitable": True},
    },
    "Kasol": {
        "jan": {"temp_min": -2, "temp_max": 8, "condition": "Cold, possible snow", "suitable": True},
        "feb": {"temp_min": 0, "temp_max": 10, "condition": "Cold, clearing", "suitable": True},
        "mar": {"temp_min": 4, "temp_max": 15, "condition": "Cool, pleasant", "suitable": True},
        "apr": {"temp_min": 8, "temp_max": 20, "condition": "Pleasant", "suitable": True},
        "may": {"temp_min": 12, "temp_max": 25, "condition": "Warm, ideal", "suitable": True},
        "jun": {"temp_min": 15, "temp_max": 27, "condition": "Warm, pre-monsoon", "suitable": True},
        "jul": {"temp_min": 16, "temp_max": 24, "condition": "Heavy rain, landslide risk", "suitable": False},
        "aug": {"temp_min": 15, "temp_max": 23, "condition": "Rain", "suitable": False},
        "sep": {"temp_min": 12, "temp_max": 22, "condition": "Clearing", "suitable": True},
        "oct": {"temp_min": 7, "temp_max": 18, "condition": "Cool, autumn colors", "suitable": True},
        "nov": {"temp_min": 2, "temp_max": 13, "condition": "Cold, clear", "suitable": True},
        "dec": {"temp_min": -2, "temp_max": 8, "condition": "Very cold", "suitable": True},
    },
    "Nainital": {
        "jan": {"temp_min": 1, "temp_max": 10, "condition": "Cold, clear", "suitable": True},
        "feb": {"temp_min": 3, "temp_max": 12, "condition": "Cold, pleasant", "suitable": True},
        "mar": {"temp_min": 7, "temp_max": 17, "condition": "Cool", "suitable": True},
        "apr": {"temp_min": 11, "temp_max": 22, "condition": "Pleasant", "suitable": True},
        "may": {"temp_min": 14, "temp_max": 25, "condition": "Warm, ideal", "suitable": True},
        "jun": {"temp_min": 16, "temp_max": 25, "condition": "Warm, pre-monsoon", "suitable": True},
        "jul": {"temp_min": 16, "temp_max": 22, "condition": "Monsoon", "suitable": False},
        "aug": {"temp_min": 16, "temp_max": 21, "condition": "Rain, misty", "suitable": False},
        "sep": {"temp_min": 13, "temp_max": 21, "condition": "Clearing", "suitable": True},
        "oct": {"temp_min": 8, "temp_max": 19, "condition": "Cool, pleasant", "suitable": True},
        "nov": {"temp_min": 4, "temp_max": 14, "condition": "Cool, dry", "suitable": True},
        "dec": {"temp_min": 1, "temp_max": 10, "condition": "Cold", "suitable": True},
    },
    "Bir Billing": {
        "jan": {"temp_min": 0, "temp_max": 12, "condition": "Cold, clear", "suitable": True},
        "feb": {"temp_min": 2, "temp_max": 14, "condition": "Cold, warming", "suitable": True},
        "mar": {"temp_min": 6, "temp_max": 19, "condition": "Pleasant", "suitable": True},
        "apr": {"temp_min": 10, "temp_max": 24, "condition": "Warm, paragliding season", "suitable": True},
        "may": {"temp_min": 14, "temp_max": 28, "condition": "Warm, ideal", "suitable": True},
        "jun": {"temp_min": 17, "temp_max": 28, "condition": "Warm, pre-monsoon", "suitable": True},
        "jul": {"temp_min": 17, "temp_max": 25, "condition": "Rain, limited flying", "suitable": False},
        "aug": {"temp_min": 16, "temp_max": 24, "condition": "Monsoon", "suitable": False},
        "sep": {"temp_min": 13, "temp_max": 23, "condition": "Clearing, flying resumes", "suitable": True},
        "oct": {"temp_min": 8, "temp_max": 20, "condition": "Cool, ideal", "suitable": True},
        "nov": {"temp_min": 3, "temp_max": 15, "condition": "Cold, clear", "suitable": True},
        "dec": {"temp_min": 0, "temp_max": 11, "condition": "Cold", "suitable": True},
    },
    "Udaipur": {
        "jan": {"temp_min": 9, "temp_max": 24, "condition": "Cool, pleasant", "suitable": True},
        "feb": {"temp_min": 12, "temp_max": 27, "condition": "Warming, pleasant", "suitable": True},
        "mar": {"temp_min": 17, "temp_max": 33, "condition": "Warm", "suitable": True},
        "apr": {"temp_min": 22, "temp_max": 38, "condition": "Hot", "suitable": False},
        "may": {"temp_min": 26, "temp_max": 41, "condition": "Very hot", "suitable": False},
        "jun": {"temp_min": 27, "temp_max": 39, "condition": "Hot, pre-monsoon", "suitable": False},
        "jul": {"temp_min": 25, "temp_max": 33, "condition": "Monsoon, lakes filling", "suitable": False},
        "aug": {"temp_min": 24, "temp_max": 31, "condition": "Monsoon, green", "suitable": False},
        "sep": {"temp_min": 22, "temp_max": 32, "condition": "Post-monsoon", "suitable": True},
        "oct": {"temp_min": 18, "temp_max": 33, "condition": "Warm, clearing", "suitable": True},
        "nov": {"temp_min": 13, "temp_max": 29, "condition": "Pleasant", "suitable": True},
        "dec": {"temp_min": 9, "temp_max": 24, "condition": "Cool, ideal", "suitable": True},
    },
}

MONTH_NAMES = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]


class WeatherTool(ToolBase):
    """Get weather information for a destination and month."""

    name = "get_weather"
    description = "Retrieve weather conditions for a destination during a specific month."

    def execute(
        self,
        destination: str = "Rishikesh",
        month: int = 10,  # 1-12
    ) -> dict:
        month_key = MONTH_NAMES[max(0, min(11, month - 1))]

        if destination not in WEATHER_DATA:
            # Fallback for unknown destinations
            return {
                "destination": destination,
                "month": month_key,
                "temp_min": 15,
                "temp_max": 30,
                "condition": "Data unavailable — estimated moderate climate",
                "suitable": True,
                "evidence": Evidence(
                    source="Estimated weather",
                    source_type=SourceType.ESTIMATED,
                    confidence=0.3,
                    data=f"No weather data available for {destination}",
                ),
            }

        weather = WEATHER_DATA[destination][month_key]
        return {
            "destination": destination,
            "month": month_key,
            "temp_min": weather["temp_min"],
            "temp_max": weather["temp_max"],
            "condition": weather["condition"],
            "suitable": weather["suitable"],
            "evidence": Evidence(
                source=f"ROAM curated weather — {destination}",
                source_type=SourceType.CURATED,
                confidence=0.8,
                data=f"{destination} in {month_key.title()}: {weather['condition']}, {weather['temp_min']}–{weather['temp_max']}°C",
            ),
        }
