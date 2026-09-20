import logging
import os


DEBUG = os.environ.get("DEBUG", "").lower() in {"1", "true", "yes"}
API_KEY = os.environ.get("API_KEY", "")
API_BASE_URL = os.environ.get("API_BASE_URL", "http://roundreview_app:8080/api").rstrip("/")

PLUGIN_VERSION = "0.1.0"
PLUGIN_NAME = "ai_reviewer_bot"
PLUGIN_BASE_URL = os.environ.get("PLUGIN_BASE_URL", "http://localhost:8083").rstrip("/")
PLUGIN_BASE_URL_PREFIX = os.environ.get("PLUGIN_BASE_URL_PREFIX", "").rstrip("/")

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://ollama:11434").rstrip("/")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.2")
LLM_API_TYPE = os.environ.get("LLM_API_TYPE", "auto").lower()
LLM_TIMEOUT_SECONDS = int(os.environ.get("LLM_TIMEOUT_SECONDS", "600"))

DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
DASHBOARD_SECRET_KEY = os.environ.get("DASHBOARD_SECRET_KEY", DASHBOARD_PASSWORD or "change-me")
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "Review the document carefully. Return clear, actionable review feedback.",
)
SYSTEM_PROMPT_FILE = os.environ.get("SYSTEM_PROMPT_FILE", "/data/system_prompt.txt")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(f"roundreview-{PLUGIN_NAME}")