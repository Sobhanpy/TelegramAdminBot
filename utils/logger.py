"""
پیکربندی ساده لاگر.
"""
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    logging.getLogger("aiogram").setLevel(logging.INFO)
    return logging.getLogger("bot")
