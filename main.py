import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from middlewares.logger import ActionLoggerMiddleware
from middlewares.database import DbSessionMiddleware
from database.engine import async_session, init_db

# ایمپورت روتر از فایل هندلر جدید
from handlers.registration import router as registration_router
from handlers import surveys

load_dotenv()
TOKEN = os.getenv("BALE_BOT_TOKEN")
if not TOKEN:
    raise ValueError("BALE_BOT_TOKEN is not set.")

bale_server = TelegramAPIServer.from_base("https://tapi.bale.ai")
session = AiohttpSession(api=bale_server)

async def main():
    # ساخت جداول در دیتابیس هنگام بالا آمدن ربات (در صورت عدم وجود)
    await init_db()
    bot = Bot(
        token=TOKEN, #type: ignore
        session=session, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    
    # ثبت میدلورها
    dp.update.outer_middleware(ActionLoggerMiddleware())
    # اضافه کردن میدلور دیتابیس به همراه سشن‌میکر SQLAlchemy
    dp.update.outer_middleware(DbSessionMiddleware(session_pool=async_session))
    
    # ثبت روترهای تفکیک شده
    dp.include_router(registration_router)
    dp.include_router(surveys.router)
    
    print("Ham-Nafas Bot is running on Bale...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot) #type: ignore

if __name__ == "__main__":
    asyncio.run(main())