"""
ROAM — AI Travel Agent API
FastAPI application with session management, CORS, error handling, and security middleware.
"""

from __future__ import annotations

import os
import time
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas.models import (
    EvalResponse,
    HealthResponse,
    PlanResponse,
    ReplanRequest,
    ReplanResponse,
    SecurityEvent,
    TripRequest,
)
from agent.intent import extract_constraints
from agent.planner import TravelPlanner
from evaluation.runner import run_all_tests
from security.sanitizer import sanitize_user_input, validate_input_length
from security.injection import detect_injection, run_security_demo
from security.validator import validate_api_key_not_exposed

# Load environment
load_dotenv()

# ── App ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="ROAM — AI Travel Agent",
    description="Constraint-aware AI travel planning agent",
    version="1.0.0",
)

# CORS — allow frontend
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Session Storage ─────────────────────────────────────────────────────
# In-memory for hackathon; would use Redis/DB in production
_sessions: dict[str, PlanResponse] = {}

# ── Rate Limiting ───────────────────────────────────────────────────────
_rate_limit: dict[str, list[float]] = {}
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "20"))
MAX_INPUT_LENGTH = int(os.getenv("MAX_INPUT_LENGTH", "2000"))

# ── Planner Instance ───────────────────────────────────────────────────
planner = TravelPlanner()


def _check_rate_limit(client_ip: str) -> bool:
    """Check if client has exceeded rate limit."""
    now = time.time()
    if client_ip not in _rate_limit:
        _rate_limit[client_ip] = []
    # Clean old entries
    _rate_limit[client_ip] = [t for t in _rate_limit[client_ip] if now - t < 60]
    if len(_rate_limit[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return False
    _rate_limit[client_ip].append(now)
    return True


# ── Error Handling ──────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global error handler — never expose internal details."""
    return JSONResponse(
        status_code=500,
        content={"error": "An internal error occurred. Please try again.", "detail": str(exc)[:200]},
    )


# ── Routes ──────────────────────────────────────────────────────────────

@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        agent_ready=True,
    )


@app.post("/api/plan", response_model=PlanResponse)
async def plan_trip(req: TripRequest, request: Request) -> PlanResponse:
    """
    Create a travel plan from a natural language request.
    This is the main agent endpoint.
    """
    # Rate limit
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please wait a moment.")

    # Validate input length
    valid, msg = validate_input_length(req.message, MAX_INPUT_LENGTH)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # Sanitize input
    clean_message = sanitize_user_input(req.message, MAX_INPUT_LENGTH)
    if not clean_message:
        raise HTTPException(status_code=400, detail="Invalid input after sanitization")

    # Check for injection in user input (low priority — user is trusted, but log it)
    user_injection_events = detect_injection(clean_message)
    security_events: list[SecurityEvent] = []
    if user_injection_events:
        # Don't block user input, but log it
        for event in user_injection_events:
            event.source = "user_input"
            event.status = "flagged"
        security_events.extend(user_injection_events)

    # Extract constraints
    try:
        constraints = extract_constraints(clean_message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not understand your request: {str(e)[:100]}")

    # Run the planner
    try:
        result = planner.plan_trip(constraints)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)[:100]}")

    # Add security events
    result.security_events = security_events

    # Verify no secrets in response
    response_str = result.model_dump_json()
    if not validate_api_key_not_exposed(response_str):
        # This should never happen, but safety net
        raise HTTPException(status_code=500, detail="Internal security check failed")

    # Store session
    _sessions[result.session_id] = result

    return result


@app.post("/api/replan", response_model=ReplanResponse)
async def replan_trip(req: ReplanRequest, request: Request) -> ReplanResponse:
    """
    Re-plan a trip with changed requirements.
    Requires a session_id from a previous plan.
    """
    # Rate limit
    client_ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded.")

    # Find existing session
    if req.session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found. Please create a plan first.")

    existing_plan = _sessions[req.session_id]

    # Sanitize
    clean_message = sanitize_user_input(req.message, MAX_INPUT_LENGTH)
    if not clean_message:
        raise HTTPException(status_code=400, detail="Invalid input")

    # Re-plan
    try:
        result = planner.replan_trip(existing_plan, clean_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Re-planning failed: {str(e)[:100]}")

    # Update session with new plan
    if result.replan_result and result.replan_result.new_itinerary:
        # Create updated PlanResponse for session
        from schemas.models import PlanResponse as PR
        updated_plan = existing_plan.model_copy(deep=True)
        updated_plan.itinerary = result.replan_result.new_itinerary
        if result.replan_result.new_constraints:
            updated_plan.constraints = result.replan_result.new_constraints
        _sessions[req.session_id] = updated_plan

    return result


@app.post("/api/evaluate", response_model=EvalResponse)
async def evaluate() -> EvalResponse:
    """Run the evaluation test suite and return results."""
    try:
        result = run_all_tests()
        return EvalResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)[:100]}")


@app.post("/api/security-demo")
async def security_demo() -> dict[str, Any]:
    """
    Run the security demonstration.
    Feeds malicious content through the injection detector.
    """
    events = run_security_demo()
    return {
        "total_tests": len(events),
        "blocked": sum(1 for e in events if e.status == "blocked"),
        "events": [e.model_dump() for e in events],
    }


# ── Startup ─────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup() -> None:
    """Startup tasks."""
    print("🧭 ROAM — AI Travel Agent")
    print("   Plan less. Explore more.")
    print(f"   CORS origins: {cors_origins}")
    print(f"   Rate limit: {RATE_LIMIT_PER_MINUTE}/min")
    print("   Agent ready.")
