"""
ROAM — Intent & Constraint Extraction
Parses natural language travel requests into structured ExtractedConstraints.
No LLM required — uses keyword matching and pattern extraction.
"""

from __future__ import annotations

import re

from schemas.models import (
    Constraint,
    ConstraintType,
    ExtractedConstraints,
    TravelPace,
)


# ── Number extraction helpers ──────────────────────────────────────────

def _extract_number(text: str, patterns: list[str]) -> int | None:
    """Extract a number using regex patterns."""
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num_str = match.group(1).replace(",", "").replace(" ", "")
            try:
                return int(float(num_str))
            except ValueError:
                continue
    return None


def _extract_budget(text: str) -> float | None:
    """Extract budget amount from text, handling ₹, Rs, INR, K, lakh formats."""
    patterns = [
        r"(?:₹|rs\.?|inr)\s*([\d,]+)\s*(?:k|thousand)",  # ₹50K
        r"(?:₹|rs\.?|inr)\s*([\d,]+)\s*(?:lakh|lac)",     # ₹1 lakh
        r"(?:under|within|budget|max|maximum|upto|up to|below)\s*(?:of\s*)?(?:₹|rs\.?|inr)\s*([\d,]+)",  # under ₹50000
        r"(?:₹|rs\.?|inr)\s*([\d,]+)",                      # ₹50000
        r"([\d,]+)\s*(?:₹|rs\.?|inr|rupees?)",               # 50000 INR
        r"(?:budget|spend|cost)\s*(?:is\s*|of\s*)?(?:₹|rs\.?|inr)?\s*([\d,]+)",  # budget 50000
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num_str = match.group(1).replace(",", "").strip()
            try:
                value = float(num_str)
            except ValueError:
                continue
            
            # Handle K/thousand suffix
            if re.search(r"(k|thousand)", text[match.end():match.end()+20], re.IGNORECASE):
                value *= 1000
            # Handle lakh
            elif re.search(r"(lakh|lac)", text[match.end():match.end()+20], re.IGNORECASE):
                value *= 100000
            # Small numbers likely in thousands
            elif value < 500:
                value *= 1000
            
            return value
    return None


def _extract_duration(text: str) -> int | None:
    """Extract trip duration in days."""
    # Direct day patterns
    patterns = [
        r"(\d+)\s*(?:-\s*)?day",          # 5-day, 5 day
        r"(\d+)\s*(?:-\s*)?night",         # 3-night
        r"(\d+)d\b",                        # 5d
        r"for\s+(\d+)\s+days?",            # for 5 days
    ]
    
    val = _extract_number(text, patterns)
    if val and 1 <= val <= 30:
        return val
    
    # Word-based: "a week" → 7, "weekend" → 2-3
    if re.search(r"\bweekend\b", text, re.IGNORECASE):
        return 3
    if re.search(r"\ba\s+week\b", text, re.IGNORECASE):
        return 7
    if re.search(r"\btwo\s+weeks?\b", text, re.IGNORECASE):
        return 14
    
    return None


def _extract_travellers(text: str) -> int | None:
    """Extract number of travellers."""
    patterns = [
        r"(\d+)\s*(?:people|persons?|travell?ers?|adults?|friends?|pax)",
        r"for\s+(\d+)\s+(?:of us|people|persons?)",
        r"group\s+of\s+(\d+)",
    ]
    
    val = _extract_number(text, patterns)
    if val and 1 <= val <= 20:
        return val
    
    # Word-based
    word_nums = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "couple": 2, "solo": 1}
    for word, num in word_nums.items():
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            return num
    
    return None


def _extract_origin(text: str) -> str | None:
    """Extract origin city."""
    patterns = [
        r"from\s+(\w+(?:\s+\w+)?)",
        r"starting\s+(?:from\s+)?(\w+)",
        r"departing\s+(?:from\s+)?(\w+)",
        r"based\s+in\s+(\w+)",
    ]
    
    # Known Indian cities
    cities = {
        "delhi", "new delhi", "mumbai", "bangalore", "bengaluru", "chennai",
        "kolkata", "hyderabad", "pune", "ahmedabad", "jaipur", "lucknow",
        "chandigarh", "gurgaon", "gurugram", "noida", "ghaziabad",
    }
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            city = match.group(1).strip()
            # Verify it looks like a city
            if city.lower() in cities or len(city) > 2:
                return city.title()
    
    return None


def _extract_interests(text: str) -> list[str]:
    """Extract travel interests from text."""
    interest_keywords = {
        "nature": ["nature", "natural", "scenic", "greenery", "mountains", "hills", "forest", "wildlife", "outdoors", "lake", "river", "waterfall", "trek"],
        "food": ["food", "cuisine", "culinary", "eat", "restaurant", "street food", "local food", "foodie", "gastronomy", "cooking"],
        "adventure": ["adventure", "adventurous", "thrill", "extreme", "rafting", "trekking", "paragliding", "bungee", "camping", "hiking"],
        "culture": ["culture", "cultural", "heritage", "history", "historical", "temple", "monument", "museum", "art", "architecture"],
        "relaxation": ["relax", "relaxation", "peaceful", "calm", "serene", "spa", "wellness", "yoga", "meditation", "quiet"],
        "photography": ["photography", "photo", "photogenic", "instagram", "scenic views"],
        "nightlife": ["nightlife", "party", "bars", "clubs", "pub"],
        "shopping": ["shopping", "shop", "bazaar", "market", "handicraft"],
    }
    
    found = []
    text_lower = text.lower()
    for interest, keywords in interest_keywords.items():
        if any(kw in text_lower for kw in keywords):
            found.append(interest)
    
    return found if found else ["nature", "culture"]  # default


