const db = require("../database");

const getMappingCoverage = () => {
  return db
    .prepare(
      `
    SELECT
      COUNT(DISTINCT s.skill_id) AS total_skills,
      COUNT(DISTINCT CASE
        WHEN sm.status = 'exact' THEN s.skill_id
      END) AS exact_matches,
      COUNT(DISTINCT s.skill_id)
        - COUNT(DISTINCT CASE
            WHEN sm.status = 'exact' THEN s.skill_id
          END) AS without_exact_match,
      ROUND(
        100.0 * COUNT(DISTINCT CASE
          WHEN sm.status = 'exact' THEN s.skill_id
        END) / NULLIF(COUNT(DISTINCT s.skill_id), 0),
        1
      ) AS exact_match_percent
    FROM skill s
    JOIN job_skill js ON js.skill_id = s.skill_id
    LEFT JOIN skill_mapping sm ON sm.skill_id = s.skill_id
  `,
    )
    .get();
};

const getOccupationRelations = () => {
  return db
    .prepare(
      `
      SELECT
        eso.relation_type,
        COUNT(DISTINCT sm.esco_uri || '|' || eso.occupation_uri)
          AS total_relations,
        COUNT(DISTINCT sm.skill_id) AS unique_skills,
        COUNT(DISTINCT eso.occupation_uri) AS unique_occupations
      FROM skill_mapping sm
      JOIN esco_skill_occupation eso
        ON eso.esco_uri = sm.esco_uri
      JOIN occupation o
        ON o.occupation_uri = eso.occupation_uri
      WHERE sm.status = 'exact'
        AND o.ict_category = 'ICT'
        AND EXISTS (
          SELECT 1
          FROM job_skill js
          WHERE js.skill_id = sm.skill_id
        )
      GROUP BY eso.relation_type
      ORDER BY eso.relation_type
    `,
    )
    .all();
};

const getCountryCoverage = () => {
  return db
    .prepare(
      `
      SELECT
        jc.country,
        COUNT(DISTINCT jc.job_id) AS total_jobs,
        COUNT(DISTINCT js.skill_id) AS total_skills,
        COUNT(DISTINCT CASE
          WHEN sm.status = 'exact' THEN js.skill_id
        END) AS exact_matches,
        ROUND(
          100.0 * COUNT(DISTINCT CASE
            WHEN sm.status = 'exact' THEN js.skill_id
          END) / NULLIF(COUNT(DISTINCT js.skill_id), 0),
          1
        ) AS exact_match_percent
      FROM job_countries jc
      JOIN job_skill js ON js.job_id = jc.job_id
      LEFT JOIN skill_mapping sm ON sm.skill_id = js.skill_id
      GROUP BY jc.country
      ORDER BY jc.country
      `,
    )
    .all();
};

const getAnalysis = () => {
  return {
    coverage: getMappingCoverage(),
    relations: getOccupationRelations(),
    countryCoverage: getCountryCoverage(),
  };
};

module.exports = {
  getMappingCoverage,
  getOccupationRelations,
  getAnalysis,
  getCountryCoverage,
};
