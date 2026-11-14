const escoService = require("../services/esco.service");
const logger = require("../utils/logger");

const getAnalysis = (req, res) => {
  try {
    const analysis = escoService.getAnalysis();
    res.json(analysis);
  } catch (error) {
    logger.error("Error fetching ESCO analysis:", { error });

    res.status(500).json({
      error: "Failed to fetch ESCO analysis",
    });
  }
};

module.exports = {
  getAnalysis,
};
