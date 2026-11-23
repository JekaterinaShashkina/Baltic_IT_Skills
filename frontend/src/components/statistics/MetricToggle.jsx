export const MetricToggle = ({ value, onChange }) => {
  return (
    <div className="metric-toggle">
      <button
        className={value === "count" ? "active" : ""}
        onClick={() => onChange("count")}
      >
        Count
      </button>

      <button
        className={value === "percentage" ? "active" : ""}
        onClick={() => onChange("percentage")}
      >
        Percentage
      </button>
    </div>
  );
};
