from aiogram import Bot
from modules.utils import load_json, save_json

FILTERS_FILE = "filters.json"

async def delete_messages(bot: Bot, chat_id: int, message_ids: list):
    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, msg_id)
        except:
            continue

def add_filter(word: str):
    filters = load_json(FILTERS_FILE)
    filters[word] = True
    save_json(FILTERS_FILE, filters)

def remove_filter(word: str):
    filters = load_json(FILTERS_FILE)
    if word in filters:
        del filters[word]
    save_json(FILTERS_FILE, filters)

def check_filters(text: str):
    filters = load_json(FILTERS_FILE)
    for word in filters.keys():
        if word in text:
            return True
    return False
