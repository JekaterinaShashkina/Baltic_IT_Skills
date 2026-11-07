const jobsService = require("../services/jobs.service");
const logger = require("../utils/logger");

const getAllJobs = (req, res) => {
  try {
    const page = Number(req.query.page ?? 1);
    const limit = Number(req.query.limit ?? 20);
    const country = req.query.country ?? null;

    const allowedCountries = ["estonia", "latvia", "lithuania"];

    if (
      !Number.isInteger(page) ||
      page < 1 ||
      !Number.isInteger(limit) ||
      limit < 1 ||
      limit > 100
    ) {
      return res.status(400).json({
        error:
          "page must be a positive integer and limit must be between 1 and 100",
      });
    }

    if (
      country !== null &&
      (typeof country !== "string" ||
        !allowedCountries.includes(country.toLowerCase()))
    ) {
      return res.status(400).json({
        error: "Invalid country",
      });
    }

    const result = jobsService.getAllJobs(page, limit, country);

    res.json(result);
  } catch (error) {
    logger.error("Error fetching jobs", { error });

    res.status(500).json({
      error: "Failed to fetch jobs",
    });
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

const matchJobSkills = (req, res) => {
  try {
    const { skillIds } = req.body;

    if (
      !Array.isArray(skillIds) ||
      !skillIds.every((id) => Number.isInteger(id))
    ) {
      return res.status(400).json({
        error: "skillIds must be an array of integers",
      });
    }

    const result = jobsService.matchJobSkills(req.params.jobId, skillIds);

    if (!result) {
      return res.status(404).json({
        error: "Job not found",
      });
    }

    res.json(result);
  } catch (error) {
    logger.error("Error matching job skills", { error });

    res.status(500).json({
      error: "Failed to match job skills",
    });
  }
};

module.exports = {
  getAllJobs,
  getJobById,
  matchJobSkills,
};
