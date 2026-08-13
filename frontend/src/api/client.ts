import type { AssessmentReport, AssessmentRequest, Site } from "../types";

// In dev, "/api" is rewritten to the local backend by the Vite proxy (see
// vite.config.ts). In production there's no dev server to proxy through, so
// VITE_API_BASE_URL must point straight at the deployed backend's origin.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function createAssessment(payload: AssessmentRequest): Promise<AssessmentReport> {
  return request<AssessmentReport>("/assess", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listSites(): Promise<Site[]> {
  return request<Site[]>("/sites");
}

export function deleteSite(siteId: number): Promise<void> {
  return request<void>(`/sites/${siteId}`, { method: "DELETE" });
}

export function listSiteAssessments(siteId: number): Promise<AssessmentReport[]> {
  return request<AssessmentReport[]>(`/sites/${siteId}/assessments`);
}
