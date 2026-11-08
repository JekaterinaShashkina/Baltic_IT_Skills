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
      s.name
    FROM job_skill js
    JOIN skill s ON s.skill_id = js.skill_id
    WHERE js.job_id = ?
    ORDER BY s.name
  `,
    )
    .all(jobId);
};

module.exports = {
  getAllJobs,
  countJobs,
  getJobById,
  getJobSkills,
};
