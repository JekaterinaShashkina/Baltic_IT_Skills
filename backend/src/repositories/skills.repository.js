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

const getSkillOccupations = (skillId) => {
  return db
    .prepare(
      `
      SELECT
        o.occupation_uri,
        o.title AS occupation_title,
        o.isco_code,
        eso.relation_type,
        es.title AS esco_skill_title
      FROM skill s
      JOIN skill_mapping sm
        ON sm.skill_id = s.skill_id
      JOIN esco_skill es
        ON es.esco_uri = sm.esco_uri
      JOIN esco_skill_occupation eso
        ON eso.esco_uri = es.esco_uri
      JOIN occupation o
        ON o.occupation_uri = eso.occupation_uri
      WHERE s.skill_id = ?
        AND sm.status = 'exact'
        AND o.ict_category = 'ICT'
      ORDER BY
        CASE eso.relation_type
          WHEN 'essential' THEN 0
          WHEN 'optional' THEN 1
          ELSE 2
        END,
        o.title
      `,
    )
    .all(skillId);
};

module.exports = {
  getAllSkills,
  getSkillStatistics,
  getSkillOccupations,
};
