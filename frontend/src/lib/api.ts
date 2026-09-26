import { PlanResponse, ReplanResponse, EvalResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function planTrip(message: string, sessionId?: string): Promise<PlanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/plan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to plan trip');
  }

  return response.json();
}

export async function replanTrip(sessionId: string, message: string): Promise<ReplanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/replan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to replan trip');
  }

  return response.json();
}

export async function runEvaluation(): Promise<EvalResponse> {
  const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to run evaluation');
  }

  return response.json();
}

export async function runSecurityDemo(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/security-demo`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error('Failed to run security demo');
  }

  return response.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
}
