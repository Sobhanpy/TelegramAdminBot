import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")  # توکن ربات
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))  # آیدی ادمین‌ها
DATA_PATH = "./data/"
