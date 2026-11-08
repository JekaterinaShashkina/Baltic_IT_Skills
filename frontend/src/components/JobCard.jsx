import { Link } from "react-router-dom";
import { SeniorityBadge } from "./SeniorityBadge";

export const JobCard = ({ job }) => {
  return (
    <article className="job-card">
      <Link to={`/jobs/${job.job_id}`} className="job-card__link">
        <h3>{job.title}</h3>
        <SeniorityBadge seniorities={job.seniorities} />
      </Link>
    </article>
  );
};
