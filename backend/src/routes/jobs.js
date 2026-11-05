const express = require("express");
const db = require("../database");

const router = express.Router();

/**
 * @swagger
 * /api/jobs:
 *   get:
 *     summary: Get job vacancies
 *     tags:
 *       - Jobs
 *     responses:
 *       200:
 *         description: List of job vacancies
 */
router.get("/", (req, res) => {
  try {
    const jobs = db.prepare("SELECT * FROM job LIMIT 20").all();
    res.json(jobs);
  } catch (error) {
    console.error("Error fetching jobs:", error);
    res.status(500).json({ error: "Failed to fetch jobs" });
  }
});

module.exports = router;
