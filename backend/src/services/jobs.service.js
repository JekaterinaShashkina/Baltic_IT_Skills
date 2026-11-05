const jobsRepository = require("../repositories/jobs.repository");

const getAllJobs = () => jobsRepository.getAllJobs();

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

module.exports = {
  getAllJobs,
  getJobById,
};
