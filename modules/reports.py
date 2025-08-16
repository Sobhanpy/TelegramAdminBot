
"""
گزارش‌گیری و آمار + جستجو.
"""
from __future__ import annotations
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import func, select, desc
from db.database import AsyncSessionLocal
from db.models import MemberStats, MessageLog, Warning
from utils.permissions import is_admin

router = Router(name="reports")

@router.message(Command("stats"))
async def stats_cmd(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        return await msg.reply("ادمین نیستید.")
    async with AsyncSessionLocal() as session:
        total_msgs = (await session.execute(
            select(func.count()).select_from(MessageLog).where(MessageLog.chat_id==msg.chat.id)
        )).scalar()
        top_users = (await session.execute(
            select(MemberStats.user_id, MemberStats.messages_count)
            .where(MemberStats.chat_id==msg.chat.id)
            .order_by(desc(MemberStats.messages_count)).limit(5)
        )).all()
        warns = (await session.execute(
            select(func.count()).select_from(Warning).where(Warning.chat_id==msg.chat.id)
        )).scalar()
    lines = [f"📨 مجموع پیام‌های لاگ‌شده: {total_msgs or 0}",
             f"⚠️ مجموع اخطارها: {warns or 0}",
             "👤 برترین فعال‌ها:"]
    for uid, cnt in top_users:
        lines.append(f"- {uid}: {cnt} پیام")
    await msg.reply("\n".join(lines))

@router.message(Command("search"))
async def search_cmd(msg: Message, bot: Bot):
    if not await is_admin(bot, msg.chat.id, msg.from_user.id):
        return await msg.reply("ادمین نیستید.")
    parts = msg.text.split(maxsplit=1)
    if len(parts) != 2:
        return await msg.reply("فرمت: /search عبارت")
    q = parts[1].lower()
    async with AsyncSessionLocal() as session:
        rows = (await session.execute(
            select(MessageLog.message_id, MessageLog.text)
            .where((MessageLog.chat_id==msg.chat.id) & (func.lower(MessageLog.text).like(f"%{q}%")))
            .order_by(desc(MessageLog.id)).limit(10)
        )).all()
    if not rows:
        return await msg.reply("چیزی پیدا نشد.")
    lines = [f"نتایج (حداکثر 10):"]
    for mid, txt in rows:
        preview = (txt or "")[:64].replace("\n", " ")
        lines.append(f"- #{mid}: {preview}")
    await msg.reply("\n".join(lines))
