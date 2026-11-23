import { useState } from "react";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { CountryFilter } from "../../CountryFilter";
import { MetricToggle } from "../MetricToggle";
import { useSkillStatistics } from "../../../hooks/useSkillStatistics";

export const TopSkillsChart = () => {
  const [country, setCountry] = useState("");
  const [metric, setMetric] = useState("count");

  const { skills, loading, error } = useSkillStatistics(country);

  const topSkills = skills.slice(0, 10);

  const isPercentage = metric === "percentage";
  const dataKey = isPercentage ? "percentage" : "job_count";

  return (
    <section>
      <div className="chart-header">
        <h2>Top 10 IT skills</h2>
        <div className="chart-controls">
          <CountryFilter country={country} onCountryChange={setCountry} />

          <MetricToggle value={metric} onChange={setMetric} />
        </div>
      </div>

      {loading && <p>Loading statistics...</p>}

      {error && <p role="alert">Error: {error}</p>}

      {!loading && !error && (
        <div className="statistics-chart">
          <ResponsiveContainer width="100%" height={420}>
            <BarChart
              data={topSkills}
              layout="vertical"
              margin={{ top: 10, right: 30, left: 10, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />

              <XAxis
                type="number"
                allowDecimals={isPercentage}
                tickFormatter={(value) => (isPercentage ? `${value}%` : value)}
              />

              <YAxis
                type="category"
                dataKey="name"
                width={70}
                tick={{ fontSize: 12 }}
              />

              <Tooltip
                formatter={(value) => [
                  isPercentage ? `${value}%` : value,
                  isPercentage
                    ? "Share of job postings"
                    : "Number of job postings",
                ]}
              />

              <Bar
                dataKey={dataKey}
                name={
                  isPercentage
                    ? "Share of job postings"
                    : "Number of job postings"
                }
                fill="#38b2ac"
                barSize={18}
                radius={[0, 5, 5, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
};
