"""
ROAM — Travel Planner Orchestrator
The core agent that coordinates tools, compares destinations, builds itineraries,
and handles re-planning. Deterministic for demo reliability.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime

from schemas.models import (
    Accommodation,
    Activity,
    BudgetBreakdown,
    CandidateDestination,
    ConstraintChange,
    DayPlan,
    Evidence,
    ExtractedConstraints,
    Itinerary,
    Meal,
    PlanResponse,
    PlanningStep,
    ReplanResponse,
    ReplanResult,
    SourceType,
    StepStatus,
    ToolCall,
    TravelPace,
)
from agent.constraints import ConstraintEngine
from tools.search import SearchDestinationsTool
from tools.weather import WeatherTool
from tools.routes import RouteTool
from tools.stays import StaysTool
from tools.food import FoodTool
from tools.activities import ActivitiesTool
from tools.budget import BudgetTool
from tools.validator import ValidatorTool


class TravelPlanner:
    """
    Orchestrates the full travel planning pipeline:
    1. Search candidate destinations
    2. Check weather
    3. Get routes and distances
    4. Score and rank candidates
    5. Select best destination
    6. Find stays, food, activities
    7. Build day-by-day itinerary
    8. Calculate budget
    9. Validate
    """

    def __init__(self) -> None:
        self.search_tool = SearchDestinationsTool()
        self.weather_tool = WeatherTool()
        self.route_tool = RouteTool()
        self.stays_tool = StaysTool()
        self.food_tool = FoodTool()
        self.activities_tool = ActivitiesTool()
        self.budget_tool = BudgetTool()
        self.validator_tool = ValidatorTool()
        self.constraint_engine = ConstraintEngine()

    def plan_trip(self, constraints: ExtractedConstraints) -> PlanResponse:
        """Execute the full planning pipeline."""
        session_id = str(uuid.uuid4())[:8]
        all_tool_calls: list[ToolCall] = []
        planning_steps: list[PlanningStep] = []
        all_evidence: list[Evidence] = []

        # ── Step 1: Check feasibility ──────────────────────────────
        step1 = PlanningStep(step="feasibility_check", label="Checking feasibility", status=StepStatus.RUNNING)
        planning_steps.append(step1)
        
        is_feasible, feasibility_issues = self.constraint_engine.check_feasibility(constraints)
        step1.status = StepStatus.COMPLETE
        step1.detail = "Feasible" if is_feasible else f"Potential issues: {'; '.join(feasibility_issues)}"

        # ── Step 2: Search destinations ────────────────────────────
        step2 = PlanningStep(step="search_destinations", label="Searching destinations", status=StepStatus.RUNNING)
        planning_steps.append(step2)

        candidates, tc = self.search_tool.run(
            origin=constraints.origin,
            interests=constraints.interests,
            duration_days=constraints.duration_days,
            budget_inr=constraints.budget_inr,
            pace=constraints.pace.value,
        )
        all_tool_calls.append(tc)

        if not candidates:
            step2.status = StepStatus.ERROR
            step2.detail = "No destinations found"
            return PlanResponse(
                session_id=session_id,
                constraints=constraints,
                candidates=[],
                planning_steps=planning_steps,
                tool_calls=all_tool_calls,
                error="Could not find any suitable destinations for your requirements.",
            )

        step2.status = StepStatus.COMPLETE
        step2.detail = f"Found {len(candidates)} candidate destinations"
        step2.tool_calls = [tc]

        # ── Step 3: Check weather for top candidates ───────────────
        step3 = PlanningStep(step="check_weather", label="Checking weather conditions", status=StepStatus.RUNNING)
        planning_steps.append(step3)

        current_month = datetime.now().month
        top_candidates = candidates[:5]  # Check weather for top 5

        for candidate in top_candidates:
            weather_result, tc = self.weather_tool.run(
                destination=candidate.name,
                month=current_month,
            )
            all_tool_calls.append(tc)
            if weather_result:
                candidate.weather_info = weather_result.get("condition", "")
                candidate.weather_temp_c = weather_result.get("temp_max")
                if weather_result.get("evidence"):
                    all_evidence.append(weather_result["evidence"])
                # Penalize if weather is not suitable
                if not weather_result.get("suitable", True):
                    candidate.overall_score -= 2.0

        step3.status = StepStatus.COMPLETE
        step3.detail = f"Checked weather for {len(top_candidates)} destinations"

        # ── Step 4: Get routes for top candidates ──────────────────
        step4 = PlanningStep(step="check_routes", label="Calculating travel routes", status=StepStatus.RUNNING)
        planning_steps.append(step4)

        budget_pref = "budget" if constraints.travel_style == "budget" else "comfort"
        for candidate in top_candidates:
            route_result, tc = self.route_tool.run(
                origin=constraints.origin,
                destination=candidate.name,
                budget_preference=budget_pref,
            )
            all_tool_calls.append(tc)
            if route_result and route_result.get("recommended_mode"):
                rec = route_result["recommended_mode"]
                candidate.travel_time_hours = rec["duration_hours"]
                candidate.travel_distance_km = route_result["distance_km"]
                if route_result.get("evidence"):
                    all_evidence.append(route_result["evidence"])

        step4.status = StepStatus.COMPLETE
        step4.detail = f"Routes calculated for {len(top_candidates)} destinations"

        # ── Step 5: Score and select best destination ──────────────
        step5 = PlanningStep(step="compare_destinations", label="Comparing destinations", status=StepStatus.RUNNING)
        planning_steps.append(step5)

        # Re-sort after weather and route updates
        top_candidates.sort(key=lambda c: c.overall_score, reverse=True)

        # Select the best
        selected = top_candidates[0]
        selected.selected = True
        selected.selection_reason = self._generate_selection_reason(selected, constraints)

        # Mark others as not selected
        for candidate in top_candidates[1:]:
            candidate.selected = False
            candidate.rejected_reason = self._generate_rejection_reason(candidate, selected, constraints)

        step5.status = StepStatus.COMPLETE
        step5.detail = f"Selected: {selected.name}, {selected.state}"

        # ── Step 6: Find stays ─────────────────────────────────────
        step6 = PlanningStep(step="search_stays", label="Comparing accommodation", status=StepStatus.RUNNING)
        planning_steps.append(step6)

        # Calculate budget for accommodation
        nights = constraints.duration_days - 1  # Typically
        # Get transport cost first to know remaining budget
        route_data, _ = self.route_tool.run(origin=constraints.origin, destination=selected.name, budget_preference=budget_pref)
        transport_pp = route_data["recommended_mode"]["cost_per_person"] if route_data and route_data.get("recommended_mode") else 800
        transport_total = transport_pp * constraints.travellers * 2  # round trip

        remaining_budget = constraints.budget_inr - transport_total
        budget_per_night = remaining_budget * 0.35 / max(nights, 1)  # ~35% for accommodation

        stays_result, tc = self.stays_tool.run(
            destination=selected.name,
            duration_days=constraints.duration_days,
            budget_per_night=budget_per_night,
            travellers=constraints.travellers,
        )
        all_tool_calls.append(tc)

        # Pick the best stay within budget
        chosen_stay = None
        if stays_result:
            for stay in stays_result:
                if stay.cost_per_night * nights <= remaining_budget * 0.4:
                    chosen_stay = stay
                    break
            if not chosen_stay:
                chosen_stay = stays_result[0]  # cheapest

        step6.status = StepStatus.COMPLETE
        step6.detail = f"Found {len(stays_result) if stays_result else 0} options, selected {chosen_stay.name if chosen_stay else 'N/A'}"

        # ── Step 7: Find food ──────────────────────────────────────
        step7 = PlanningStep(step="search_food", label="Finding local food experiences", status=StepStatus.RUNNING)
        planning_steps.append(step7)

        food_result, tc = self.food_tool.run(
            destination=selected.name,
            preferences=constraints.interests,
            dietary=constraints.dietary_preferences,
        )
        all_tool_calls.append(tc)
        
        available_meals: list[Meal] = []
        if food_result:
            available_meals = food_result.get("restaurants", [])
            if food_result.get("evidence"):
                all_evidence.append(food_result["evidence"])

        step7.status = StepStatus.COMPLETE
        step7.detail = f"Found {len(available_meals)} food options"

        # ── Step 8: Find activities ────────────────────────────────
        step8 = PlanningStep(step="search_activities", label="Discovering activities", status=StepStatus.RUNNING)
        planning_steps.append(step8)

        activities_result, tc = self.activities_tool.run(
            destination=selected.name,
            interests=constraints.interests,
            pace=constraints.pace.value,
        )
        all_tool_calls.append(tc)

        step8.status = StepStatus.COMPLETE
        step8.detail = f"Found {len(activities_result) if activities_result else 0} activities"

        # ── Step 9: Build itinerary ────────────────────────────────
        step9 = PlanningStep(step="build_itinerary", label="Building your itinerary", status=StepStatus.RUNNING)
        planning_steps.append(step9)

        itinerary = self._build_itinerary(
            destination=selected,
            constraints=constraints,
            stay=chosen_stay,
            meals=available_meals,
            activities=activities_result or [],
            transport_cost_pp=transport_pp,
            route_data=route_data,
        )

        step9.status = StepStatus.COMPLETE
        step9.detail = f"{constraints.duration_days}-day itinerary built"

        # ── Step 10: Calculate budget ──────────────────────────────
        step10 = PlanningStep(step="calculate_budget", label="Calculating budget", status=StepStatus.RUNNING)
        planning_steps.append(step10)

        budget, tc = self.budget_tool.run(
            transport_cost=transport_total,
            accommodation_cost=chosen_stay.cost_per_night * nights if chosen_stay else 0,
            food_cost=sum(d.daily_cost * 0.35 for d in itinerary.days),  # food portion
            activities_cost=sum(
                sum(a.cost_per_person * constraints.travellers for a in d.morning + d.afternoon + d.evening)
                for d in itinerary.days
            ),
            local_transport_cost=constraints.duration_days * 300 * constraints.travellers,
            travellers=constraints.travellers,
            duration_days=constraints.duration_days,
            budget_limit=constraints.budget_inr,
        )
        all_tool_calls.append(tc)

        # Recalculate more accurately
        actual_food = self._calculate_food_cost(itinerary, constraints)
        actual_activities = self._calculate_activities_cost(itinerary, constraints)
        actual_accommodation = (chosen_stay.cost_per_night if chosen_stay else 2000) * nights
        local_transport = constraints.duration_days * 250 * constraints.travellers

        final_budget, tc2 = self.budget_tool.run(
            transport_cost=transport_total,
            accommodation_cost=actual_accommodation,
            food_cost=actual_food,
            activities_cost=actual_activities,
            local_transport_cost=local_transport,
            travellers=constraints.travellers,
            duration_days=constraints.duration_days,
            budget_limit=constraints.budget_inr,
        )
        all_tool_calls.append(tc2)
        itinerary.budget = final_budget

        step10.status = StepStatus.COMPLETE
        step10.detail = f"Total: ₹{final_budget.total:,.0f} — {final_budget.status.value.replace('_', ' ').upper()}"

        # ── Step 11: Validate ──────────────────────────────────────
        step11 = PlanningStep(step="validate", label="Validating itinerary", status=StepStatus.RUNNING)
        planning_steps.append(step11)

        validation, tc = self.validator_tool.run(
            itinerary=itinerary,
            constraints=constraints,
        )
        all_tool_calls.append(tc)

        if validation:
            itinerary.constraints_satisfied = validation.get("satisfied", [])
            itinerary.constraints_unsatisfied = validation.get("issues", [])
            itinerary.warnings = validation.get("warnings", [])
            if validation.get("evidence"):
                all_evidence.append(validation["evidence"])

        step11.status = StepStatus.COMPLETE
        step11.detail = "Valid" if validation and validation.get("valid") else "Issues found"

        # ── Collect all evidence ───────────────────────────────────
        for candidate in top_candidates:
            all_evidence.extend(candidate.evidence)
        if chosen_stay and chosen_stay.evidence:
            all_evidence.append(chosen_stay.evidence)

        itinerary.evidence = all_evidence
        itinerary.selection_reasoning = selected.selection_reason or ""

        return PlanResponse(
            session_id=session_id,
            constraints=constraints,
            candidates=top_candidates,
            itinerary=itinerary,
            planning_steps=planning_steps,
            tool_calls=all_tool_calls,
        )

    def replan_trip(
        self,
        existing_plan: PlanResponse,
        new_message: str,
    ) -> ReplanResponse:
        """Re-plan a trip based on changed requirements."""
        # Detect changes
        new_constraints, changes = self.constraint_engine.detect_changes(
            existing_plan.constraints, new_message
        )
        preserved = self.constraint_engine.get_preserved_constraints(new_constraints, changes)

        if not changes:
            return ReplanResponse(
                session_id=existing_plan.session_id,
                replan_result=ReplanResult(
                    changes=[],
                    preserved=preserved,
                    new_constraints=new_constraints,
                    reasoning="No significant changes detected in your request.",
                ),
                planning_steps=[
                    PlanningStep(step="detect_changes", label="Analyzing changes", status=StepStatus.COMPLETE, detail="No changes detected")
                ],
                tool_calls=[],
            )

        # Check if destination change is needed
        needs_destination_change = any(
            c.field in ("budget_inr", "duration_days", "interests") for c in changes
        )

        # Re-plan with new constraints
        new_plan = self.plan_trip(new_constraints)

        replan_result = ReplanResult(
            changes=changes,
            preserved=preserved,
            new_constraints=new_constraints,
            new_itinerary=new_plan.itinerary,
            reasoning=self._generate_replan_reasoning(changes, new_plan, existing_plan),
        )

        return ReplanResponse(
            session_id=existing_plan.session_id,
            replan_result=replan_result,
            planning_steps=new_plan.planning_steps,
            tool_calls=new_plan.tool_calls,
        )

    # ── Private helpers ────────────────────────────────────────────

    def _build_itinerary(
        self,
        destination: CandidateDestination,
        constraints: ExtractedConstraints,
        stay: Accommodation | None,
        meals: list[Meal],
        activities: list[Activity],
        transport_cost_pp: float,
        route_data: dict | None,
    ) -> Itinerary:
        """Build a day-by-day itinerary."""
        days: list[DayPlan] = []
        num_days = constraints.duration_days

        # Separate activities by time slot
        morning_acts = [a for a in activities if a.time_slot == "morning"]
        afternoon_acts = [a for a in activities if a.time_slot == "afternoon"]
        evening_acts = [a for a in activities if a.time_slot == "evening"]

        # Separate meals by time slot
        breakfast_meals = [m for m in meals if m.time_slot == "breakfast"]
        lunch_meals = [m for m in meals if m.time_slot in ("lunch",)]
        dinner_meals = [m for m in meals if m.time_slot == "dinner"]
        snack_meals = [m for m in meals if m.time_slot == "snack"]

        # Activities per day based on pace
        acts_per_slot = {
            TravelPace.RELAXED: 1,
            TravelPace.MODERATE: 1,
            TravelPace.ACTIVE: 2,
            TravelPace.ADVENTURE: 2,
        }
        max_per_slot = acts_per_slot.get(constraints.pace, 1)

        # Track used activities and meals to avoid duplicates
        used_morning = 0
        used_afternoon = 0
        used_evening = 0
        used_meals: set[str] = set()

        travel_mode = ""
        if route_data and route_data.get("recommended_mode"):
            travel_mode = route_data["recommended_mode"]["mode"]

        for day_num in range(1, num_days + 1):
            is_first_day = day_num == 1
            is_last_day = day_num == num_days
            
            day_morning: list[Activity] = []
            day_afternoon: list[Activity] = []
            day_evening: list[Activity] = []
            day_meals: list[Meal] = []
            day_highlights: list[str] = []
            day_notes: list[str] = []
            day_cost = 0
            day_travel_km = 0

            # ── Day 1: Travel day ──────────────────────────────────
            if is_first_day:
                title = f"Arrival in {destination.name}"
                day_notes.append(f"Travel from {constraints.origin} via {travel_mode}")
                day_travel_km = destination.travel_distance_km

                # Add travel activity
                day_morning.append(Activity(
                    name=f"Travel from {constraints.origin} to {destination.name}",
                    description=f"Depart via {travel_mode} (~{destination.travel_time_hours:.0f}h journey)",
                    duration_hours=destination.travel_time_hours,
                    cost_per_person=transport_cost_pp,
                    category="transport",
                    time_slot="morning",
                    location=constraints.origin,
                ))
                day_cost += transport_cost_pp * constraints.travellers

                # Afternoon: arrive and settle, maybe one light activity
                if destination.travel_time_hours <= 6:
                    # If short travel, add an afternoon activity
                    if afternoon_acts and used_afternoon < len(afternoon_acts):
                        act = afternoon_acts[used_afternoon]
                        day_afternoon.append(act)
                        used_afternoon += 1
                        day_highlights.append(act.name)
                        day_cost += act.cost_per_person * constraints.travellers

                # Evening: dinner
                if evening_acts and used_evening < len(evening_acts):
                    act = evening_acts[used_evening]
                    day_evening.append(act)
                    used_evening += 1
                    day_highlights.append(act.name)
                    day_cost += act.cost_per_person * constraints.travellers

            # ── Last day: Departure ────────────────────────────────
            elif is_last_day:
                title = f"Farewell {destination.name}"
                day_notes.append(f"Depart for {constraints.origin} via {travel_mode}")

                # Morning: one light activity or breakfast spot
                if morning_acts and used_morning < len(morning_acts):
                    act = morning_acts[used_morning]
                    day_morning.append(act)
                    used_morning += 1
                    day_highlights.append(act.name)
                    day_cost += act.cost_per_person * constraints.travellers

                # Afternoon: travel back
                day_afternoon.append(Activity(
                    name=f"Return to {constraints.origin}",
                    description=f"Depart via {travel_mode} (~{destination.travel_time_hours:.0f}h journey)",
                    duration_hours=destination.travel_time_hours,
                    cost_per_person=transport_cost_pp,
                    category="transport",
                    time_slot="afternoon",
                    location=destination.name,
                ))
                day_cost += transport_cost_pp * constraints.travellers
                day_travel_km = destination.travel_distance_km

            # ── Middle days: Full exploration ──────────────────────
            else:
                title = f"Exploring {destination.name}"

                # Morning activities
                for _ in range(max_per_slot):
                    if morning_acts and used_morning < len(morning_acts):
                        act = morning_acts[used_morning]
                        day_morning.append(act)
                        used_morning += 1
                        day_highlights.append(act.name)
                        day_cost += act.cost_per_person * constraints.travellers

                # Afternoon activities
                for _ in range(max_per_slot):
                    if afternoon_acts and used_afternoon < len(afternoon_acts):
                        act = afternoon_acts[used_afternoon]
                        day_afternoon.append(act)
                        used_afternoon += 1
                        day_highlights.append(act.name)
                        day_cost += act.cost_per_person * constraints.travellers

                # Evening activities
                if evening_acts and used_evening < len(evening_acts):
                    act = evening_acts[used_evening]
                    day_evening.append(act)
                    used_evening += 1
                    day_highlights.append(act.name)
                    day_cost += act.cost_per_person * constraints.travellers

                day_travel_km = 15  # local exploration

            # ── Add meals for the day ──────────────────────────────
            # Breakfast
            if breakfast_meals:
                meal = breakfast_meals[day_num % len(breakfast_meals)]
                if meal.name not in used_meals or len(breakfast_meals) <= num_days:
                    day_meals.append(meal)
                    day_cost += meal.cost_per_person * constraints.travellers
                    used_meals.add(meal.name)

            # Lunch
            if lunch_meals:
                meal = lunch_meals[day_num % len(lunch_meals)]
                day_meals.append(meal)
                day_cost += meal.cost_per_person * constraints.travellers

            # Snack (every other day)
            if snack_meals and day_num % 2 == 0:
                meal = snack_meals[(day_num // 2) % len(snack_meals)]
                day_meals.append(meal)
                day_cost += meal.cost_per_person * constraints.travellers

            # Dinner
            if dinner_meals:
                meal = dinner_meals[day_num % len(dinner_meals)]
                day_meals.append(meal)
                day_cost += meal.cost_per_person * constraints.travellers

            # Fallback meals if none found
            if not day_meals:
                day_meals = [
                    Meal(name="Local breakfast", cuisine="Local", cost_per_person=150, time_slot="breakfast", description="Local breakfast"),
                    Meal(name="Lunch", cuisine="Local", cost_per_person=250, time_slot="lunch", description="Local lunch"),
                    Meal(name="Dinner", cuisine="Local", cost_per_person=300, time_slot="dinner", description="Local dinner"),
                ]
                day_cost += 700 * constraints.travellers

            # Accommodation (not on last day)
            day_accommodation = stay if not is_last_day else None
            if day_accommodation:
                day_cost += day_accommodation.cost_per_night

            # Relaxation level
            total_activity_hours = sum(a.duration_hours for a in day_morning + day_afternoon + day_evening)
            if total_activity_hours <= 4:
                relax_level = "high"
            elif total_activity_hours <= 7:
                relax_level = "medium"
            else:
                relax_level = "low"

            day = DayPlan(
                day_number=day_num,
                location=destination.name if not (is_first_day and destination.travel_time_hours > 6) else f"{constraints.origin} → {destination.name}",
                title=title,
                morning=day_morning,
                afternoon=day_afternoon,
                evening=day_evening,
                meals=day_meals,
                accommodation=day_accommodation,
                daily_cost=round(day_cost, 0),
                travel_km=day_travel_km,
                relaxation_level=relax_level,
                highlights=day_highlights[:3],
                notes=day_notes,
            )
            days.append(day)

        # Route summary
        route_summary = f"{constraints.origin} → {destination.name} (via {travel_mode}, ~{destination.travel_time_hours:.0f}h) → {constraints.origin}"
        travel_route = [constraints.origin, destination.name, constraints.origin]

        return Itinerary(
            destination=destination.name,
            destination_state=destination.state,
            duration_days=num_days,
            travellers=constraints.travellers,
            days=days,
            route_summary=route_summary,
            travel_route=travel_route,
        )

    def _calculate_food_cost(self, itinerary: Itinerary, constraints: ExtractedConstraints) -> float:
        """Calculate total food cost from itinerary meals."""
        total = 0
        for day in itinerary.days:
            for meal in day.meals:
                total += meal.cost_per_person * constraints.travellers
        return total

    def _calculate_activities_cost(self, itinerary: Itinerary, constraints: ExtractedConstraints) -> float:
        """Calculate total activities cost from itinerary."""
        total = 0
        for day in itinerary.days:
            for act in day.morning + day.afternoon + day.evening:
                if act.category != "transport":  # Transport counted separately
                    total += act.cost_per_person * constraints.travellers
        return total

    def _generate_selection_reason(self, selected: CandidateDestination, constraints: ExtractedConstraints) -> str:
        """Generate a human-readable explanation for why this destination was selected."""
        reasons = []
        reasons.append(f"{selected.name} was selected because it scores highest for your combination of interests")
        
        # Interest alignment
        interest_scores = []
        for interest in constraints.interests:
            score_map = {
                "nature": selected.nature_score,
                "food": selected.food_score,
                "relaxation": selected.relaxation_score,
                "adventure": selected.adventure_score,
                "culture": selected.culture_score,
            }
            if interest.lower() in score_map:
                interest_scores.append(f"{interest} ({score_map[interest.lower()]}/10)")
        if interest_scores:
            reasons.append(f"Interest scores: {', '.join(interest_scores)}")

        # Travel time
        reasons.append(f"Travel time from {constraints.origin}: ~{selected.travel_time_hours:.0f} hours")
        
        # Budget fit
        reasons.append(f"Estimated cost is within your ₹{constraints.budget_inr:,.0f} budget")

        # Weather
        if selected.weather_info:
            reasons.append(f"Current weather: {selected.weather_info}")

        return ". ".join(reasons) + "."

    def _generate_rejection_reason(self, rejected: CandidateDestination, selected: CandidateDestination, constraints: ExtractedConstraints) -> str:
        """Generate a reason for why a destination was not selected."""
        reasons = []
        
        if rejected.overall_score < selected.overall_score:
            diff = selected.overall_score - rejected.overall_score
            reasons.append(f"Lower overall match score ({rejected.overall_score:.1f} vs {selected.overall_score:.1f})")
        
        if rejected.travel_time_hours > selected.travel_time_hours + 2:
            reasons.append(f"Longer travel time ({rejected.travel_time_hours:.0f}h vs {selected.travel_time_hours:.0f}h)")
        
        if rejected.estimated_total_cost > constraints.budget_inr:
            reasons.append("Estimated cost exceeds budget")

        return ". ".join(reasons) if reasons else "Lower overall match for your requirements"

    def _generate_replan_reasoning(self, changes: list[ConstraintChange], new_plan: PlanResponse, old_plan: PlanResponse) -> str:
        """Generate reasoning for the re-plan."""
        parts = []
        
        for change in changes:
            parts.append(f"• {change.field.replace('_', ' ').title()}: {change.old_value} → {change.new_value}")
            if change.impact:
                parts.append(f"  Impact: {change.impact}")

        if new_plan.itinerary and old_plan.itinerary:
            if new_plan.itinerary.destination != old_plan.itinerary.destination:
                parts.append(f"\nDestination changed: {old_plan.itinerary.destination} → {new_plan.itinerary.destination}")
            else:
                parts.append(f"\nDestination kept: {new_plan.itinerary.destination}")
            
            parts.append(f"New budget: ₹{new_plan.itinerary.budget.total:,.0f} ({new_plan.itinerary.budget.status.value.replace('_', ' ')})")

        return "\n".join(parts)
