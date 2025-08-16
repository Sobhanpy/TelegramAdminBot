"""
نقطه شروع: ساخت Bot/Dispatcher، رجیستر روترها، ساخت جداول DB، و Polling.
"""
from __future__ import annotations
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import settings
from utils.logger import setup_logging
from db.database import engine, Base
from modules import public, admin, messages, reports, inline
from services.scheduler import SchedulerService

async def on_startup(bot: Bot):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    logger = setup_logging()
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # سرویس زمان‌بندی برای استفاده در admin
    admin.scheduler_service = SchedulerService(bot)

    # روترها
    dp.include_router(public.router)
    dp.include_router(admin.router)
    dp.include_router(messages.router)
    dp.include_router(reports.router)
    dp.include_router(inline.router)

    await on_startup(bot)
    logger.info("ربات در حال اجراست...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
