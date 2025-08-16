"""
زمان‌بندی پیام‌ها با APScheduler.
"""
from __future__ import annotations
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from aiogram import Bot

class SchedulerService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()

    async def schedule_message(self, chat_id: int, text: str, run_at: datetime):
        trigger = DateTrigger(run_date=run_at.astimezone(timezone.utc))
        self.scheduler.add_job(self._send, trigger=trigger, args=[chat_id, text])

    async def _send(self, chat_id: int, text: str):
        await self.bot.send_message(chat_id, text)
