import { Link, useParams } from "react-router-dom";
import { useJob } from "../hooks/useJob";

import { JobDetails } from "../components/jobs/JobDetail";
import { SkillMatcher } from "../components/jobs/SkillMatcher";

export const JobPage = () => {
  const { jobId } = useParams();
  const { job, loading, error } = useJob(jobId);

  return (
    <main className="page-content">
      <Link to="/jobs" className="back-link">
        ← Back to jobs
      </Link>

      {loading && <p>Loading job details...</p>}

      {error && <p role="alert">Error: {error}</p>}

      {!loading && !error && job && (
        <>
          <JobDetails job={job} />

          {job.skills?.length > 0 && (
            <SkillMatcher key={job.job_id} job={job} />
          )}
        </>
      )}
    </main>
  );
};
