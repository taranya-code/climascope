import { useEffect, useState } from "react";
import { deleteSite, listSiteAssessments, listSites } from "../api/client";
import type { ComparisonItem } from "./ComparisonTable";
import type { AssessmentReport, Site } from "../types";

interface Props {
  refreshKey: number;
  onSelectReport: (report: AssessmentReport) => void;
  onCompare: (items: ComparisonItem[]) => void;
}

export default function SavedSites({ refreshKey, onSelectReport, onCompare }: Props) {
  const [sites, setSites] = useState<Site[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [isComparing, setIsComparing] = useState(false);

  useEffect(() => {
    listSites()
      .then(setSites)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load sites"));
  }, [refreshKey]);

  async function handleDelete(siteId: number) {
    await deleteSite(siteId);
    setSites((prev) => prev.filter((s) => s.id !== siteId));
    setSelectedIds((prev) => {
      const next = new Set(prev);
      next.delete(siteId);
      return next;
    });
  }

  async function handleView(siteId: number) {
    const assessments = await listSiteAssessments(siteId);
    if (assessments.length > 0) {
      onSelectReport(assessments[0]);
    }
  }

  function toggleSelected(siteId: number) {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(siteId)) {
        next.delete(siteId);
      } else {
        next.add(siteId);
      }
      return next;
    });
  }

  async function handleCompare() {
    setIsComparing(true);
    setError(null);
    try {
      const selectedSites = sites.filter((s) => selectedIds.has(s.id));
      const items = await Promise.all(
        selectedSites.map(async (site) => {
          const assessments = await listSiteAssessments(site.id);
          return { site, report: assessments[0] };
        }),
      );
      const withReports = items.filter(
        (item): item is ComparisonItem => item.report !== undefined,
      );
      onCompare(withReports);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to compare sites");
    } finally {
      setIsComparing(false);
    }
  }

  if (error) {
    return <div className="card error">Failed to load sites: {error}</div>;
  }

  return (
    <div className="card">
      <h2>Saved sites</h2>
      {sites.length === 0 ? (
        <p className="muted">No sites assessed yet.</p>
      ) : (
        <>
          <p className="muted">Select 2+ to compare.</p>
          <ul className="site-list">
            {sites.map((site) => (
              <li key={site.id}>
                <input
                  type="checkbox"
                  checked={selectedIds.has(site.id)}
                  onChange={() => toggleSelected(site.id)}
                  aria-label={`Select ${site.name} for comparison`}
                />
                <button type="button" className="site-link" onClick={() => handleView(site.id)}>
                  {site.name}
                </button>
                <span className="muted">
                  {site.lat.toFixed(3)}, {site.lon.toFixed(3)}
                </span>
                <button type="button" className="text-button" onClick={() => handleDelete(site.id)}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
          {selectedIds.size >= 2 && (
            <button
              type="button"
              className="secondary-button compare-button"
              onClick={handleCompare}
              disabled={isComparing}
            >
              {isComparing ? "Loading…" : `Compare ${selectedIds.size} selected`}
            </button>
          )}
        </>
      )}
    </div>
  );
}
