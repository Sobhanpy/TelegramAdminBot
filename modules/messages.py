"""
شنونده پیام‌ها: لاگ، فیلتر، ضدربات/محدودیت عضو جدید، ضد-فلاود.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
from aiogram import Router, Bot
from aiogram.types import Message, ChatMemberUpdated, ChatPermissions
from utils.filters import contains_forbidden, has_link, flood_hit
from db.database import AsyncSessionLocal
from db.models import Chat, MemberStats, MessageLog
from config import settings
from utils.permissions import is_admin

router = Router(name="messages")

@router.message()
async def message_logger(msg: Message, bot: Bot):
    # لاگ پیام + افزایش شمارش
    async with AsyncSessionLocal() as session:
        await session.execute(MessageLog.__table__.insert().values(
            chat_id=msg.chat.id,
            user_id=msg.from_user.id,
            message_id=msg.message_id,
            text=msg.text or msg.caption or "",
            has_link=has_link(msg.text or msg.caption or ""),
        ))
        ms = (await session.execute(
            MemberStats.__table__.select().where(
                (MemberStats.chat_id==msg.chat.id) & (MemberStats.user_id==msg.from_user.id)
            )
        )).scalar_one_or_none()
        if ms:
            await session.execute(
                MemberStats.__table__.update().where(MemberStats.id==ms.id).values(
                    messages_count=ms.messages_count+1, last_message_at=datetime.now(timezone.utc)
                )
            )
        else:
            await session.execute(
                MemberStats.__table__.insert().values(
                    chat_id=msg.chat.id, user_id=msg.from_user.id, messages_count=1, warnings_count=0,
                    last_message_at=datetime.now(timezone.utc)
                )
            )
        await session.commit()

    # تنظیمات گروه (در صورت نبود، ایجاد با پیش‌فرض)
    async with AsyncSessionLocal() as session:
        chat = (await session.execute(Chat.__table__.select().where(Chat.chat_id==msg.chat.id))).scalar_one_or_none()
        if not chat:
            await session.execute(Chat.__table__.insert().values(
                chat_id=msg.chat.id, title=msg.chat.title or "", settings=settings.DEFAULT_SETTINGS
            ))
            await session.commit()
            cfg = settings.DEFAULT_SETTINGS
        else:
            cfg = chat.settings if chat.settings else settings.DEFAULT_SETTINGS

    # ضد-فلاود
    if flood_hit(msg.chat.id, msg.from_user.id, threshold=cfg.get("flood_threshold", 8)):
        if not await is_admin(bot, msg.chat.id, msg.from_user.id):
            try:
                await msg.delete()
            except:
                pass

    # فیلتر کلمات
    if cfg.get("filter_enabled", True):
        bad = contains_forbidden(msg.text or msg.caption or "", cfg.get("filter_words", []))
        if bad and not await is_admin(bot, msg.chat.id, msg.from_user.id):
            try:
                await msg.delete()
            except:
                pass
            await msg.answer(f"⚠️ کلمه ممنوعه شناسایی شد: `{bad}`", parse_mode="Markdown")

@router.chat_member()
async def on_member_update(evt: ChatMemberUpdated, bot: Bot):
    # وقتی کاربر عضو می‌شود
    if evt.old_chat_member.status == "left" and evt.new_chat_member.status in {"member", "restricted"}:
        user = evt.new_chat_member.user
        chat_id = evt.chat.id
        # ضد ربات
        if user.is_bot:
            try:
                await bot.ban_chat_member(chat_id, user.id)
            except:
                pass
            return

        # محدودیت عضو جدید
        async with AsyncSessionLocal() as session:
            chat = (await session.execute(Chat.__table__.select().where(Chat.chat_id==chat_id))).scalar_one_or_none()
            cfg = chat.settings if chat and chat.settings else settings.DEFAULT_SETTINGS
            minutes = cfg.get("new_member_restrict_minutes", 0)

        if minutes > 0:
            until_date = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            perms = ChatPermissions(
                can_send_messages=False, can_send_media_messages=False, can_send_other_messages=False
            )
            try:
                await bot.restrict_chat_member(chat_id, user.id, permissions=perms, until_date=until_date)
            except:
                pass
