import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const COUNTRY_NAMES = {
  estonia: "Estonia",
  latvia: "Latvia",
  lithuania: "Lithuania",
};

export const EscoCountryComparison = ({ countries }) => {
  const data = countries.map((item) => ({
    ...item,
    name: COUNTRY_NAMES[item.country] ?? item.country,
  }));

  return (
    <section className="dashboard-panel">
      <h2>ESCO Mapping by Country</h2>

      <div className="statistics-chart">
        <ResponsiveContainer width="100%" height={260}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 10, right: 40, left: 10, bottom: 10 }}
          >
            <CartesianGrid strokeDasharray="3 3" horizontal={false} />

            <XAxis
              type="number"
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
            />

            <YAxis
              type="category"
              dataKey="name"
              width={75}
              tick={{ fontSize: 12 }}
            />

            <Tooltip formatter={(value) => [`${value}%`, "Exact match rate"]} />

            <Bar
              dataKey="exact_match_percent"
              name="Exact match rate"
              fill="#38b2ac"
              barSize={22}
              radius={[0, 5, 5, 0]}
              label={{
                position: "right",
                formatter: (value) => `${value}%`,
              }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="esco-coverage__note">
        Percentage of unique skills with exact ESCO matches in each country's
        MeetFrank job postings.
      </p>
    </section>
  );
};
