const jobsService = require("../services/jobs.service");
const logger = require("../utils/logger");

const getAllJobs = (req, res) => {
  try {
    const jobs = jobsService.getAllJobs();
    res.json(jobs);
  } catch (error) {
    logger.error("Error fetching jobs:", { error });
    res.status(500).json({ error: "Failed to fetch jobs" });
  }
};

const getJobById = (req, res) => {
  try {
    const job = jobsService.getJobById(req.params.jobId);
    if (!job) {
      return res.status(404).json({
        error: "Job not found",
      });
    }
    res.json(job);
  } catch (error) {
    logger.error("Error fetching job:", { error });
    res.status(500).json({
      error: "Failed to fetch job",
    });
  }
};

module.exports = {
  getAllJobs,
  getJobById,
};
