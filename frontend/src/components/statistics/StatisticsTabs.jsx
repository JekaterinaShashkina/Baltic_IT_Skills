const tabs = [
  { id: "overview", label: "Overview" },
  { id: "top", label: "Top 10 skills" },
  { id: "comparison", label: "Country comparison" },
];

export const StatisticsTabs = ({ activeTab, onTabChange }) => {
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
