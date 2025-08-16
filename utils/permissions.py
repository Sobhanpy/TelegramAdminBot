"""
بررسی ادمین بودن و سطوح دسترسی.
"""
from aiogram import Bot
from aiogram.enums import ChatMemberStatus

async def is_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    # try:
    #     member = await bot.get_chat_member(chat_id, user_id)
    #     return member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}
    # except Exception:
    #     return False
    admin_list = []
    admin_list.append(bot.get_chat_administrators(chat_id))
    if user_id in admin_list:
        return True
    else:
        return False