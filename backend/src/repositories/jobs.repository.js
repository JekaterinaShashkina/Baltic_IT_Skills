const db = require("../database");

const getAllJobs = (limit, offset, country) => {
  return db
    .prepare(
      `
    SELECT j.*
    FROM job j
    WHERE (
      ? IS NULL
      OR EXISTS (
        SELECT 1
        FROM job_countries jc
        WHERE jc.job_id = j.job_id
          AND LOWER(jc.country) = LOWER(?)
      )
    )
    ORDER BY
        j.published_at DESC,
        j.job_id ASC
    LIMIT ? OFFSET ?
  `,
    )
    .all(country, country, limit, offset);
};

const countJobs = (country) => {
  return db
    .prepare(
      `
    SELECT COUNT(*) AS total
    FROM job j
    WHERE (
      ? IS NULL
      OR EXISTS (
        SELECT 1
        FROM job_countries jc
        WHERE jc.job_id = j.job_id
          AND LOWER(jc.country) = LOWER(?)
      )
    )
  `,
    )
    .get(country, country).total;
};

const getJobById = (jobId) =>
  db.prepare("SELECT * FROM job WHERE job_id = ?").get(jobId);

const getJobSkills = (jobId) => {
  return db
    .prepare(
      `
      SELECT
        s.skill_id,
        s.name,
        sm.status AS mapping_status,
        es.title AS esco_title
      FROM job_skill AS js
      JOIN skill AS s
        ON s.skill_id = js.skill_id
      LEFT JOIN skill_mapping AS sm
        ON sm.skill_id = s.skill_id
      LEFT JOIN esco_skill AS es
        ON es.esco_uri = sm.esco_uri
      WHERE js.job_id = ?
      ORDER BY s.name
    `,
    )
    .all(jobId);
};

const getJobsBySkills = (skillIds, excludeJobId = null) => {
  if (!skillIds.length) {
    return [];
  }

  const placeholders = skillIds.map(() => "?").join(", ");

  return db
    .prepare(
      `
      SELECT DISTINCT
        j.job_id,
        j.title,
        j.company
      FROM job j
      JOIN job_skill js ON js.job_id = j.job_id
      WHERE js.skill_id IN (${placeholders})
        AND (? IS NULL OR j.job_id != ?)
      `,
    )
    .all(...skillIds, excludeJobId, excludeJobId);
};

const getJobsForMap = () => {
  return db
    .prepare(
      `
    SELECT
      j.job_id,
      j.title,
      j.location,
      GROUP_CONCAT(DISTINCT jc.country) AS source_countries
    FROM job AS j
    LEFT JOIN job_countries AS jc
      ON jc.job_id = j.job_id
    WHERE j.location IS NOT NULL
      AND TRIM(j.location) <> ''
    GROUP BY j.job_id, j.title, j.location
  `,
    )
    .all();
};

const getJobLocations = () => {
  return db
    .prepare(
      `
      SELECT city, country, latitude, longitude, status
      FROM job_locations
      WHERE latitude IS NOT NULL
        AND longitude IS NOT NULL
    `,
    )
    .all();
};

module.exports = {
  getAllJobs,
  countJobs,
  getJobById,
  getJobSkills,
  getJobsBySkills,
  getJobsForMap,
  getJobLocations,
};
