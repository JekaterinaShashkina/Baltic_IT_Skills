const Database = require("better-sqlite3");

const path = require("path");

const dbPath = path.join(__dirname, "../data/baltic_it_skills.db");

const db = new Database(dbPath, {
  readonly: true,
  fileMustExist: true,
});

module.exports = db;
