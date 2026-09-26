/**
 * ROAM — Frontend Types
 * Mirrors the backend Pydantic schemas exactly.
 */

// ── Enums ──────────────────────────────────────────────────────────────

export type TravelPace = 'relaxed' | 'moderate' | 'active' | 'adventure';
export type ConstraintType = 'hard' | 'soft';
export type SourceType = 'verified' | 'estimated' | 'user_provided' | 'curated';
export type ToolStatus = 'success' | 'error' | 'timeout' | 'skipped' | 'fallback';
export type BudgetStatusType = 'under_budget' | 'on_budget' | 'over_budget';
export type StepStatus = 'pending' | 'running' | 'complete' | 'error';

// ── Constraint ─────────────────────────────────────────────────────────

export interface Constraint {
  type: ConstraintType;
  field: string;
  operator: string;
  value: any;
  description: string;
}

// ── Extracted Constraints ──────────────────────────────────────────────

export interface ExtractedConstraints {
  origin: string;
  destination?: string | null;
  travellers: number;
  duration_days: number;
  budget_inr: number;
  interests: string[];
  pace: TravelPace;
  hard_constraints: Constraint[];
  soft_preferences: Constraint[];
  dietary_preferences: string[];
  accessibility_needs: string[];
  travel_style: string;
  early_riser?: boolean | null;
  additional_notes: string[];
}

// ── Evidence ───────────────────────────────────────────────────────────

export interface Evidence {
  source: string;
  source_type: SourceType;
  confidence: number;
  data: string;
  url?: string | null;
  retrieved_at?: string | null;
}

// ── Candidate Destination ──────────────────────────────────────────────

export interface CandidateDestination {
  name: string;
  state: string;
  travel_time_hours: number;
  travel_distance_km: number;
  travel_modes: string[];
  estimated_total_cost: number;
  nature_score: number;
  food_score: number;
  relaxation_score: number;
  adventure_score: number;
  culture_score: number;
  weather_info: string;
  weather_temp_c?: number | null;
  best_season: string;
  evidence: Evidence[];
  overall_score: number;
  selected: boolean;
  selection_reason?: string | null;
  rejected_reason?: string | null;
}

// ── Itinerary Components ───────────────────────────────────────────────

export interface Activity {
  name: string;
  description: string;
  duration_hours: number;
  cost_per_person: number;
  category: string;
  time_slot: string;
  location: string;
  evidence?: Evidence | null;
  notes?: string | null;
}

export interface Meal {
  name: string;
  cuisine: string;
  cost_per_person: number;
  time_slot: string;
  description: string;
  is_local_specialty: boolean;
  dietary_tags: string[];
  evidence?: Evidence | null;
}

export interface Accommodation {
  name: string;
  type: string;
  cost_per_night: number;
  location: string;
  rating?: number | null;
  amenities: string[];
  evidence?: Evidence | null;
}

export interface DayPlan {
  day_number: number;
  date?: string | null;
  location: string;
  title: string;
  morning: Activity[];
  afternoon: Activity[];
  evening: Activity[];
  meals: Meal[];
  accommodation?: Accommodation | null;
  daily_cost: number;
  travel_km: number;
  relaxation_level: string;
  highlights: string[];
  notes: string[];
}

// ── Budget ─────────────────────────────────────────────────────────────

export interface BudgetBreakdown {
  transport: number;
  accommodation: number;
  food: number;
  activities: number;
  local_transport: number;
  emergency_buffer: number;
  miscellaneous: number;
  total: number;
  budget_limit: number;
  status: BudgetStatusType;
  per_person: number;
  savings: number;
}

// ── Itinerary ──────────────────────────────────────────────────────────

export interface Itinerary {
  destination: string;
  destination_state: string;
  duration_days: number;
  travellers: number;
  days: DayPlan[];
  budget: BudgetBreakdown;
  route_summary: string;
  travel_route: string[];
  evidence: Evidence[];
  selection_reasoning: string;
  constraints_satisfied: string[];
  constraints_unsatisfied: string[];
  warnings: string[];
}

// ── Tool Tracking ──────────────────────────────────────────────────────

export interface ToolCall {
  tool_name: string;
  arguments: Record<string, string>;
  status: ToolStatus;
  result_summary: string;
  duration_ms: number;
  error?: string | null;
}

export interface PlanningStep {
  step: string;
  label: string;
  status: StepStatus;
  detail: string;
  tool_calls: ToolCall[];
  timestamp?: string | null;
}

// ── Constraint Change / Replan ─────────────────────────────────────────

export interface ConstraintChange {
  field: string;
  old_value: string;
  new_value: string;
  impact: string;
}

export interface ReplanResult {
  changes: ConstraintChange[];
  preserved: string[];
  new_constraints?: ExtractedConstraints | null;
  new_itinerary?: Itinerary | null;
  reasoning: string;
}

// ── Security ───────────────────────────────────────────────────────────

export interface SecurityEvent {
  type: string;
  source: string;
  content_snippet: string;
  status: 'blocked' | 'sanitized' | 'flagged';
  detail: string;
  timestamp?: string | null;
}

// ── Evaluation ─────────────────────────────────────────────────────────

export interface EvaluationTestCase {
  name: string;
  category: string;
  description: string;
  passed: boolean;
  score: number;
  details: string;
  errors: string[];
}

export interface EvaluationResult {
  total_tests: number;
  passed: number;
  failed: number;
  categories: Record<string, number>;
  test_cases: EvaluationTestCase[];
  overall_score: number;
  run_timestamp?: string | null;
}

// ── API Responses ──────────────────────────────────────────────────────

export interface PlanResponse {
  session_id: string;
  constraints: ExtractedConstraints;
  candidates: CandidateDestination[];
  itinerary?: Itinerary | null;
  planning_steps: PlanningStep[];
  tool_calls: ToolCall[];
  security_events: SecurityEvent[];
  error?: string | null;
}

export interface ReplanResponse {
  session_id: string;
  replan_result?: ReplanResult | null;
  planning_steps: PlanningStep[];
  tool_calls: ToolCall[];
  security_events: SecurityEvent[];
  error?: string | null;
}

export interface EvalResponse {
  result: EvaluationResult;
  security_events: SecurityEvent[];
}

// ── Request types ──────────────────────────────────────────────────────

export interface TripRequest {
  message: string;
  session_id?: string;
}

export interface ReplanRequest {
  session_id: string;
  message: string;
}
