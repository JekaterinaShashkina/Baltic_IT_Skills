const skillsService = require("../services/skills.service");
const logger = require("../utils/logger");

const getAllSkills = (req, res) => {
  try {
    const skills = skillsService.getAllSkills();
    res.json(skills);
  } catch (error) {
    logger.error("Error fetching skills:", { error });
    res.status(500).json({ error: "Failed to fetch skills" });
  }
};

const getSkillStatistics = (req, res) => {
  try {
    const { country } = req.query;
    const statistics = skillsService.getSkillStatistics(country);

    res.json(statistics);
  } catch (error) {
    logger.error("Error fetching skill statistics:", { error });
    res.status(500).json({
      error: "Failed to fetch skill statistics",
    });
  }
};

const getSkillOccupations = (req, res) => {
  try {
    const skillId = Number(req.params.skillId);

    if (!Number.isSafeInteger(skillId) || skillId <= 0) {
      return res.status(400).json({
        error: "Invalid skill ID",
      });
    }

    const occupations = skillsService.getSkillOccupations(skillId);

    res.json(occupations);
  } catch (error) {
    logger.error("Error fetching ESCO occupations:", {
      message: error.message,
      stack: error.stack,
    });
    res.status(500).json({
      error: "Failed to fetch ESCO occupations",
    });
  }
};

module.exports = {
  getAllSkills,
  getSkillStatistics,
  getSkillOccupations,
};
