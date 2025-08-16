
"""
فرمان‌های عمومی (برای همه اعضا): هواشناسی، نرخ ارز، ترجمه، تگ محدود.
"""
from __future__ import annotations
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from services.external.weather import get_weather
from services.external.currency import fx_rate
from services.external.translate import translate as do_translate
from config import settings

router = Router(name="public")

@router.message(Command("start"))
async def start_cmd(msg: Message):
    await msg.reply("سلام! من یک ربات مدیریت گروه هستم. برای راهنما: /help")

@router.message(Command("help"))
async def help_cmd(msg: Message):
    text = (
        "دستورهای عمومی:\n"
        "/weather lat lon - هواشناسی (مثال: /weather 35.7 51.4)\n"
        "/fx BASE SYMBOLS - نرخ ارز (مثال: /fx USD EUR,IRR)\n"
        "/tr lang - روی یک پیام ریپلای کنید (مثال: /tr en)\n"
        "/tagonline - منشن محدود اعضای فعال اخیر\n"
        "دستورهای ادمین: /panel ، /ban ، /mute ، /purge ، /schedule ، /warn ، /stats ، /search ، /syncfrom\n"
    )
    await msg.reply(text)

@router.message(Command("weather"))
async def weather_cmd(msg: Message):
    parts = msg.text.split()
    if len(parts) != 3:
        return await msg.reply("فرمت: /weather lat lon")
    try:
        lat, lon = float(parts[1]), float(parts[2])
    except ValueError:
        return await msg.reply("مختصات نامعتبر.")
    res = await get_weather(lat, lon)
    await msg.reply(res)

@router.message(Command("fx"))
async def fx_cmd(msg: Message):
    parts = msg.text.split(maxsplit=2)
    base, symbols = "USD", "EUR,IRR"
    if len(parts) >= 2: base = parts[1]
    if len(parts) == 3: symbols = parts[2]
    data = await fx_rate(base, symbols)
    rates = data.get("rates", {})
    lines = [f"{k} = {v:.4f}" for k, v in rates.items()]
    await msg.reply(" | ".join(lines) or "نرخی در دسترس نیست.")

@router.message(Command("tr"))
async def translate_cmd(msg: Message):
    parts = msg.text.split()
    target = settings.DEFAULT_TRANSLATE_LANG if len(parts) < 2 else parts[1]
    if not msg.reply_to_message or not (msg.reply_to_message.text or msg.reply_to_message.caption):
        return await msg.reply("روی پیامی که می‌خواهید ترجمه شود ریپلای کنید.")
    src = msg.reply_to_message.text or msg.reply_to_message.caption
    out = await do_translate(src, target_lang=target)
    await msg.reply(out)

@router.message(Command("tagonline"))
async def tag_online_cmd(msg: Message):
    user = msg.from_user
    mention = f"[{user.full_name}](tg://user?id={user.id})"
    await msg.reply(f"تگ نمونه: {mention}", parse_mode="Markdown")
