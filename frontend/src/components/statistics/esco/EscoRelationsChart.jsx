import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

const COLORS = {
  essential: "#0d9488",
  optional: "#94a3b8",
};

export const EscoRelationsChart = ({ relations }) => {
  const data = relations.map((item) => ({
    name: item.relation_type,
    value: item.total_relations,
    uniqueSkills: item.unique_skills,
    uniqueOccupations: item.unique_occupations,
  }));

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <section className="dashboard-panel">
      <h2>ESCO Relations with ICT Occupations</h2>

      <div className="esco-relations__chart">
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              innerRadius={75}
              outerRadius={105}
              paddingAngle={3}
            >
              {data.map((item) => (
                <Cell key={item.name} fill={COLORS[item.name] ?? "#64748b"} />
              ))}
            </Pie>

            <Tooltip
              formatter={(value, name) => [`${value} relations`, name]}
            />

            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="esco-relations__summary">
        {data.map((item) => (
          <div key={item.name}>
            <strong>{item.value} </strong>
            <span>
              {item.name} ({total ? ((item.value / total) * 100).toFixed(1) : 0}
              %)
            </span>
          </div>
        ))}
      </div>

      <p className="esco-coverage__note">
        Essential and optional describe ESCO skill–occupation relationships, not
        employers' requirements.
      </p>
    </section>
  );
};
