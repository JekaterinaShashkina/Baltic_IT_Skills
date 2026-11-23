import { useState } from "react";
import { useSkillStatistics } from "../../hooks/useSkillStatistics";
import { CountryFilter } from "../CountryFilter";
import { TopSkillsChart } from "./meetfrank/TopSkillsChart";
import { CountryComparison } from "./meetfrank/CountryComparison";
import { StatisticsOverview } from "./meetfrank/StatisticsOverview";
import { MetricToggle } from "./MetricToggle";

export const MeetFrankDashboard = () => {
  const [country, setCountry] = useState("");
  const { skills, loading, error } = useSkillStatistics(country);
  const [metric, setMetric] = useState("count");

  return (
    <div className="statistics-dashboard">
      <section className="dashboard-panel dashboard-panel--center">
        <StatisticsOverview />
      </section>
      <section className="dashboard-panel">
        <TopSkillsChart />
      </section>

      <section className="dashboard-panel">
        <CountryComparison />
      </section>
    </div>
  );
};
