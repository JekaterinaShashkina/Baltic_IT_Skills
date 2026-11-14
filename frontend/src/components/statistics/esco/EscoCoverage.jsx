export const EscoCoverage = ({ coverage }) => {
  const {
    total_skills,
    exact_matches,
    without_exact_match,
    exact_match_percent,
  } = coverage;

  return (
    <section className="dashboard-panel">
      <h2>ESCO Mapping Coverage</h2>

      <div className="esco-coverage__stats">
        <div className="esco-coverage__stat">
          <span>Total unique skills</span>
          <strong>{total_skills}</strong>
        </div>

        <div className="esco-coverage__stat">
          <span>Exact matches</span>
          <strong>{exact_matches}</strong>
        </div>

        <div className="esco-coverage__stat">
          <span>Exact match rate</span>
          <strong>{exact_match_percent}%</strong>
        </div>
      </div>

      <div
        className="esco-coverage__progress"
        role="progressbar"
        aria-label="Exact ESCO mapping coverage"
        aria-valuenow={exact_match_percent}
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className="esco-coverage__progress-fill"
          style={{ width: `${exact_match_percent}%` }}
        />
      </div>

      <p className="esco-coverage__note">
        {without_exact_match} skills have no exact match. Matching is based on
        ESCO preferred and alternative skill labels.
      </p>
    </section>
  );
};
