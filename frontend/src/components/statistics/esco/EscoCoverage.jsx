export const EscoCoverage = ({
  coverage,
  exact_examples,
  no_match_examples,
  occupation_summary,
}) => {
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
        <div className="overview-card">
          <span>Total unique skills</span>
          <strong>{total_skills}</strong>
        </div>

        <div className="overview-card">
          <span>Exact matches</span>
          <strong>{exact_matches}</strong>
        </div>

        <div className="overview-card">
          <span>Exact match rate</span>
          <strong>{exact_match_percent}%</strong>
        </div>

        <div className="overview-card">
          <span>ICT occupations</span>
          <strong>{occupation_summary?.unique_occupations ?? 0}</strong>
        </div>

        <div className="overview-card">
          <span>Skill-occupation relations</span>
          <strong>{occupation_summary?.total_relations ?? 0}</strong>
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

      <div className="esco-examples">
        <div className="esco-example-card">
          <h3>Most frequent exact matches</h3>

          {exact_examples?.map((skill) => (
            <div className="esco-example-row" key={skill.skill_id}>
              <div>
                <strong>{skill.name}</strong>

                {skill.name !== skill.esco_name && (
                  <span className="esco-match-label">
                    {" → "}
                    {skill.esco_name}
                  </span>
                )}
              </div>

              <span className="esco-job-count">{skill.job_count} jobs</span>
            </div>
          ))}
        </div>

        <div className="esco-example-card">
          <h3>Frequent skills with no exact match</h3>

          {no_match_examples?.map((skill) => (
            <div className="esco-example-row" key={skill.skill_id}>
              <strong>{skill.name}</strong>

              <span className="esco-job-count">{skill.job_count} jobs</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
