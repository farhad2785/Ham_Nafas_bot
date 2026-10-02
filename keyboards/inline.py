from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_registration_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 شروع ثبت‌نام", callback_data="start_registration")]
    ])

def survey_keyboard(base_url: str, bale_id: int, survey_step: int):
    # چسباندن bale_id به انتهای لینک پرسیان
    dynamic_url = f"{base_url}?bale_id={bale_id}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 ورود به فرم پرسشنامه", url=dynamic_url)],
        # در بخش callback_data شماره مرحله پرسشنامه را می‌فرستیم تا بدانیم کدام فرم باید چک شود
        [InlineKeyboardButton(text="✅ پرسشنامه را تکمیل کردم", callback_data=f"check_survey_{survey_step}")]
    ])
    return kb