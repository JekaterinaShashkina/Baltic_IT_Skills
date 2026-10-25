# Baltic IT Skills

Baltic IT Skills is a bachelor's thesis project focused on analyzing IT skills demand in Estonia, Latvia, and Lithuania using online job advertisements and the ESCO classification.

The project aims to identify frequently requested IT skills, compare demand across the Baltic countries, and support students in understanding the skills required in the job market.

## Technologies

- Python
- SQLite
- MeetFrank API
- ESCO classification
- Requests

## Current Implementation

- Automated collection of IT job advertisements from MeetFrank.
- Data processing and storage in SQLite.
- Tracking job advertisements and their observations over time.
- Recording ETL pipeline execution results.
- Initial experiments with mapping job skills to ESCO concepts.
- Tests for data collection, processing, and database updates.

## Project Structure

- `src/` – data collection, processing, database operations, and ESCO integration.
- `tests/` – automated tests and data validation scripts.
- `experiments/` – experimental scripts and sample API responses.
- `data/` – raw and processed data.
- `db_sceme.drawio` – database schema diagram.

## Running the ETL Pipeline

From the project root directory:

```bash
python -m src.run_pipeline
```

The pipeline collects software engineering job advertisements from Estonia, Latvia, and Lithuania and updates the SQLite database.

Database location: `data/baltic_it_skills.db`

## Planned Development

- Further integration with ESCO.
- Analysis and visualization of IT skills demand across the Baltic countries.
- Development of a web prototype for comparing students' skills with labour market requirements.

## Project Status

Work in progress — bachelor's thesis project.
