const express = require("express");
const skillsController = require("../controllers/skills.controller");

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
router.get("/", skillsController.getAllSkills);

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

router.get("/statistics", skillsController.getSkillStatistics);

module.exports = router;
