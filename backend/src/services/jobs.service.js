const jobsRepository = require("../repositories/jobs.repository");

const getAllJobs = (page = 1, limit = 20, country = null) => {
  const offset = (page - 1) * limit;

  const jobs = jobsRepository.getAllJobs(limit, offset, country);
  const total = jobsRepository.countJobs(country);

  return {
    data: jobs,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
    },
  };
};

const getJobById = (jobId) => {
  const job = jobsRepository.getJobById(jobId);

  if (!job) {
    return null;
  }

  const skills = jobsRepository.getJobSkills(jobId);

  return {
    ...job,
    skills,
  };
};

const matchJobSkills = (jobId, skillIds) => {
  const job = getJobById(jobId);

  if (!job) {
    return null;
  }

  const studentSkills = new Set(skillIds);

  const matchedSkills = job.skills.filter((skill) =>
    studentSkills.has(skill.skill_id),
  );

  const missingSkills = job.skills.filter(
    (skill) => !studentSkills.has(skill.skill_id),
  );

  const totalRequired = job.skills.length;

  const matchPercentage =
    totalRequired === 0
      ? 0
      : Math.round((matchedSkills.length / totalRequired) * 100);

  return {
    jobId: job.job_id,
    totalRequired,
    matchedCount: matchedSkills.length,
    missingCount: missingSkills.length,
    matchPercentage,
    matchedSkills,
    missingSkills,
  };
};

module.exports = {
  getAllJobs,
  getJobById,
  matchJobSkills,
};
