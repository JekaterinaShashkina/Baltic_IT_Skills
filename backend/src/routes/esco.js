const express = require("express");
const router = express.Router();

const escoController = require("../controllers/esco.controller");

/**
 * @swagger
 * /api/esco/analysis:
 *   get:
 *     summary: Get ESCO mapping analysis
 *     tags: [ESCO]
 *     responses:
 *       200:
 *         description: ESCO mapping coverage and ICT occupation statistics
 *       500:
 *         description: Internal server error
 */
router.get("/analysis", escoController.getAnalysis);

module.exports = router;
