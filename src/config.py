
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DB_PATH = BASE_DIR / "data" / "baltic_it_skills.db"

# MeetFrank API
MEETFRANK_API_URL = "https://api.meetfrank.com/ai/jobs"
COUNTRIES = ["estonia", "latvia", "lithuania"]
MEETFRANK_SPECIALITY = "software engineering"
MEETFRANK_PAGE_SIZE = 100

# ESCO API
ESCO_API_URL = "https://ec.europa.eu/esco/api/search"
ESCO_SKILL_URL = "https://ec.europa.eu/esco/api/resource/skill"
ESCO_VERSION = "v1.2.0"
ESCO_LANGUAGE = "en"
ESCO_SEARCH_LIMIT = 10

# HTTP
REQUEST_TIMEOUT = 30
