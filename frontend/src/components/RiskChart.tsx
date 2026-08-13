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

interface Props {
  report: AssessmentReport;
}

export default function RiskChart({ report }: Props) {
  const data = MONTH_LABELS.map((month, i) => ({
    month,
    maxTemp: report.monthly_max_temps_c[i],
    meanTemp: report.monthly_mean_temps_c[i],
    precip: report.monthly_precip_mm_day[i],
  }));

  return (
    <div className="card">
      <h2>Monthly climate trend</h2>
      <ResponsiveContainer width="100%" height={280}>
        <ComposedChart data={data} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis dataKey="month" />
          <YAxis yAxisId="temp" unit="°C" width={48} />
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