def _extract_pace(text: str) -> TravelPace:
    """Extract travel pace from text."""
    text_lower = text.lower()
    
    if any(w in text_lower for w in ["relaxed", "chill", "lazy", "slow", "easy", "peaceful", "calm", "no rush", "not hectic"]):
        return TravelPace.RELAXED
    if any(w in text_lower for w in ["adventure", "adventurous", "thrill", "extreme", "action", "adrenaline"]):
        return TravelPace.ADVENTURE
    if any(w in text_lower for w in ["active", "energetic", "packed", "full", "busy"]):
        return TravelPace.ACTIVE
    if any(w in text_lower for w in ["moderate", "balanced", "mix"]):
        return TravelPace.MODERATE
    
    return TravelPace.RELAXED  # default


def _extract_dietary(text: str) -> list[str]:
    """Extract dietary preferences."""
    prefs = []
    text_lower = text.lower()
    
    if any(w in text_lower for w in ["vegetarian", "veg only", "pure veg", "no meat", "no non-veg"]):
        prefs.append("veg")
    if any(w in text_lower for w in ["non-veg", "non veg", "meat", "chicken", "fish"]):
        prefs.append("non-veg")
    if any(w in text_lower for w in ["vegan"]):
        prefs.append("vegan")
    if any(w in text_lower for w in ["street food", "street-food"]):
        prefs.append("street-food")
    
    return prefs


def extract_constraints(user_message: str) -> ExtractedConstraints:
    """
    Parse a natural language travel request into structured constraints.
    Identifies hard constraints (budget, duration, travellers) and soft preferences (interests, pace).
    """
    text = user_message.strip()
    
    # Extract fields
    origin = _extract_origin(text) or "Delhi"
    travellers = _extract_travellers(text) or 2
    duration = _extract_duration(text) or 5
    budget = _extract_budget(text) or 50000
    interests = _extract_interests(text)
    pace = _extract_pace(text)
    dietary = _extract_dietary(text)
    
    # Check for destination hint
    destination = None
    dest_match = re.search(r"(?:to|visit|explore|go to|trip to)\s+(\w+(?:\s+\w+)?)", text, re.IGNORECASE)
    if dest_match:
        dest_candidate = dest_match.group(1).strip().title()
        # Only set if it's a specific destination (not a generic word)
        generic_words = {"Somewhere", "Place", "Destination", "Location", "Trip", "India"}
        if dest_candidate not in generic_words:
            destination = dest_candidate
    
    # Build hard constraints
    hard_constraints = [
        Constraint(type=ConstraintType.HARD, field="budget_inr", operator="<=", value=budget, description=f"Total budget must not exceed ₹{budget:,.0f}"),
        Constraint(type=ConstraintType.HARD, field="duration_days", operator="==", value=duration, description=f"Trip duration is {duration} days"),
        Constraint(type=ConstraintType.HARD, field="travellers", operator="==", value=travellers, description=f"Planning for {travellers} traveller(s)"),
    ]
    
    # Build soft preferences
    soft_preferences = []
    for interest in interests:
        soft_preferences.append(
            Constraint(type=ConstraintType.SOFT, field="interests", operator="contains", value=interest, description=f"Preference for {interest}")
        )
    soft_preferences.append(
        Constraint(type=ConstraintType.SOFT, field="pace", operator="==", value=pace.value, description=f"Preferred pace: {pace.value}")
    )
    
    # Check for additional notes
    notes = []
    if re.search(r"don'?t\s+(?:want|like|include)", text, re.IGNORECASE):
        avoid_match = re.search(r"don'?t\s+(?:want|like|include)\s+(.+?)(?:\.|,|$)", text, re.IGNORECASE)
        if avoid_match:
            notes.append(f"Avoid: {avoid_match.group(1).strip()}")
    
    if re.search(r"no\s+(?:early|late|long)", text, re.IGNORECASE):
        no_match = re.search(r"(no\s+(?:early|late|long)\s+\w+)", text, re.IGNORECASE)
        if no_match:
            notes.append(no_match.group(1).strip())
    
    # Detect early riser preference
    early_riser = None
    if re.search(r"(?:early\s+morning|sunrise|dawn|wake.+early)", text, re.IGNORECASE):
        early_riser = True
    elif re.search(r"(?:no\s+early|don'?t.+wake.+early|sleep\s+in|late\s+morning|before\s+[89])", text, re.IGNORECASE):
        early_riser = False
    
    # Travel style
    travel_style = "budget"
    if any(w in text.lower() for w in ["luxury", "premium", "5-star", "five star", "upscale"]):
        travel_style = "luxury"
    elif any(w in text.lower() for w in ["mid-range", "comfortable", "comfort", "mid range"]):
        travel_style = "comfort"
    elif any(w in text.lower() for w in ["backpack", "budget", "cheap", "affordable", "economical"]):
        travel_style = "budget"
    
    return ExtractedConstraints(
        origin=origin,
        destination=destination,
        travellers=travellers,
        duration_days=duration,
        budget_inr=budget,
        interests=interests,
        pace=pace,
        hard_constraints=hard_constraints,
        soft_preferences=soft_preferences,
        dietary_preferences=dietary,
        early_riser=early_riser,
        travel_style=travel_style,
        additional_notes=notes,
    )
