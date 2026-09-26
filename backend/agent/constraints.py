"""
ROAM — Constraint Engine
Validates itineraries against constraints, detects changes, and checks feasibility.
"""

from __future__ import annotations

from schemas.models import (
    Constraint,
    ConstraintChange,
    ConstraintType,
    ExtractedConstraints,
    Itinerary,
    TravelPace,
)
from agent.intent import extract_constraints


class ConstraintEngine:
    """
    Manages travel constraints throughout the planning lifecycle.
    Validates plans, detects changes, and checks feasibility.
    """

    def validate_against_constraints(
        self,
        itinerary: Itinerary,
        constraints: ExtractedConstraints,
    ) -> tuple[list[str], list[str], list[str]]:
        """
        Validate an itinerary against constraints.
        Returns (issues, warnings, satisfied) — issues are hard constraint violations.
        """
        issues: list[str] = []
        warnings: list[str] = []
        satisfied: list[str] = []

        # Hard constraints
        if itinerary.budget.total > constraints.budget_inr:
            issues.append(
                f"Budget exceeded: ₹{itinerary.budget.total:,.0f} > ₹{constraints.budget_inr:,.0f}"
            )
        else:
            satisfied.append(f"Budget within limit: ₹{itinerary.budget.total:,.0f} ≤ ₹{constraints.budget_inr:,.0f}")

        if itinerary.duration_days != constraints.duration_days:
            issues.append(f"Duration mismatch: {itinerary.duration_days}d ≠ {constraints.duration_days}d")
        else:
            satisfied.append(f"Duration: {constraints.duration_days} days")

        if itinerary.travellers != constraints.travellers:
            issues.append(f"Traveller count mismatch: {itinerary.travellers} ≠ {constraints.travellers}")
        else:
            satisfied.append(f"Travellers: {constraints.travellers}")

        # Soft preferences (warnings only)
        for pref in constraints.soft_preferences:
            if pref.field == "interests":
                # Check if interest is reflected in activities
                interest = pref.value
                activity_categories = set()
                for day in itinerary.days:
                    for act in day.morning + day.afternoon + day.evening:
                        activity_categories.add(act.category)
                
                matched = any(
                    interest.lower() in cat or cat in interest.lower()
                    for cat in activity_categories
                )
                if matched:
                    satisfied.append(f"Interest '{interest}' covered")
                else:
                    warnings.append(f"Interest '{interest}' may not be well-represented")

        return issues, warnings, satisfied

    def detect_changes(
        self,
        old_constraints: ExtractedConstraints,
        new_message: str,
    ) -> tuple[ExtractedConstraints, list[ConstraintChange]]:
        """
        Detect what changed between old constraints and a new user message.
        Returns (updated_constraints, list_of_changes).
        """
        # Parse the new message for constraint updates
        new_partial = extract_constraints(new_message)
        changes: list[ConstraintChange] = []

        # Start from old constraints
        updated = old_constraints.model_copy(deep=True)

        # Check budget change
        if self._message_mentions_budget(new_message) and new_partial.budget_inr != old_constraints.budget_inr:
            changes.append(ConstraintChange(
                field="budget_inr",
                old_value=f"₹{old_constraints.budget_inr:,.0f}",
                new_value=f"₹{new_partial.budget_inr:,.0f}",
                impact="Budget change may require different accommodation, transport, or destination",
            ))
            updated.budget_inr = new_partial.budget_inr
            # Update hard constraints
            for hc in updated.hard_constraints:
                if hc.field == "budget_inr":
                    hc.value = new_partial.budget_inr
                    hc.description = f"Total budget must not exceed ₹{new_partial.budget_inr:,.0f}"

        # Check duration change
        if self._message_mentions_duration(new_message) and new_partial.duration_days != old_constraints.duration_days:
            changes.append(ConstraintChange(
                field="duration_days",
                old_value=f"{old_constraints.duration_days} days",
                new_value=f"{new_partial.duration_days} days",
                impact="Duration change affects itinerary depth and travel feasibility",
            ))
            updated.duration_days = new_partial.duration_days

        # Check pace change
        if self._message_mentions_pace(new_message) and new_partial.pace != old_constraints.pace:
            changes.append(ConstraintChange(
                field="pace",
                old_value=old_constraints.pace.value,
                new_value=new_partial.pace.value,
                impact="Pace change will adjust activity density and type",
            ))
            updated.pace = new_partial.pace

        # Check interest change
        new_interests = new_partial.interests
        if self._message_mentions_interests(new_message) and set(new_interests) != set(old_constraints.interests):
            changes.append(ConstraintChange(
                field="interests",
                old_value=", ".join(old_constraints.interests),
                new_value=", ".join(new_interests),
                impact="Interest change will modify recommended activities and possibly destination",
            ))
            updated.interests = new_interests

        # Check traveller change
        if self._message_mentions_travellers(new_message) and new_partial.travellers != old_constraints.travellers:
            changes.append(ConstraintChange(
                field="travellers",
                old_value=str(old_constraints.travellers),
                new_value=str(new_partial.travellers),
                impact="Traveller count affects total budget allocation",
            ))
            updated.travellers = new_partial.travellers

        return updated, changes

    def get_preserved_constraints(
        self,
        constraints: ExtractedConstraints,
        changes: list[ConstraintChange],
    ) -> list[str]:
        """List constraints that were NOT changed."""
        changed_fields = {c.field for c in changes}
        preserved = []

        if "duration_days" not in changed_fields:
            preserved.append(f"{constraints.duration_days} days")
        if "travellers" not in changed_fields:
            preserved.append(f"{constraints.travellers} traveller(s)")
        if "budget_inr" not in changed_fields:
            preserved.append(f"₹{constraints.budget_inr:,.0f} budget")
        if "pace" not in changed_fields:
            preserved.append(f"{constraints.pace.value} pace")
        if "interests" not in changed_fields:
            preserved.append(f"Interests: {', '.join(constraints.interests)}")

        return preserved

    def check_feasibility(
        self,
        constraints: ExtractedConstraints,
    ) -> tuple[bool, list[str]]:
        """
        Check if the constraints are feasible at all.
        Returns (is_feasible, list_of_issues).
        """
        issues = []

        # Budget sanity
        per_person_per_day = constraints.budget_inr / max(constraints.travellers, 1) / max(constraints.duration_days, 1)
        if per_person_per_day < 500:
            issues.append(
                f"Budget of ₹{constraints.budget_inr:,.0f} for {constraints.travellers} people over "
                f"{constraints.duration_days} days is very tight (₹{per_person_per_day:,.0f}/person/day). "
                f"This may not cover basic accommodation and food."
            )
        elif per_person_per_day < 1000:
            issues.append(
                f"Budget is tight at ₹{per_person_per_day:,.0f}/person/day. "
                f"Only budget hostels/camps and basic food will be feasible."
            )

        # Duration sanity
        if constraints.duration_days < 2:
            issues.append("A 1-day trip is very short for meaningful travel planning.")
        if constraints.duration_days > 14:
            issues.append("Very long trips may need multiple destination planning.")

        # Luxury + low budget conflict
        if constraints.travel_style == "luxury" and per_person_per_day < 5000:
            issues.append(
                "Luxury travel typically requires ₹5,000+/person/day. "
                "The current budget may not support luxury stays and experiences."
            )

        return len(issues) == 0, issues

    # ── Helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _message_mentions_budget(text: str) -> bool:
        import re
        return bool(re.search(r"(?:budget|₹|rs\.?|inr|spend|cost|afford|cheaper|expensive|money)", text, re.IGNORECASE))

    @staticmethod
    def _message_mentions_duration(text: str) -> bool:
        import re
        return bool(re.search(r"(?:\d+\s*day|duration|longer|shorter|extend|week)", text, re.IGNORECASE))

    @staticmethod
    def _message_mentions_pace(text: str) -> bool:
        import re
        return bool(re.search(r"(?:pace|relaxed|hectic|adventure|adventurous|active|slow|fast|chill|busy|packed)", text, re.IGNORECASE))

    @staticmethod
    def _message_mentions_interests(text: str) -> bool:
        import re
        return bool(re.search(r"(?:nature|food|culture|adventure|photography|nightlife|beach|mountain|wildlife|shopping)", text, re.IGNORECASE))

    @staticmethod
    def _message_mentions_travellers(text: str) -> bool:
        import re
        return bool(re.search(r"(?:\d+\s*people|\d+\s*person|travell|solo|couple|group)", text, re.IGNORECASE))
