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

import { useCountryComparison } from "../../hooks/useCountryComparison";
import { prepareCountryComparison } from "../../utils/prepareCountryComparison";

export const CountryComparison = () => {
  const { data, loading, error } = useCountryComparison();

  if (loading) return <p>Loading comparison...</p>;
  if (error) return <p role="alert">Error: {error}</p>;

  const chartData = prepareCountryComparison(data);

  return (
    <section>
      <h2>Country comparison</h2>
      <p>Top 10 IT skills across Estonia, Latvia and Lithuania.</p>

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
              domain={[0, 50]}
              ticks={[0, 10, 20, 30, 40, 50]}
              allowDecimals={false}
              label={{
                value: "Number of job postings",
                angle: -90,
                position: "insideLeft",
                style: { textAnchor: "middle", fontSize: 12 },
              }}
            />

            <Tooltip />
            <Legend verticalAlign="top" height={36} />

            <Bar
              dataKey="estonia"
              name="Estonia"
              fill="#16A34A"
              radius={[4, 4, 0, 0]}
              maxBarSize={12}
            />
            <Bar
              dataKey="latvia"
              name="Latvia"
              fill="#3B82F6"
              radius={[4, 4, 0, 0]}
              maxBarSize={12}
            />
            <Bar
              dataKey="lithuania"
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
