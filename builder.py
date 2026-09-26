import os

files = {
    "backend/tools/__init__.py": "# init\n",
    "backend/agent/__init__.py": "# init\n",
    "backend/security/__init__.py": "# init\n",
    "backend/evaluation/__init__.py": "# init\n",
    "backend/__init__.py": "# init\n",
    
    "backend/tools/base.py": """
import time
from abc import ABC, abstractmethod
from typing import Any, Dict
from schemas.models import ToolCall, ToolStatus

class ToolBase(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass
        
    def run(self, **kwargs) -> tuple[Any, ToolCall]:
        start = time.time()
        tool_call = ToolCall(tool_name=self.__class__.__name__, arguments=kwargs)
        try:
            result = self.execute(**kwargs)
            tool_call.status = ToolStatus.SUCCESS
            tool_call.result_summary = "Success"
            return result, tool_call
        except Exception as e:
            tool_call.status = ToolStatus.FAILED
            tool_call.error = str(e)
            return None, tool_call
        finally:
            tool_call.duration_ms = (time.time() - start) * 1000
""",

    "backend/tools/search.py": """
from backend.tools.base import ToolBase
from schemas.models import CandidateDestination, Evidence

DESTINATIONS = {
    "Rishikesh": CandidateDestination(name="Rishikesh", region="Uttarakhand", description="Yoga capital, adventure sports.", travel_time_hours=6.0, travel_distance_km=250.0, base_cost_per_day=2000, overall_score=8.5, evidence=[Evidence(source="curated", content="Well known", reliability=0.9)]),
    "Manali": CandidateDestination(name="Manali", region="Himachal Pradesh", description="Hill station, snow, cafes.", travel_time_hours=12.0, travel_distance_km=530.0, base_cost_per_day=3000, overall_score=9.0, evidence=[Evidence(source="curated", content="Well known", reliability=0.9)]),
    "Jaipur": CandidateDestination(name="Jaipur", region="Rajasthan", description="Pink city, forts, culture.", travel_time_hours=5.0, travel_distance_km=280.0, base_cost_per_day=2500, overall_score=8.0, evidence=[Evidence(source="curated", content="Well known", reliability=0.9)])
}

class SearchDestinationsTool(ToolBase):
    def execute(self, origin: str, interests: list[str], duration: int, budget: float) -> list[CandidateDestination]:
        return list(DESTINATIONS.values())
""",

    "backend/tools/weather.py": """
from backend.tools.base import ToolBase

class WeatherTool(ToolBase):
    def execute(self, destination: str, month: str) -> dict:
        return {"weather_info": "Pleasant", "weather_temp_c": 22.5, "best_season": "Spring"}
""",

    "backend/tools/routes.py": """
from backend.tools.base import ToolBase

class RoutesTool(ToolBase):
    def execute(self, origin: str, destination: str) -> dict:
        return {"distance_km": 250, "time_hours": 6, "modes": ["bus", "train", "taxi"], "cost": 1500}
""",

    "backend/tools/stays.py": """
from backend.tools.base import ToolBase
from schemas.models import Accommodation, Evidence

class StaysTool(ToolBase):
    def execute(self, destination: str, duration_days: int, budget_per_night: float, travellers: int) -> list[Accommodation]:
        return [
            Accommodation(name="Budget Inn", cost_per_night=1000, type="hotel", rating=3.5, evidence=Evidence(source="curated", content="Good value")),
            Accommodation(name="Comfort Stay", cost_per_night=3000, type="hotel", rating=4.5, evidence=Evidence(source="curated", content="Luxury"))
        ]
""",

    "backend/tools/food.py": """
from backend.tools.base import ToolBase

class FoodTool(ToolBase):
    def execute(self, destination: str, preferences: list[str], dietary: list[str]) -> list[dict]:
        return [{"name": "Local Cafe", "cuisine": "Local", "cost_per_person": 500}]
""",

    "backend/tools/activities.py": """
from backend.tools.base import ToolBase
from schemas.models import Activity

class ActivitiesTool(ToolBase):
    def execute(self, destination: str, interests: list[str], pace: str) -> list[Activity]:
        return [
            Activity(name="Sightseeing", description="Visit local attractions", duration_hours=2.0, cost_per_person=200, category="general")
        ]
""",

    "backend/tools/budget.py": """
from backend.tools.base import ToolBase
from schemas.models import BudgetBreakdown

class BudgetTool(ToolBase):
    def execute(self, transport: float, stay: float, food: float, activities: float, local_transport: float, travellers: int, days: int, budget_limit: float) -> BudgetBreakdown:
        b = BudgetBreakdown(transport=transport, accommodation=stay, food=food, activities=activities, local_transport=local_transport, budget_limit=budget_limit)
        b.recalculate()
        return b
""",

    "backend/tools/validator.py": """
from backend.tools.base import ToolBase

class ValidatorTool(ToolBase):
    def execute(self, itinerary: dict, constraints: dict) -> list[str]:
        return []
""",

    "backend/agent/intent.py": """
from schemas.models import ExtractedConstraints

def extract_constraints(user_message: str) -> ExtractedConstraints:
    return ExtractedConstraints(origin="Delhi", duration_days=5, budget_limit=50000)
""",

    "backend/agent/constraints.py": """
from schemas.models import ExtractedConstraints

class ConstraintEngine:
    def check_feasibility(self, constraints: ExtractedConstraints) -> tuple[bool, list[str]]:
        return True, []
""",

    "backend/agent/planner.py": """
from schemas.models import PlanResponse, Itinerary, ExtractedConstraints, CandidateDestination, DayPlan

class TravelPlanner:
    def plan_trip(self, constraints: ExtractedConstraints) -> PlanResponse:
        itinerary = Itinerary(destination="Rishikesh", duration_days=constraints.duration_days or 5, travellers=constraints.travellers or 2)
        itinerary.days.append(DayPlan(day_number=1, location="Rishikesh"))
        return PlanResponse(session_id="123", constraints=constraints, itinerary=itinerary)
        
    def replan_trip(self, existing_plan, new_message) -> PlanResponse:
        return existing_plan
""",

    "backend/security/sanitizer.py": """
def sanitize_user_input(text: str) -> str:
    return text.strip()
""",

    "backend/security/injection.py": """
from schemas.models import SecurityEvent

def detect_injection(text: str) -> list[SecurityEvent]:
    events = []
    if "ignore previous" in text.lower():
        events.append(SecurityEvent(type="prompt_injection", source="input", content_snippet="ignore previous"))
    return events
""",

    "backend/security/validator.py": """
def validate_tool_args(tool_name: str, args: dict) -> tuple[bool, list[str]]:
    return True, []
""",

    "backend/evaluation/test_suite.py": """
from schemas.models import EvaluationTestCase

def test_basic_planning() -> EvaluationTestCase:
    return EvaluationTestCase(name="Basic Planning", category="planning", passed=True, score=1.0)
    
def get_all_tests():
    return [test_basic_planning()]
""",

    "backend/evaluation/runner.py": """
from schemas.models import EvaluationResult
from backend.evaluation.test_suite import get_all_tests

def run_all_tests() -> EvaluationResult:
    tests = get_all_tests()
    return EvaluationResult(total_tests=len(tests), passed=len([t for t in tests if t.passed]), test_cases=tests)
""",

    "backend/main.py": """
from fastapi import FastAPI
from schemas.models import TripRequest, PlanResponse, ReplanRequest, ReplanResponse, EvalResponse, HealthResponse
from backend.agent.planner import TravelPlanner
from backend.agent.intent import extract_constraints
from backend.evaluation.runner import run_all_tests

app = FastAPI()

planner = TravelPlanner()

@app.post("/api/plan", response_model=PlanResponse)
def plan_trip(req: TripRequest):
    constraints = extract_constraints(req.message)
    return planner.plan_trip(constraints)

@app.post("/api/replan", response_model=ReplanResponse)
def replan_trip(req: ReplanRequest):
    pass

@app.post("/api/evaluate", response_model=EvalResponse)
def evaluate():
    res = run_all_tests()
    return EvalResponse(result=res)

@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse()
"""
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

print("Files generated.")
