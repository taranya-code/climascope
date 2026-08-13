import { useState } from "react";
import ComparisonTable from "./components/ComparisonTable";
import type { ComparisonItem } from "./components/ComparisonTable";
import LocationForm from "./components/LocationForm";
import RecommendationsList from "./components/RecommendationsList";
import ResultsPanel from "./components/ResultsPanel";
import RiskChart from "./components/RiskChart";
import SavedSites from "./components/SavedSites";
import { createAssessment } from "./api/client";
import type { AssessmentReport, AssessmentRequest } from "./types";

export default function App() {
  const [report, setReport] = useState<AssessmentReport | null>(null);
  const [comparison, setComparison] = useState<ComparisonItem[] | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  async function handleAssess(payload: AssessmentRequest) {
    setIsSubmitting(true);
    setError(null);
    try {
      const result = await createAssessment(payload);
      setReport(result);
      setComparison(null);
      setRefreshKey((key) => key + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleSelectReport(selected: AssessmentReport) {
    setReport(selected);
    setComparison(null);
  }

  function handleCompare(items: ComparisonItem[]) {
    setComparison(items);
    setError(null);
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ClimaScope</h1>
        <p className="tagline">Renewable energy feasibility &amp; climate adaptation planning</p>
      </header>

      <main className="app-grid">
        <div className="app-column">
          <LocationForm onSubmit={handleAssess} isSubmitting={isSubmitting} />
          <SavedSites refreshKey={refreshKey} onSelectReport={handleSelectReport} onCompare={handleCompare} />
        </div>

        <div className="app-column">
          {error && <div className="card error">{error}</div>}
          {comparison ? (
            <ComparisonTable items={comparison} onClose={() => setComparison(null)} />
          ) : report ? (
            <>
              <ResultsPanel report={report} />
              <RiskChart report={report} />
              <RecommendationsList report={report} />
            </>
          ) : (
            <div className="card muted-card">Run an assessment to see results here.</div>
          )}
        </div>
      </main>
    </div>
  );
}
