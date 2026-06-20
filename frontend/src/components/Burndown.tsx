import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { BurndownPoint } from "../types";

interface Props {
  data: BurndownPoint[];
}

export function Burndown({ data }: Props) {
  // Linia idealna: od pierwszego 'remaining' liniowo do zera.
  const start = data.length > 0 ? data[0].remaining : 0;
  const step = data.length > 1 ? start / (data.length - 1) : 0;
  const chartData = data.map((p, i) => ({
    date: p.date.slice(5), // MM-DD
    actual: p.remaining,
    ideal: Math.max(Math.round((start - step * i) * 10) / 10, 0),
  }));

  return (
    <div className="panel">
      <div className="panel-head">
        <span>◷ BURNDOWN</span>
        <span className="legend">IDEAL ┄┄ · ACTUAL ━━</span>
      </div>
      {chartData.length === 0 ? (
        <div className="chat-empty">Brak danych — zamknij task, żeby zacząć log.</div>
      ) : (
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={chartData} margin={{ top: 6, right: 10, bottom: 0, left: -20 }}>
            <CartesianGrid stroke="#3a2f22" strokeOpacity={0.4} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 9, fontFamily: "monospace", fill: "#7a6a52" }}
              stroke="#3a2f22"
            />
            <YAxis
              tick={{ fontSize: 9, fontFamily: "monospace", fill: "#7a6a52" }}
              stroke="#3a2f22"
              allowDecimals={false}
            />
            <Tooltip
              contentStyle={{
                background: "#1a1410",
                border: "1px solid #5a4a32",
                borderRadius: 3,
                fontFamily: "monospace",
                fontSize: 11,
                color: "#e8d4a8",
              }}
            />
            <Line
              type="linear"
              dataKey="ideal"
              stroke="#7a6a52"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#ffb000"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
