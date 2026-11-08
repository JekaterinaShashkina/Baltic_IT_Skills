import { SeniorityBadge } from "./SeniorityBadge";

export const JobDetails = ({ job }) => {
  return (
    <section className="job-details">
      <h1>{job.title}</h1>
      <SeniorityBadge seniorities={job.seniorities} />

      <div className="job-info">
        <p>
          <span className="job-info__label">Company:</span>
          <span>{job.company || "Not specified"}</span>
        </p>
        <p>
          <span className="job-info__label">Speciality:</span>
          <span>{job.speciality || "Not specified"}</span>
        </p>
        <p>
          <span className="job-info__label">Employment:</span>
          <span>{job.employment_type || "Not specified"}</span>
        </p>
        <p>
          <span className="job-info__label">Remote work:</span>
          <span>{job.remote_type || "Not specified"}</span>
        </p>
      </div>

      <h2>Required skills</h2>

      {job.skills?.length > 0 ? (
        <div className="skill-list">
          {job.skills.map((skill) => (
            <span key={skill.skill_id} className="skill-tag">
              {skill.name}
            </span>
          ))}
        </div>
      ) : (
        <p>No skills listed for this job.</p>
      )}

      {job.apply_url && (
        <a
          href={job.apply_url}
          target="_blank"
          rel="noopener noreferrer"
          className="job-external-link"
        >
          View original job ↗
        </a>
      )}
    </section>
  );
};
