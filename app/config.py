import os
from pathlib import Path
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
assert BOT_TOKEN, "BOT_TOKEN environment variable is not set"

_BASE_DIR = Path(__file__).parent
_PROD_DATA = Path("/data")
TIMEZONE = ZoneInfo("Asia/Jakarta")  # adjust to if needed
DATA_DIR = _PROD_DATA if _PROD_DATA.exists() and any(_PROD_DATA.iterdir()) else _BASE_DIR / "data"
TASK_FILE = DATA_DIR / "tasks.json"
SOFT_DELETE = True

DATA_DIR.mkdir(parents=True, exist_ok=True)


NOTIFY_TIMES = [
    {"hour": 7,  "minute": 0,  "label": "morning"},
    {"hour": 12, "minute": 30,  "label": "afternoon"},
    {"hour": 19, "minute": 0,  "label": "evening"},
]

# Tasks created automatically for every known chat_id each morning.
# Set your default tasks or [] to disable.
DEFAULT_DAILY_TASKS: list[str] = []