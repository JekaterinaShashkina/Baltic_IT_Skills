const db = require("../database");

const getAllSkills = () => {
  return db
    .prepare(
      `
    SELECT
      s.skill_id,
      s.name,
      e.title AS esco_title,
      m.status AS mapping_status
    FROM skill s
    LEFT JOIN skill_mapping m ON s.skill_id = m.skill_id
    LEFT JOIN esco_skill e ON m.esco_uri = e.esco_uri
    ORDER BY s.name
  `,
    )
    .all();
};

const getSkillStatistics = (country) => {
  return db
    .prepare(
      `
    SELECT
      s.skill_id,
      s.name,
      COUNT(DISTINCT js.job_id) AS job_count
    FROM skill s
    LEFT JOIN job_skill js ON s.skill_id = js.skill_id
    LEFT JOIN job_countries jc ON js.job_id = jc.job_id
    WHERE (? IS NULL OR LOWER(jc.country) = LOWER(?))
    GROUP BY s.skill_id, s.name
    HAVING job_count > 0
    ORDER BY job_count DESC, s.name
  `,
    )
    .all(country || null, country || null);
};

module.exports = {
  getAllSkills,
  getSkillStatistics,
};
