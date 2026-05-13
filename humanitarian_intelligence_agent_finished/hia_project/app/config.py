import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")
DAILY_CHAT_ID = os.getenv("DAILY_CHAT_ID", "")
DAILY_BRIEF_HOUR_UTC = int(os.getenv("DAILY_BRIEF_HOUR_UTC", "6"))

RELIEFWEB_APPNAME = "humanitarian-intelligence-agent"
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
