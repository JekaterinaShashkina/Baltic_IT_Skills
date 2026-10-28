console.log("SERVER FILE STARTED");
const express = require("express");
const cors = require("cors");
const db = require("./database");
const swaggerUi = require("swagger-ui-express");
const swaggerSpec = require("./swagger");

const jobsRouter = require("./routes/jobs");
const skillsRouter = require("./routes/skills");

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

/**
 * @swagger
 * /api/health:
 *   get:
 *     summary: Check API health
 *     tags:
 *       - System
 *     responses:
 *       200:
 *         description: API is running
 */
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", message: "BalticITSkills API is running" });
});

app.use("/api-docs", swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.use("/api/jobs", jobsRouter);
app.use("/api/skills", skillsRouter);

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
