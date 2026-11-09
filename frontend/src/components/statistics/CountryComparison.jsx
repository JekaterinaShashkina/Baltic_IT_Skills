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
        <ResponsiveContainer width="100%" height={500}>
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 10, bottom: 85 }}
            barCategoryGap="20%"
          >
            <CartesianGrid strokeDasharray="3 3" vertical={false} />

            <XAxis
              dataKey="skill"
              angle={-35}
              textAnchor="end"
              interval={0}
              height={110}
              tick={{ fontSize: 12 }}
            />

            <YAxis
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
            />
            <Bar
              dataKey="latvia"
              name="Latvia"
              fill="#3B82F6"
              radius={[4, 4, 0, 0]}
            />
            <Bar
              dataKey="lithuania"
              name="Lithuania"
              fill="#F59E0B"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>{" "}
      </div>
    </section>
  );
};
