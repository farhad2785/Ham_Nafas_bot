from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_registration_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 شروع ثبت‌نام", callback_data="start_registration")]
    ])