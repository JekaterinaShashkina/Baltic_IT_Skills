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

module.exports = {
  getAllSkills,
  getSkillStatistics,
};
