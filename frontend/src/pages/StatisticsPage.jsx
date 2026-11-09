import { useState } from "react";
import { useSkillStatistics } from "../hooks/useSkillStatistics";
import { CountryFilter } from "../components/CountryFilter";
import { TopSkillsChart } from "../components/statistics/TopSkillsChart";
import { StatisticsTabs } from "../components/statistics/StatisticsTabs";
import { CountryComparison } from "../components/statistics/CountryComparison";
import { StatisticsOverview } from "../components/statistics/StatisticsOverview";

export const StatisticsPage = () => {
  const [country, setCountry] = useState("");
  const [activeTab, setActiveTab] = useState("overview");
  const { skills, loading, error } = useSkillStatistics(country);

  return (
    <main className="page-content">
      <div className="page-intro">
        <h1>Statistics</h1>
        <p>
          Explore the demand for IT skills across Estonia, Latvia and Lithuania.
        </p>
        <StatisticsTabs activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {activeTab === "overview" && <StatisticsOverview />}

      {activeTab === "comparison" && <CountryComparison />}
      {activeTab === "top" && (
        <>
          <div className="jobs-header">
            <h2>Top 10 IT skills</h2>
            <CountryFilter country={country} onCountryChange={setCountry} />
          </div>

          {loading && <p>Loading statistics...</p>}
          {error && <p role="alert">Error: {error}</p>}

          {!loading && !error && <TopSkillsChart skills={skills} />}
        </>
      )}
    </main>
  );
};
