"""
ROAM — Budget Calculator Tool
Calculates complete trip budget with category breakdown and validation.
"""

from __future__ import annotations

from schemas.models import BudgetBreakdown, BudgetStatus, Evidence, SourceType
from tools.base import ToolBase


class BudgetTool(ToolBase):
    """Calculate and validate complete trip budget."""

    name = "calculate_budget"
    description = "Calculate trip budget with breakdown by category and validate against limit."

    def execute(
        self,
        transport_cost: float = 0,
        accommodation_cost: float = 0,
        food_cost: float = 0,
        activities_cost: float = 0,
        local_transport_cost: float = 0,
        travellers: int = 2,
        duration_days: int = 5,
        budget_limit: float = 50000,
        buffer_percent: float = 0.10,
    ) -> BudgetBreakdown:
        # Calculate subtotal before buffer
        subtotal = (
            transport_cost
            + accommodation_cost
            + food_cost
            + activities_cost
            + local_transport_cost
        )

        # Calculate buffer
        emergency_buffer = round(subtotal * buffer_percent, 0)

        # Miscellaneous (small % for tips, bottles, etc.)
        miscellaneous = round(subtotal * 0.03, 0)

        total = subtotal + emergency_buffer + miscellaneous

        # Determine status
        if total <= budget_limit * 0.95:
            status = BudgetStatus.UNDER_BUDGET
        elif total <= budget_limit:
            status = BudgetStatus.ON_BUDGET
        else:
            status = BudgetStatus.OVER_BUDGET

        return BudgetBreakdown(
            transport=transport_cost,
            accommodation=accommodation_cost,
            food=food_cost,
            activities=activities_cost,
            local_transport=local_transport_cost,
            emergency_buffer=emergency_buffer,
            miscellaneous=miscellaneous,
            total=total,
            budget_limit=budget_limit,
            status=status,
            per_person=round(total / max(travellers, 1), 0),
            savings=round(budget_limit - total, 0),
        )
