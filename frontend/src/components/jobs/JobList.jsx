import { JobCard } from "./JobCard";

export const JobList = ({ jobs }) => {
  if (jobs.length === 0) {
    return <p>No jobs found.</p>;
  }

  return (
    <div className="job-list">
      {jobs.map((job) => (
        <JobCard key={job.job_id} job={job} />
      ))}
    </div>
  );
};
