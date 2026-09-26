"""
ROAM — AI Travel Agent
Core data models and schemas using Pydantic v2.
All data flowing through the system is typed here.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


# ── Enums ───────────────────────────────────────────────────────────────

class TravelPace(str, Enum):
    RELAXED = "relaxed"
    MODERATE = "moderate"
    ACTIVE = "active"
    ADVENTURE = "adventure"


class ConstraintType(str, Enum):
    HARD = "hard"
    SOFT = "soft"


class SourceType(str, Enum):
    VERIFIED = "verified"
    ESTIMATED = "estimated"
    USER_PROVIDED = "user_provided"
    CURATED = "curated"


class ToolStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"
    FALLBACK = "fallback"


class BudgetStatus(str, Enum):
    UNDER_BUDGET = "under_budget"
    ON_BUDGET = "on_budget"
    OVER_BUDGET = "over_budget"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


# ── Constraint ──────────────────────────────────────────────────────────

class Constraint(BaseModel):
    type: ConstraintType
    field: str
    operator: str = Field(description="Comparison operator: <=, ==, >=, in, not_in, contains")
    value: Any
    description: str


# ── Trip Request (from frontend) ────────────────────────────────────────

class TripRequest(BaseModel):
    message: str = Field(min_length=5, max_length=2000)
    session_id: Optional[str] = None

    @field_validator("message")
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        # Basic length check — deeper sanitization in security layer
        return v.strip()


class ReplanRequest(BaseModel):
    session_id: str
    message: str = Field(min_length=3, max_length=2000)


# ── Extracted Constraints ───────────────────────────────────────────────

class ExtractedConstraints(BaseModel):
    origin: str = "Delhi"
    destination: Optional[str] = None  # None means agent should decide
    travellers: int = 2
    duration_days: int = 5
    budget_inr: float = 50000
    interests: list[str] = Field(default_factory=lambda: ["nature", "food"])
    pace: TravelPace = TravelPace.RELAXED
    hard_constraints: list[Constraint] = Field(default_factory=list)
    soft_preferences: list[Constraint] = Field(default_factory=list)
    dietary_preferences: list[str] = Field(default_factory=list)
    accessibility_needs: list[str] = Field(default_factory=list)
    travel_style: str = "budget"
    early_riser: Optional[bool] = None
    additional_notes: list[str] = Field(default_factory=list)


# ── Evidence / Sources ──────────────────────────────────────────────────

class Evidence(BaseModel):
    source: str
    source_type: SourceType = SourceType.ESTIMATED
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)
    data: str
    url: Optional[str] = None
    retrieved_at: Optional[str] = None


# ── Candidate Destinations ──────────────────────────────────────────────

class CandidateDestination(BaseModel):
    name: str
    state: str
    travel_time_hours: float
    travel_distance_km: float
    travel_modes: list[str] = Field(default_factory=lambda: ["bus", "train"])
    estimated_total_cost: float
    nature_score: float = Field(ge=0, le=10, default=5)
    food_score: float = Field(ge=0, le=10, default=5)
    relaxation_score: float = Field(ge=0, le=10, default=5)
    adventure_score: float = Field(ge=0, le=10, default=5)
    culture_score: float = Field(ge=0, le=10, default=5)
    weather_info: str = ""
    weather_temp_c: Optional[float] = None
    best_season: str = ""
    evidence: list[Evidence] = Field(default_factory=list)
    overall_score: float = 0.0
    selected: bool = False
    selection_reason: Optional[str] = None
    rejected_reason: Optional[str] = None


# ── Itinerary Components ────────────────────────────────────────────────

class Activity(BaseModel):
    name: str
    description: str
    duration_hours: float = 1.5
    cost_per_person: float = 0
    category: str = "general"  # nature, food, culture, adventure, shopping, etc.
    time_slot: str = "morning"  # morning, afternoon, evening
    location: str = ""
    evidence: Optional[Evidence] = None
    notes: Optional[str] = None


class Meal(BaseModel):
    name: str
    cuisine: str = ""
    cost_per_person: float = 200
    time_slot: str = "lunch"  # breakfast, lunch, dinner, snack
    description: str = ""
    is_local_specialty: bool = False
    dietary_tags: list[str] = Field(default_factory=list)  # veg, non-veg, street-food
    evidence: Optional[Evidence] = None


class Accommodation(BaseModel):
    name: str
    type: str = "hotel"  # hotel, homestay, hostel, resort, camp
    cost_per_night: float
    location: str = ""
    rating: Optional[float] = Field(ge=0, le=5, default=None)
    amenities: list[str] = Field(default_factory=list)
    evidence: Optional[Evidence] = None


class DayPlan(BaseModel):
    day_number: int
    date: Optional[str] = None
    location: str
    title: str = ""  # e.g. "Arrival & Lakeside Walk"
    morning: list[Activity] = Field(default_factory=list)
    afternoon: list[Activity] = Field(default_factory=list)
    evening: list[Activity] = Field(default_factory=list)
    meals: list[Meal] = Field(default_factory=list)
    accommodation: Optional[Accommodation] = None
    daily_cost: float = 0
    travel_km: float = 0
    relaxation_level: str = "high"  # high, medium, low
    highlights: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


# ── Budget ──────────────────────────────────────────────────────────────

class BudgetBreakdown(BaseModel):
    transport: float = 0
    accommodation: float = 0
    food: float = 0
    activities: float = 0
    local_transport: float = 0
    emergency_buffer: float = 0
    miscellaneous: float = 0
    total: float = 0
    budget_limit: float = 50000
    status: BudgetStatus = BudgetStatus.UNDER_BUDGET
    per_person: float = 0
    savings: float = 0  # budget_limit - total

    def recalculate(self) -> None:
        self.total = (
            self.transport
            + self.accommodation
            + self.food
            + self.activities
            + self.local_transport
            + self.emergency_buffer
            + self.miscellaneous
        )
        if self.total <= self.budget_limit * 0.95:
            self.status = BudgetStatus.UNDER_BUDGET
        elif self.total <= self.budget_limit:
            self.status = BudgetStatus.ON_BUDGET
        else:
            self.status = BudgetStatus.OVER_BUDGET
        self.savings = self.budget_limit - self.total


# ── Full Itinerary ──────────────────────────────────────────────────────

class Itinerary(BaseModel):
    destination: str
    destination_state: str = ""
    duration_days: int
    travellers: int
    days: list[DayPlan] = Field(default_factory=list)
    budget: BudgetBreakdown = Field(default_factory=BudgetBreakdown)
    route_summary: str = ""
    travel_route: list[str] = Field(default_factory=list)  # ["Delhi", "Rishikesh", ...]
    evidence: list[Evidence] = Field(default_factory=list)
    selection_reasoning: str = ""
    constraints_satisfied: list[str] = Field(default_factory=list)
    constraints_unsatisfied: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# ── Tool Tracking ───────────────────────────────────────────────────────

class ToolCall(BaseModel):
    tool_name: str
    arguments: dict = Field(default_factory=dict)
    status: ToolStatus = ToolStatus.SUCCESS
    result_summary: str = ""
    duration_ms: float = 0
    error: Optional[str] = None


class PlanningStep(BaseModel):
    step: str
    label: str = ""  # User-facing label
    status: StepStatus = StepStatus.PENDING
    detail: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)
    timestamp: Optional[str] = None


# ── Constraint Change / Replan ──────────────────────────────────────────

class ConstraintChange(BaseModel):
    field: str
    old_value: str
    new_value: str
    impact: str = ""


class ReplanResult(BaseModel):
    changes: list[ConstraintChange] = Field(default_factory=list)
    preserved: list[str] = Field(default_factory=list)
    new_constraints: Optional[ExtractedConstraints] = None
    new_itinerary: Optional[Itinerary] = None
    reasoning: str = ""


# ── Security ────────────────────────────────────────────────────────────

class SecurityEvent(BaseModel):
    type: str  # prompt_injection, invalid_input, suspicious_url, etc.
    source: str
    content_snippet: str = ""
    status: Literal["blocked", "sanitized", "flagged"] = "blocked"
    detail: str = ""
    timestamp: Optional[str] = None


# ── Evaluation ──────────────────────────────────────────────────────────

class EvaluationTestCase(BaseModel):
    name: str
    category: str
    description: str
    passed: bool = False
    score: float = Field(ge=0, le=1, default=0)
    details: str = ""
    errors: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    categories: dict[str, float] = Field(default_factory=dict)
    test_cases: list[EvaluationTestCase] = Field(default_factory=list)
    overall_score: float = 0.0
    run_timestamp: Optional[str] = None


# ── API Responses ───────────────────────────────────────────────────────

class PlanResponse(BaseModel):
    session_id: str
    constraints: ExtractedConstraints
    candidates: list[CandidateDestination] = Field(default_factory=list)
    itinerary: Optional[Itinerary] = None
    planning_steps: list[PlanningStep] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    security_events: list[SecurityEvent] = Field(default_factory=list)
    error: Optional[str] = None


class ReplanResponse(BaseModel):
    session_id: str
    replan_result: Optional[ReplanResult] = None
    planning_steps: list[PlanningStep] = Field(default_factory=list)
    tool_calls: list[ToolCall] = Field(default_factory=list)
    security_events: list[SecurityEvent] = Field(default_factory=list)
    error: Optional[str] = None


class EvalResponse(BaseModel):
    result: EvaluationResult
    security_events: list[SecurityEvent] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    agent_ready: bool = True
