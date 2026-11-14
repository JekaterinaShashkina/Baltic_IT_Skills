import { useState } from "react";
import { StatisticsTabs } from "../components/statistics/StatisticsTabs";
import { MeetFrankDashboard } from "../components/statistics/MeetFrankDashboard";
import { EscoDashboard } from "../components/statistics/EscoDashboard";
// import { MapDashboard } from "../components/statistics/MapDashboard";

export const StatisticsPage = () => {
  const [activeTab, setActiveTab] = useState("meetfrank");

  return (
    <main className="page-content">
      <div className="page-intro">
        <h1>Statistics</h1>
        <p>
          Explore the demand for IT skills across Estonia, Latvia and Lithuania.
        </p>
        <StatisticsTabs activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      {activeTab === "meetfrank" && <MeetFrankDashboard />}

      {activeTab === "esco" && <EscoDashboard />}
      {/* {activeTab === "map" && <MapDashboard />} */}
    </main>
  );
};
