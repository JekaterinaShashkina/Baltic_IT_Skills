const winston = require("winston");
const path = require("path");

const { combine, timestamp, errors, json, colorize, printf } = winston.format;

const logDirectory = path.join(__dirname, "../../logs");

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || "info",

  format: combine(timestamp(), errors({ stack: true }), json()),

  transports: [
    new winston.transports.File({
      filename: path.join(logDirectory, "error.log"),
      level: "error",
    }),

    new winston.transports.File({
      filename: path.join(logDirectory, "combined.log"),
    }),
  ],
});

if (process.env.NODE_ENV !== "test") {
  logger.add(
    new winston.transports.Console({
      format: combine(
        colorize(),
        timestamp({ format: "HH:mm:ss" }),
        printf(
          ({ timestamp, level, message }) =>
            `${timestamp} ${level}: ${message}`,
        ),
      ),
    }),
  );
}

module.exports = logger;
