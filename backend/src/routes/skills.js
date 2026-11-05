const express = require("express");
const db = require("../database");

const router = express.Router();

/**
 * @swagger
 * /api/skills:
 *   get:
 *     summary: Get all skills
 *     tags:
 *       - Skills
 *     responses:
 *       200:
 *         description: List of skills
 */
router.get("/", (req, res) => {
  try {
    const skills = db
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

    res.json(skills);
  } catch (error) {
    console.error("Error fetching skills:", error);
    res.status(500).json({ error: "Failed to fetch skills" });
  }
});

/**
 * @swagger
 * /api/skills/statistics:
 *   get:
 *     summary: Get skill demand statistics
 *     tags:
 *       - Skills
 *     parameters:
 *       - in: query
 *         name: country
 *         required: false
 *         schema:
 *           type: string
 *           enum: [estonia, latvia, lithuania]
 *         description: Filter vacancies by country
 *     responses:
 *       200:
 *         description: Number of vacancies requiring each skill
 */

router.get("/statistics", (req, res) => {
  try {
    const { country } = req.query;

    const statistics = db
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

    res.json(statistics);
  } catch (error) {
    console.error("Error fetching skill statistics:", error);
    res.status(500).json({ error: "Failed to fetch skill statistics" });
  }
});

module.exports = router;
