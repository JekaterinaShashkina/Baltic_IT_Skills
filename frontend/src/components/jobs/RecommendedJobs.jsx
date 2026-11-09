import { Link } from "react-router-dom";

export const RecommendedJobs = ({ jobs }) => {
  return (
    <section className="recommended-jobs">
      <h3>Other matching jobs</h3>
      <p>Other job postings matching your selected skills.</p>

      {jobs.length === 0 ? (
        <p>No matching jobs found.</p>
      ) : (
        <div className="recommended-jobs-list">
          {jobs.map((job) => (
            <Link
              key={job.jobId}
              to={`/jobs/${job.jobId}`}
              className="recommended-job"
            >
              <div className="recommended-job-info">
                <strong>{job.title}</strong>
                <span>{job.company}</span>
                <small>
                  {job.matchedCount} of {job.totalRequired} skills matched
                </small>
              </div>

              <span className="recommended-job-match">
                {job.matchPercentage}%
              </span>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
};
