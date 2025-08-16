from __future__ import annotations
import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    DEFAULT_TRANSLATE_LANG: str = os.getenv("DEFAULT_TRANSLATE_LANG", "en")
    TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Tehran")
    MAX_WARNINGS: int = int(os.getenv("MAX_WARNINGS", "3"))
    MUTE_MINUTES_ON_MAX_WARN: int = int(os.getenv("MUTE_MINUTES_ON_MAX_WARN", "60"))
    DEFAULT_SETTINGS: dict = {
        "new_member_restrict_minutes": 10,
        "filter_enabled": True,
        "filter_words": ["spam", "xxx"],
        "flood_threshold": 8,
        "rules_reminder_hours": 24,
        "auto_delete_ads": True,
    }

settings = Settings()
assert settings.BOT_TOKEN, "BOT_TOKEN در .env تنظیم نشده است!"
