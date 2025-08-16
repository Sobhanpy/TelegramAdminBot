from aiogram import types, Bot
from config import ADMIN_IDS

async def kick_user(bot: Bot, chat_id: int, user_id: int):
    try:
        await bot.ban_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)  # برای حذف کامل
        return True
    except Exception as e:
        print("Kick error:", e)
        return False

async def restrict_user(bot: Bot, chat_id: int, user_id: int, until_date=None):
    try:
        await bot.restrict_chat_member(
            chat_id,
            user_id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        return True
    except Exception as e:
        print("Restrict error:", e)
        return False

async def promote_user(bot: Bot, chat_id: int, user_id: int):
    if user_id in ADMIN_IDS:
        return False
    try:
        await bot.promote_chat_member(chat_id, user_id,
                                      can_change_info=True,
                                      can_delete_messages=True,
                                      can_invite_users=True,
                                      can_restrict_members=True)
        return True
    except Exception as e:
        print("Promote error:", e)
        return False
