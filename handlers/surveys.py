import aiohttp
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from states.surveys import SurveyFlow
from keyboards.inline import survey_keyboard
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User

router = Router()

# آدرس فرم‌های شما در پرسیان
SURVEY_URLS = {
    1: "https://porsian.ir/s/HUB1HC/",
    2: "https://porsian.ir/s/zoRrNN/",
    3: "https://porsian.ir/s/JkqU1B/"
}

@router.callback_query(F.data.startswith("check_survey_"))
async def verify_survey_completion(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    survey_step = int(callback.data.split("_")[2])
    bale_id = callback.from_user.id
    
    full_url = SURVEY_URLS.get(survey_step)
    short_code = full_url.rstrip('/').split('/')[-1]
    api_endpoint = f"https://porsian.ir/api/bot-check/?bale_id={bale_id}&short_code={short_code}"
    
    # ۱. قطع کردن لودینگ خود دکمه شیشه‌ای (تا ارور تایم‌اوت ندهد)
    await callback.answer()
    
    # ۲. ارسال یک پیام متنی موقت برای لودینگ
    wait_msg = await callback.message.answer("⏳ در حال استعلام وضعیت شما از سرور پرسیان... لطفاً شکیبا باشید.")
    
    try:
        async with aiohttp.ClientSession() as http_session:
            async with http_session.get(api_endpoint, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("is_completed") is True:
                        submission_id = data.get("submission_id")
                        
                        user = await session.scalar(select(User).where(User.bale_id == bale_id))
                        if user:
                            if survey_step == 1:
                                user.survey1_submission_id = submission_id
                            elif survey_step == 2:
                                user.survey2_submission_id = submission_id
                            elif survey_step == 3:
                                user.survey3_submission_id = submission_id
                                
                            await session.commit()
                        
                        # حذف پیام لودینگ و پیام حاوی دکمه
                        await wait_msg.delete()
                        await callback.message.delete()
                        
                        # رفتن به مرحله بعد
                        await process_next_survey(callback.message, state, survey_step, bale_id)
                        
                    else:
                        # ویرایش پیام موقت به متن خطا
                        await wait_msg.edit_text("❌ هنوز پاسخی با شناسه شما در سیستم ثبت نشده است.\nلطفاً وارد لینک شده و پس از زدن دکمه «ثبت نهایی» در سایت پرسیان، مجدداً اینجا تست کنید.")
                else:
                    await wait_msg.edit_text("⚠️ ارتباط با سرور پرسیان موقتاً دچار مشکل است. لطفاً چند دقیقه دیگر تلاش کنید.")
                    
    except Exception as e:
        print(f"❌ HTTP Error: {e}")
        await wait_msg.edit_text("⚠️ خطای سیستمی رخ داد. لطفاً چند دقیقه دیگر تست کنید.")

async def process_next_survey(message: types.Message, state: FSMContext, current_step: int, bale_id: int):
    """تابع کمکی برای هدایت کاربر به پرسشنامه بعدی یا پایان کار"""
    
    if current_step == 1:
        await state.set_state(SurveyFlow.waiting_for_survey_2)
        await message.answer(
            "✅ پرسشنامه اول با موفقیت ثبت شد. خداقوت!\n\n"
            "لطفاً برای ادامه، پرسشنامه دوم را تکمیل کنید:",
            reply_markup=survey_keyboard(SURVEY_URLS[2], bale_id, 2)
        )
    elif current_step == 2:
        await state.set_state(SurveyFlow.waiting_for_survey_3)
        await message.answer(
            "✅ پرسشنامه دوم نیز ثبت شد. فقط یک گام دیگر باقی مانده است!\n\n"
            "لطفاً پرسشنامه نهایی را تکمیل کنید:",
            reply_markup=survey_keyboard(SURVEY_URLS[3], bale_id, 3)
        )
    elif current_step == 3:
        await state.clear()
        await message.answer("🎉 تبریک! تمام مراحل ثبت‌نام و ارزیابی اولیه با موفقیت به پایان رسید.\nحالا می‌توانید از امکانات اصلی ربات استفاده کنید.")