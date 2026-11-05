const db = require("../database");

const getAllJobs = () => db.prepare("SELECT * FROM job LIMIT 20").all();

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
  getJobById,
  getJobSkills,
};
