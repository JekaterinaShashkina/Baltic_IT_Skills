import { useState } from "react";
import { useSkillStatistics } from "../../hooks/useSkillStatistics";
import { CountryFilter } from "../CountryFilter";
import { TopSkillsChart } from "./meetfrank/TopSkillsChart";
import { CountryComparison } from "./meetfrank/CountryComparison";
import { StatisticsOverview } from "./meetfrank/StatisticsOverview";

export const MeetFrankDashboard = () => {
  const [country, setCountry] = useState("");
  const { skills, loading, error } = useSkillStatistics(country);

  return (
    <div className="statistics-dashboard">
      <section className="dashboard-panel">
        <div className="jobs-header">
          <h2>Top 10 IT skills</h2>
          <CountryFilter country={country} onCountryChange={setCountry} />
        </div>

        {loading && <p>Loading statistics...</p>}
        {error && <p role="alert">Error: {error}</p>}
        {!loading && !error && <TopSkillsChart skills={skills} />}
      </section>

      <section className="dashboard-panel">
        <CountryComparison />
      </section>

      <section className="dashboard-panel dashboard-panel--center">
        <StatisticsOverview />
      </section>
    </div>
  );
};
