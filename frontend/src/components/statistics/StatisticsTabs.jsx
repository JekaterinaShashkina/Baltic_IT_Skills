export const StatisticsTabs = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: "meetfrank", label: "MeetFrank" },
    { id: "esco", label: "ESCO Statistics" },
    { id: "map", label: "Job Map " },
  ];
  return (
    <nav className="statistics-tabs" aria-label="Statistics navigation">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={`statistics-tab ${activeTab === tab.id ? "active" : ""}`}
          onClick={() => onTabChange(tab.id)}
          aria-current={activeTab === tab.id ? "page" : undefined}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
};
