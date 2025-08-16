import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_IDS
from modules import user_management, message_management, external_apis
from .modules import reports

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# استارت ربات و خوشامدگویی
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.reply("سلام! ربات مدیریت گروه پیشرفته آماده است.")

# نمونه فرمان فیلتر کلمات
@dp.message()
async def filter_handler(message: types.Message):
    if message.chat.type in ["group", "supergroup"]:
        if message_management.check_filters(message.text):
            await message.delete()
            await message.reply(f"{message.from_user.mention()} پیام شما شامل کلمه فیلتر شده است.")

# نمونه فرمان سکوت دادن کاربر
@dp.message(Command("mute"))
async def mute_handler(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.reply("این فرمان فقط برای ادمین‌هاست!")
        return
    if not message.reply_to_message:
        await message.reply("برای سکوت دادن، پیام کاربر را ریپلای کنید.")
        return
    user_id = message.reply_to_message.from_user.id
    await user_management.restrict_user(bot, message.chat.id, user_id)
    await message.reply(f"{message.reply_to_message.from_user.mention()} سکوت شد.")

# نمونه فرمان وضعیت هوا
@dp.message(Command("weather"))
async def weather_handler(message: types.Message):
    city = message.get_args()
    if not city:
        await message.reply("لطفاً نام شهر را وارد کنید: /weather Berlin")
        return
    result = await external_apis.get_weather(city)
    await message.reply(result)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
