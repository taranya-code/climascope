import type { AssessmentReport } from "../types";

interface Props {
  report: AssessmentReport;
}

export default function ResultsPanel({ report }: Props) {
  return (
    <div className="card">
      <h2>Results</h2>
      <div className="stat-grid">
        <div className="stat">
          <span className="stat-label">Solar output</span>
          <span className="stat-value">{report.solar_annual_kwh.toLocaleString()} kWh/yr</span>
          <span className="stat-sub">{report.solar_daily_kwh.toLocaleString()} kWh/day</span>
        </div>
        <div className="stat">
          <span className="stat-label">Wind output</span>
          <span className="stat-value">{report.wind_annual_kwh.toLocaleString()} kWh/yr</span>
          <span className="stat-sub">
            class: {report.wind_class} @ {report.hub_height_wind_speed_ms} m/s
          </span>
        </div>
        <div className="stat">
          <span className="stat-label">Heat stress</span>
          <span className="stat-value">{report.heat_stress_days_per_year} days/yr</span>
        </div>
        <div className="stat">
          <span className="stat-label">Degree days</span>
          <span className="stat-value">{report.cooling_degree_days} CDD</span>
          <span className="stat-sub">{report.heating_degree_days} HDD</span>
        </div>
        <div className="stat">
          <span className="stat-label">Precip. variability</span>
          <span className="stat-value">{report.precipitation_variability_index.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
