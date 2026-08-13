import type { AssessmentReport } from "../types";

interface Props {
  report: AssessmentReport;
}

export default function RecommendationsList({ report }: Props) {
  return (
    <div className="card">
      <h2>Recommendations</h2>
      <ol className="recommendation-list">
        {report.recommendations.map((rec) => (
          <li key={rec.title}>
            <strong>{rec.title}</strong>
            <p>{rec.rationale}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
