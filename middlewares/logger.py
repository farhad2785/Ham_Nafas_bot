import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update

# تنظیمات لاگر
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ActionLoggerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        if isinstance(event, Update):
            if event.message:
                user = event.message.from_user
                text = event.message.text or "[بدون متن - فایل/عکس]"
                # بررسی None بودن کاربر برای جلوگیری از خطای Pylance
                if user:
                    logger.info(f"[MESSAGE] User: {user.id} ({user.first_name}) | Text: {text}")
                
            elif event.callback_query:
                user = event.callback_query.from_user
                data_str = event.callback_query.data
                if user:
                    logger.info(f"[CALLBACK] User: {user.id} ({user.first_name}) | Data: {data_str}")
                
        return await handler(event, data)