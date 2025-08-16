"""
فرمان‌های ادمین: پنل، بن/آنبن، سکوت/آزاد، پاکسازی، زمان‌بندی، اخطار، تنظیمات، همگام‌سازی.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from aiogram import Router, Bot
from aiogram.types import Message, CallbackQuery, ChatPermissions
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from utils.permissions import is_admin
from utils.keyboards import admin_panel_kb, settings_kb
from db.database import AsyncSessionLocal
from db.models import Chat, MemberStats, ScheduledMessage, Warning
from config import settings
from services.scheduler import SchedulerService

router = Router(name="admin")
scheduler_service: SchedulerService | None = None  # در main مقداردهی می‌شود

@router.message(Command("panel"))
async def admin_panel(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("این دستور فقط برای ادمین‌هاست.")
    await msg.reply("پنل ادمین:", reply_markup=admin_panel_kb(msg.chat.id))

@router.message(Command("ban"))
async def ban_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False :
        return await msg.reply("ادمین نیستید.")
    target_id = msg.reply_to_message.from_user.id
    # if not target_id:
    #     parts = msg.text.split()
    #     if len(parts) == 2 and parts[1].isdigit():
    #         target_id = int(parts[1])
    if not target_id:
        return await msg.reply("یک پیام از کاربر ریپلای کنید")
    try:
        await bot.ban_chat_member(msg.chat.id, target_id)
        await msg.reply("کاربر بن شد.")
    except TelegramBadRequest as e:
        await msg.reply(f"خطا در بن: {e.message}")

@router.message(Command("unban"))
async def unban_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    parts = msg.text.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.reply("فرمت: /unban user_id")
    try:
        await bot.unban_chat_member(msg.chat.id, int(parts[1]))
        await msg.reply("کاربر آزاد شد.")
    except TelegramBadRequest as e:
        await msg.reply(f"خطا: {e.message}")

@router.message(Command("mute"))
async def mute_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    parts = msg.text.split()
    target_id = msg.reply_to_message.from_user.id if msg.reply_to_message else (int(parts[1]) if len(parts)>=2 and parts[1].isdigit() else None)
    minutes = (int(parts[2]) if len(parts)>=3 and parts[2].isdigit() else settings.MUTE_MINUTES_ON_MAX_WARN)
    if not target_id:
        return await msg.reply("یک پیام از کاربر ریپلای کنید")
    until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    perms = ChatPermissions(can_send_messages=False)
    try:
        await bot.restrict_chat_member(msg.chat.id, target_id, permissions=perms, until_date=until_date)
        await msg.reply(f"کاربر به مدت {minutes} دقیقه میوت شد.")
    except TelegramBadRequest as e:
        await msg.reply(f"خطا: {e.message}")

@router.message(Command("unmute"))
async def unmute_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    parts = msg.text.split()
    target_id = msg.reply_to_message.from_user.id if msg.reply_to_message else (int(parts[1]) if len(parts)==2 and parts[1].isdigit() else None)
    if not target_id:
        return await msg.reply("یک پیام از کاربر ریپلای کنید")
    perms = ChatPermissions(
        can_send_messages=True, can_send_audios=True, can_send_documents=True,
        can_send_photos=True, can_send_videos=True, can_send_voice_notes=True,
        can_send_video_notes=True
    )
    try:
        await bot.restrict_chat_member(msg.chat.id, target_id, permissions=perms)
        await msg.reply("کاربر آزاد شد.")
    except TelegramBadRequest as e:
        await msg.reply(f"خطا: {e.message}")

@router.message(Command("purge"))
async def purge_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    if not msg.reply_to_message:
        return await msg.reply("برای پاکسازی، روی اولین پیام ریپلای کنید و /purge بفرستید.")
    start_id = msg.reply_to_message.message_id
    end_id = msg.message_id
    deleted = 0
    for mid in range(start_id, end_id+1):
        try:
            await bot.delete_message(msg.chat.id, mid)
            deleted += 1
        except TelegramBadRequest:
            pass
    await msg.reply(f"پاکسازی انجام شد. تعداد حذف‌شده: {deleted}")

@router.message(Command("schedule"))
async def schedule_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    try:
        _, date_s, time_s, *text_parts = msg.text.split()
        text = " ".join(text_parts)
        run_at = datetime.fromisoformat(f"{date_s} {time_s}")
        if scheduler_service:
            await scheduler_service.schedule_message(msg.chat.id, text, run_at)
        async with AsyncSessionLocal() as session:
            sm = ScheduledMessage(chat_id=msg.chat.id, text=text, run_at=run_at, created_by=msg.from_user.id)
            session.add(sm)
            await session.commit()
        await msg.reply("پیام زمان‌بندی شد.")
    except Exception:
        await msg.reply("فرمت نادرست. مثال: /schedule 2025-12-01 09:30 متن")

@router.message(Command("warn"))
async def warn_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    target_id = msg.reply_to_message.from_user.id #if msg.reply_to_message else None
    if not target_id:
        return await msg.reply("روی پیام کاربر ریپلای کنید.")
    reason = " ".join(msg.text.split()[1:]) if len(msg.text.split()) > 1 else "نقض قوانین"
    async with AsyncSessionLocal() as session:
        session.add(Warning(chat_id=msg.chat.id, user_id=target_id, reason=reason))
        ms = (await session.execute(
            MemberStats.__table__.select().where(
                (MemberStats.chat_id==msg.chat.id) & (MemberStats.user_id==target_id)
            )
        )).scalar_one_or_none()
        if ms:
            await session.execute(
                MemberStats.__table__.update().where(MemberStats.id==ms.id).values(
                    warnings_count=ms.warnings_count+1
                )
            )
            warns = ms.warnings_count + 1
        else:
            await session.execute(
                MemberStats.__table__.insert().values(
                    chat_id=msg.chat.id, user_id=target_id, messages_count=0, warnings_count=1
                )
            )
            warns = 1
        await session.commit()

    if warns >= settings.MAX_WARNINGS:
        minutes = settings.MUTE_MINUTES_ON_MAX_WARN
        until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        perms = ChatPermissions(can_send_messages=False)
        try:
            await bot.restrict_chat_member(msg.chat.id, target_id, permissions=perms, until_date=until_date)
            await msg.reply(f"اخطار {warns}/{settings.MAX_WARNINGS}. کاربر {minutes} دقیقه میوت شد.")
        except TelegramBadRequest as e:
            await msg.reply(f"خطا در میوت خودکار: {e.message}")
    else:
        await msg.reply(f"اخطار ثبت شد: {warns}/{settings.MAX_WARNINGS}")

@router.message(Command("syncfrom"))
async def syncfrom_cmd(msg: Message, bot: Bot):
    """
    همگام‌سازی تنظیمات از یک گروه دیگر: /syncfrom other_chat_id
    (باید ادمین هر دو گروه باشید)
    """
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.reply("فرمت: /syncfrom chat_id")
    other_id = int(parts[1])
    async with AsyncSessionLocal() as session:
        other = (await session.execute(Chat.__table__.select().where(Chat.chat_id==other_id))).scalar_one_or_none()
        if not other or not other.settings:
            return await msg.reply("تنظیمات گروه مبدا یافت نشد.")
        current = (await session.execute(Chat.__table__.select().where(Chat.chat_id==msg.chat.id))).scalar_one_or_none()
        if current:
            await session.execute(Chat.__table__.update().where(Chat.chat_id==msg.chat.id).values(settings=other.settings))
        else:
            await session.execute(Chat.__table__.insert().values(chat_id=msg.chat.id, settings=other.settings))
        await session.commit()
    await msg.reply("تنظیمات همگام‌سازی شد.")

@router.message(Command("settings"))
async def settings_cmd(msg: Message, bot: Bot):
    if  is_admin(bot, msg.chat.id, msg.from_user.id) == False:
        return await msg.reply("ادمین نیستید.")
    await msg.reply("تنظیمات:", reply_markup=settings_kb(msg.chat.id))
