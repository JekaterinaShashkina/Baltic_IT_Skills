const express = require("express");
const jobsController = require("../controllers/jobs.controller");

const router = express.Router();

/**
 * @swagger
 * /api/jobs:
 *   get:
 *     summary: Get paginated job listings
 *     tags:
 *       - Jobs
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           default: 1
 *           minimum: 1
 *         description: Page number
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           default: 20
 *           minimum: 1
 *           maximum: 100
 *         description: Number of jobs per page
 *       - in: query
 *         name: country
 *         schema:
 *           type: string
 *           enum: [estonia, latvia, lithuania]
 *         description: Filter jobs by country
 *     responses:
 *       200:
 *         description: Paginated job listings
 *       400:
 *         description: Invalid query parameters
 */
router.get("/", jobsController.getAllJobs);

/**
 * @swagger
 * /api/jobs/{jobId}:
 *   get:
 *     summary: Get job details with required skills
 *     tags:
 *       - Jobs
 *     parameters:
 *       - in: path
 *         name: jobId
 *         required: true
 *         schema:
 *           type: string
 *         description: MeetFrank job identifier
 *     responses:
 *       200:
 *         description: Job details with skills
 *       404:
 *         description: Job not found
 *       500:
 *         description: Internal server error
 */
router.get("/:jobId", jobsController.getJobById);

/**
 * @swagger
 * /api/jobs/{jobId}/match:
 *   post:
 *     summary: Compare student skills with job requirements
 *     tags:
 *       - Jobs
 *     parameters:
 *       - in: path
 *         name: jobId
 *         required: true
 *         schema:
 *           type: string
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - skillIds
 *             properties:
 *               skillIds:
 *                 type: array
 *                 items:
 *                   type: integer
 *                 example: [3, 4, 5]
 *     responses:
 *       200:
 *         description: Skill comparison result
 *       400:
 *         description: Invalid skill IDs
 *       404:
 *         description: Job not found
 */
router.post("/:jobId/match", jobsController.matchJobSkills);

/**
 * @swagger
 * /api/jobs/recommendations:
 *   post:
 *     summary: Recommend jobs based on selected skills
 *     tags:
 *       - Jobs
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - skillIds
 *             properties:
 *               skillIds:
 *                 type: array
 *                 items:
 *                   type: integer
 *                 example: [3, 4, 5]
 *               excludeJobId:
 *                 type: string
 *                 nullable: true
 *                 description: Job ID to exclude from recommendations
 *               limit:
 *                 type: integer
 *                 default: 3
 *                 minimum: 1
 *                 maximum: 10
 *     responses:
 *       200:
 *         description: List of recommended jobs sorted by skill match
 *       400:
 *         description: Invalid request parameters
 *       500:
 *         description: Internal server error
 */
router.post("/recommendations", jobsController.recommendJobs);

module.exports = router;
