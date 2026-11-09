import { useDatasetOverview } from "../../hooks/useDatasetOverview";

export const StatisticsOverview = () => {
  const { counts, loading, error } = useDatasetOverview();

  if (loading) return <p>Loading overview...</p>;
  if (error) return <p role="alert">Error: {error}</p>;

  const total = counts.estonia + counts.latvia + counts.lithuania;

  return (
    <section>
      <h2>Dataset overview</h2>
      <p>Overview of collected IT job postings across the Baltic countries.</p>

      <div className="overview-grid">
        <div className="overview-card">
          <span>Total job postings</span>
          <strong>{total}</strong>
        </div>

        <div className="overview-card">
          <span>Countries</span>
          <strong>3</strong>
        </div>
      </div>

      <h3>Job postings by country</h3>

      <div className="overview-grid">
        {Object.entries(counts).map(([country, count]) => (
          <div className="overview-card" key={country}>
            <span>{country.charAt(0).toUpperCase() + country.slice(1)}</span>
            <strong>{count}</strong>
          </div>
        ))}
      </div>
    </section>
  );
};
