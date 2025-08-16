"""
کیبوردهای این‌لاین برای پنل ادمین و تنظیمات.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_panel_kb(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🚫 فهرست کلمات ممنوعه", callback_data=f"show_filters:{chat_id}"),
            InlineKeyboardButton(text="➕ افزودن کلمه", callback_data=f"add_filter:{chat_id}")
        ],
        [
            InlineKeyboardButton(text="🧹 پاکسازی بازه پیام", callback_data=f"purge:{chat_id}"),
            InlineKeyboardButton(text="⏰ زمان‌بندی پیام", callback_data=f"schedule:{chat_id}")
        ],
        [
            InlineKeyboardButton(text="📊 آمار گروه", callback_data=f"stats:{chat_id}"),
            InlineKeyboardButton(text="⚙️ تنظیمات گروه", callback_data=f"settings:{chat_id}")
        ],
        [
            InlineKeyboardButton(text="🔁 همگام‌سازی تنظیمات", callback_data=f"sync:{chat_id}"),
        ]
    ])

def settings_kb(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="فیلتر کلمات: روشن/خاموش", callback_data=f"toggle_filter:{chat_id}"),
            InlineKeyboardButton(text="محدودیت عضو جدید", callback_data=f"new_member_restrict:{chat_id}")
        ],
        [
            InlineKeyboardButton(text="خروج", callback_data=f"back:{chat_id}")
        ]
    ])
