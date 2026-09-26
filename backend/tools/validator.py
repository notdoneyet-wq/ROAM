"""
ROAM — Itinerary Validator Tool
Validates an itinerary against constraints for feasibility, timing, and budget.
"""

from __future__ import annotations

from schemas.models import (
    BudgetStatus,
    Evidence,
    ExtractedConstraints,
    Itinerary,
    SourceType,
)
from tools.base import ToolBase


class ValidatorTool(ToolBase):
    """Validate an itinerary against constraints."""

    name = "validate_itinerary"
    description = "Check itinerary for budget compliance, timing feasibility, and constraint violations."

    def execute(
        self,
        itinerary: Itinerary | None = None,
        constraints: ExtractedConstraints | None = None,
    ) -> dict:
        issues: list[str] = []
        warnings: list[str] = []
        satisfied: list[str] = []

        if itinerary is None or constraints is None:
            return {"valid": False, "issues": ["Missing itinerary or constraints"], "warnings": [], "satisfied": []}

        # ── Check duration ─────────────────────────────────────────
        if itinerary.duration_days != constraints.duration_days:
            issues.append(
                f"Duration mismatch: itinerary has {itinerary.duration_days} days but constraint requires {constraints.duration_days} days"
            )
        else:
            satisfied.append(f"Duration: {constraints.duration_days} days ✓")

        # ── Check travellers ────────────────────────────────────────
        if itinerary.travellers != constraints.travellers:
            issues.append(
                f"Traveller count mismatch: itinerary for {itinerary.travellers} but constraint requires {constraints.travellers}"
            )
        else:
            satisfied.append(f"Travellers: {constraints.travellers} ✓")

        # ── Check budget ────────────────────────────────────────────
        if itinerary.budget.total > constraints.budget_inr:
            issues.append(
                f"BUDGET EXCEEDED: ₹{itinerary.budget.total:,.0f} > ₹{constraints.budget_inr:,.0f} limit"
            )
        else:
            satisfied.append(f"Budget: ₹{itinerary.budget.total:,.0f} within ₹{constraints.budget_inr:,.0f} limit ✓")

        # ── Check days are populated ───────────────────────────────
        if len(itinerary.days) != constraints.duration_days:
            issues.append(
                f"Missing days: expected {constraints.duration_days} days, found {len(itinerary.days)}"
            )
        else:
            satisfied.append(f"All {constraints.duration_days} days planned ✓")

        # ── Check each day ──────────────────────────────────────────
        seen_activities: set[str] = set()
        total_daily_cost = 0

        for day in itinerary.days:
            # Check for empty days
            total_activities = len(day.morning) + len(day.afternoon) + len(day.evening)
            if total_activities == 0:
                warnings.append(f"Day {day.day_number}: No activities planned")

            # Check for duplicate activities
            for activity in day.morning + day.afternoon + day.evening:
                if activity.name in seen_activities:
                    warnings.append(f"Day {day.day_number}: Duplicate activity '{activity.name}'")
                seen_activities.add(activity.name)

            # Check daily activity hours vs pace
            total_hours = sum(a.duration_hours for a in day.morning + day.afternoon + day.evening)
            if constraints.pace.value == "relaxed" and total_hours > 8:
                warnings.append(
                    f"Day {day.day_number}: {total_hours:.1f}h of activities may be too much for a relaxed pace"
                )
            elif constraints.pace.value == "moderate" and total_hours > 10:
                warnings.append(
                    f"Day {day.day_number}: {total_hours:.1f}h of activities may be too much"
                )

            total_daily_cost += day.daily_cost

        # ── Check accommodation ────────────────────────────────────
        nights_with_stay = sum(1 for d in itinerary.days if d.accommodation is not None)
        needed_nights = constraints.duration_days - 1  # Last day may be travel back
        if nights_with_stay < needed_nights - 1:
            warnings.append(f"Only {nights_with_stay} nights with accommodation out of {needed_nights} needed")

        # ── Interest coverage ──────────────────────────────────────
        all_categories = set()
        for day in itinerary.days:
            for act in day.morning + day.afternoon + day.evening:
                all_categories.add(act.category)

        for interest in constraints.interests:
            interest_lower = interest.lower()
            matched = any(interest_lower in cat or cat in interest_lower for cat in all_categories)
            if matched:
                satisfied.append(f"Interest '{interest}' covered ✓")
            else:
                warnings.append(f"Interest '{interest}' may not be well-covered in activities")

        # ── Summary ────────────────────────────────────────────────
        valid = len(issues) == 0

        return {
            "valid": valid,
            "issues": issues,
            "warnings": warnings,
            "satisfied": satisfied,
            "evidence": Evidence(
                source="ROAM Itinerary Validator",
                source_type=SourceType.VERIFIED,
                confidence=0.95,
                data=f"Validation: {'PASS' if valid else 'FAIL'} — {len(issues)} issues, {len(warnings)} warnings, {len(satisfied)} constraints satisfied",
            ),
        }
