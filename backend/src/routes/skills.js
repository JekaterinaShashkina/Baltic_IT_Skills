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

/**
 * @swagger
 * /api/skills/{skillId}/occupations:
 *   get:
 *     summary: Get ESCO occupations for a specific skill
 *     tags:
 *       - Skills
 *     parameters:
 *       - in: path
 *         name: skillId
 *         required: true
 *         schema:
 *           type: integer
 *         description: The ID of the skill
 *     responses:
 *       200:
 *         description: List of ESCO occupations related to the skill
 *       400:
 *         description: Invalid skill ID
 *       500:
 *         description: Failed to fetch ESCO occupations
 */
router.get("/:skillId/occupations", skillsController.getSkillOccupations);

module.exports = router;
