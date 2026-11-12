const skillsRepository = require("../repositories/skills.repository");

const getAllSkills = () => skillsRepository.getAllSkills();

const getSkillStatistics = (country) =>
  skillsRepository.getSkillStatistics(country);

const getSkillOccupations = (skillId) =>
  skillsRepository.getSkillOccupations(skillId);

module.exports = {
  getAllSkills,
  getSkillStatistics,
  getSkillOccupations,
};
