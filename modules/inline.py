
"""
اینلاین‌مود: نمایش گزینه‌ی «پنل ادمین» برای استفاده سریع در گروه.
"""
from __future__ import annotations
from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent

router = Router(name="inline")

@router.inline_query()
async def inline_admin_panel(iq: InlineQuery):
    result = InlineQueryResultArticle(
        id="admin-panel",
        title="پنل ادمین گروه",
        description="برای باز کردن پنل ادمین، این کارت را ارسال کنید",
        input_message_content=InputTextMessageContent(message_text="«پنل ادمین» را باز کنید: /panel"),
    )
    await iq.answer([result], cache_time=1, is_personal=True)
