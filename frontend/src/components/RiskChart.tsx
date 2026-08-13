import { useState } from "react";
import {
  Bar,
  CartesianGrid,
  ComposedChart,
  Legend,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { AssessmentReport } from "../types";

const MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

type TempUnit = "C" | "F";

function celsiusTo(unit: TempUnit, celsius: number): number {
  return unit === "C" ? celsius : (celsius * 9) / 5 + 32;
}

interface Props {
  report: AssessmentReport;
}

export default function RiskChart({ report }: Props) {
  const [unit, setUnit] = useState<TempUnit>("C");

  const data = MONTH_LABELS.map((month, i) => ({
    month,
    maxTemp: Math.round(celsiusTo(unit, report.monthly_max_temps_c[i]) * 10) / 10,
    meanTemp: Math.round(celsiusTo(unit, report.monthly_mean_temps_c[i]) * 10) / 10,
    precip: report.monthly_precip_mm_day[i],
  }));

  return (
    <div className="card">
      <div className="comparison-header">
        <h2>Monthly climate trend</h2>
        <div className="unit-toggle">
          <button
            type="button"
            className={unit === "C" ? "unit-button active" : "unit-button"}
            onClick={() => setUnit("C")}
          >
            °C
          </button>
          <button
            type="button"
            className={unit === "F" ? "unit-button active" : "unit-button"}
            onClick={() => setUnit("F")}
          >
            °F
          </button>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="month" />
          <YAxis yAxisId="temp" unit={`°${unit}`} width={48} />
          <YAxis yAxisId="precip" orientation="right" unit="mm/d" width={48} />
          <Tooltip />
          <Legend />
          <Bar yAxisId="precip" dataKey="precip" name="Precipitation" fill="#7fb3d5" barSize={16} />
          <Line yAxisId="temp" type="monotone" dataKey="maxTemp" name="Max temp" stroke="#e67e22" strokeWidth={2} />
          <Line
            yAxisId="temp"
            type="monotone"
            dataKey="meanTemp"
            name="Mean temp"
            stroke="#c0392b"
            strokeWidth={2}
            strokeDasharray="4 2"
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
