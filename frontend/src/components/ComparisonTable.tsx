import type { AssessmentReport, Site } from "../types";

export interface ComparisonItem {
  site: Site;
  report: AssessmentReport;
}

interface Props {
  items: ComparisonItem[];
  onClose: () => void;
}

interface RowProps {
  label: string;
  values: (string | number)[];
}

function Row({ label, values }: RowProps) {
  return (
    <tr>
      <th scope="row">{label}</th>
      {values.map((value, i) => (
        <td key={i}>{value}</td>
      ))}
    </tr>
  );
}

export default function ComparisonTable({ items, onClose }: Props) {
  const hasSavings = items.some((item) => item.report.estimated_annual_savings !== null);

  return (
    <div className="card">
      <div className="comparison-header">
        <h2>Compare sites</h2>
        <button type="button" className="text-button" onClick={onClose}>
          ← Back to single view
        </button>
      </div>

      <div className="comparison-scroll">
        <table className="comparison-table">
          <thead>
            <tr>
              <th scope="col"></th>
              {items.map(({ site }) => (
                <th scope="col" key={site.id}>
                  {site.name}
                  <div className="muted">
                    {site.lat.toFixed(2)}, {site.lon.toFixed(2)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <Row
              label="Solar output (kWh/yr)"
              values={items.map((i) => i.report.solar_annual_kwh.toLocaleString())}
            />
            <Row
              label="Wind output (kWh/yr)"
              values={items.map((i) => i.report.wind_annual_kwh.toLocaleString())}
            />
            <Row label="Wind class" values={items.map((i) => i.report.wind_class)} />
            <Row
              label="Heat stress (days/yr)"
              values={items.map((i) => i.report.heat_stress_days_per_year)}
            />
            <Row
              label="Cooling degree days"
              values={items.map((i) => i.report.cooling_degree_days)}
            />
            <Row
              label="Heating degree days"
              values={items.map((i) => i.report.heating_degree_days)}
            />
            <Row
              label="Precip. variability"
              values={items.map((i) => i.report.precipitation_variability_index.toFixed(2))}
            />
            <Row
              label="CO₂ avoided (kg/yr)"
              values={items.map((i) => i.report.annual_co2_avoided_kg.toLocaleString())}
            />
            {hasSavings && (
              <Row
                label="Est. savings / yr"
                values={items.map((i) =>
                  i.report.estimated_annual_savings !== null
                    ? `${i.report.currency_symbol}${i.report.estimated_annual_savings.toLocaleString()}`
                    : "—",
                )}
              />
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
