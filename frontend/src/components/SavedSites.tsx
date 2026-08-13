import { useEffect, useState } from "react";
import { deleteSite, listSiteAssessments, listSites } from "../api/client";
import type { AssessmentReport, Site } from "../types";

interface Props {
  refreshKey: number;
  onSelectReport: (report: AssessmentReport) => void;
}

export default function SavedSites({ refreshKey, onSelectReport }: Props) {
  const [sites, setSites] = useState<Site[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listSites()
      .then(setSites)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load sites"));
  }, [refreshKey]);

  async function handleDelete(siteId: number) {
    await deleteSite(siteId);
    setSites((prev) => prev.filter((s) => s.id !== siteId));
  }

  async function handleView(siteId: number) {
    const assessments = await listSiteAssessments(siteId);
    if (assessments.length > 0) {
      onSelectReport(assessments[0]);
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
        <ul className="site-list">
          {sites.map((site) => (
            <li key={site.id}>
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
      )}
    </div>
  );
}
