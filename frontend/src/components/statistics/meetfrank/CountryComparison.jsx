import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { MetricToggle } from "../MetricToggle";

import { useCountryComparison } from "../../../hooks/useCountryComparison";
import { prepareCountryComparison } from "../../../utils/prepareCountryComparison";

export const CountryComparison = () => {
  const { data, loading, error } = useCountryComparison();
  const [metric, setMetric] = useState("count");

  if (loading) return <p>Loading comparison...</p>;
  if (error) return <p role="alert">Error: {error}</p>;

  const chartData = prepareCountryComparison(data, metric);

  const isPercentage = metric === "percentage";

  return (
    <section>
      <div className="chart-header">
        <h2>Country comparison</h2>
        <div className="chart-controls">
          <MetricToggle value={metric} onChange={setMetric} />
        </div>
      </div>

      <div className="statistics-chart">
        <ResponsiveContainer width="100%" height={420}>
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 20, left: 20, bottom: 35 }}
            barCategoryGap="12%"
            barGap={2}
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="skill"
              angle={-35}
              textAnchor="end"
              interval={0}
              height={60}
              tick={{ fontSize: 12 }}
            />

            <YAxis
              domain={isPercentage ? [0, 100] : ["auto", "auto"]}
              allowDecimals={isPercentage}
              tickFormatter={(value) => (isPercentage ? `${value}%` : value)}
              label={{
                value: isPercentage
                  ? "Share of job postings"
                  : "Number of job postings",
                angle: -90,
                position: "insideLeft",
                style: { textAnchor: "middle", fontSize: 12 },
              }}
            />

            <Tooltip
              formatter={(value) => [isPercentage ? `${value}%` : value]}
            />
            <Legend verticalAlign="top" height={36} />

            <Bar
              dataKey={isPercentage ? "estonia_percentage" : "estonia"}
              name="Estonia"
              fill="#16A34A"
              radius={[4, 4, 0, 0]}
              maxBarSize={12}
            />
            <Bar
              dataKey={isPercentage ? "latvia_percentage" : "latvia"}
              name="Latvia"
              fill="#3B82F6"
              radius={[4, 4, 0, 0]}
              maxBarSize={12}
            />
            <Bar
              dataKey={isPercentage ? "lithuania_percentage" : "lithuania"}
              name="Lithuania"
              fill="#b91c1c"
              radius={[4, 4, 0, 0]}
              maxBarSize={12}
            />
          </BarChart>
        </ResponsiveContainer>{" "}
      </div>
    </section>
  );
};
