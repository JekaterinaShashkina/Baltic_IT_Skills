import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export const TopSkillsChart = ({ skills }) => {
  const topSkills = skills.slice(0, 10);

  return (
    <section className="statistics-chart">
      <ResponsiveContainer width="100%" height={420}>
        <BarChart
          data={topSkills}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 45, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />

          <XAxis type="number" allowDecimals={false} />

          <YAxis
            type="category"
            dataKey="name"
            width={150}
            tick={{ fontSize: 12 }}
          />

          <Tooltip />

          <Bar
            dataKey="job_count"
            name="Number of jobs"
            fill="#38b2ac"
            radius={[0, 5, 5, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </section>
  );
};
