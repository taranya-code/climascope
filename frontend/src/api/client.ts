import type { AssessmentReport, AssessmentRequest, Site } from "../types";

const API_BASE = "/api";

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
