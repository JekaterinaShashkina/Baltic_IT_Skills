const escoRepository = require("../repositories/esco.repository");

const getAnalysis = () => escoRepository.getAnalysis();

module.exports = {
  getAnalysis,
};
