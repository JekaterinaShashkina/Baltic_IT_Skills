const express = require("express");
const jobsController = require("../controllers/jobs.controller");

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

module.exports = router;
