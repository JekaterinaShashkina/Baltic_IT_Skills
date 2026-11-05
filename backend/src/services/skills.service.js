const skillsRepository = require("../repositories/skills.repository");

const getAllSkills = () => skillsRepository.getAllSkills();

const getSkillStatistics = (country) =>
  skillsRepository.getSkillStatistics(country);

module.exports = {
  getAllSkills,
  getSkillStatistics,
};
