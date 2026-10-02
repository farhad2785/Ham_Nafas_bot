from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
# ایمپورت مدل‌های دیتابیس
from database.models import User, Caregiver, Patient
from sqlalchemy.orm import selectinload
from states.registration import RegistrationForm
from states.surveys import SurveyFlow
from keyboards.inline import start_registration_kb,survey_keyboard
from keyboards.reply import (
    education_keyboard, 
    copd_stage_keyboard, 
    marital_status_keyboard,
    sex_keyboard,
    yes_no_keyboard,
    phone_keyboard
)

router = Router()

# آدرس فرم‌های شما در پرسیان
SURVEY_URLS = {
    1: "https://porsian.ir/s/HUB1HC/",
    2: "https://porsian.ir/s/zoRrNN/",
    3: "https://porsian.ir/s/JkqU1B/"
}

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, session: AsyncSession):
    bale_id = message.from_user.id
    
    # جستجوی کاربر همراه با اطلاعات مراقب و بیمار
    query = select(User).options(selectinload(User.caregiver), selectinload(User.patient)).where(User.bale_id == bale_id)
    user = await session.scalar(query)

    # حالت اول: کاربر کاملاً جدید است (اصلاً در دیتابیس نیست)
    if not user:
        new_user = User(bale_id=bale_id)
        session.add(new_user)
        await session.commit()
        await send_welcome_and_register(message, state) # تابع پیام خوشامدگویی اولیه
        return

    # حالت دوم: کاربر هست، اما فرم ۱۷ فیلدی را کامل نکرده است
    if not user.caregiver or not user.patient:
        await send_welcome_and_register(message, state)
        return

    # حالت سوم: فرم ۱۷ فیلدی پر شده، اما پرسشنامه‌ها ناقص است
    if not user.survey1_submission_id:
        await state.set_state(SurveyFlow.waiting_for_survey_1)
        await message.answer(
            "👋 شما قبلاً ثبت‌نام اولیه را انجام داده‌اید. لطفاً پرسشنامه اول را تکمیل کنید:",
            reply_markup=survey_keyboard(SURVEY_URLS[1], bale_id, 1)
        )
    elif not user.survey2_submission_id:
        await state.set_state(SurveyFlow.waiting_for_survey_2)
        await message.answer(
            "👋 خوش برگشتید! شما پرسشنامه اول را تکمیل کرده‌اید. لطفاً پرسشنامه دوم را پر کنید:",
            reply_markup=survey_keyboard(SURVEY_URLS[2], bale_id, 2)
        )
    elif not user.survey3_submission_id:
        await state.set_state(SurveyFlow.waiting_for_survey_3)
        await message.answer(
            "👋 فقط یک قدم تا پایان مانده! لطفاً پرسشنامه آخر را تکمیل کنید:",
            reply_markup=survey_keyboard(SURVEY_URLS[3], bale_id, 3)
        )
    else:
        # حالت چهارم: همه شناسه‌ها پر هستند (کار تمام شده است)
        await state.clear()
        await message.answer("✅ ثبت‌نام و ارزیابی‌های شما کاملاً انجام شده است. به منوی اصلی ربات خوش آمدید!")

async def send_welcome_and_register(message: types.Message, state: FSMContext):
    """تابع کمکی برای جلوگیری از تکرار کدهای پیام خوشامدگویی"""
    
    await state.clear()
    
    welcome_text = (
        "سلام! به ربات *هم‌نفس* خوش آمدید. 🩵\n\n"
        "مراقبت از عزیزان مبتلا به بیماری‌های مزمن تنفسی (COPD) مسیری پر از فداکاری است. "
        "برای اینکه بتوانیم محتوا و پرسشنامه‌ها را دقیقاً متناسب با شرایط شما و بیمارتان تنظیم کنیم، "
        "لطفاً ابتدا فرآیند ثبت‌نام را تکمیل کنید."
    )
    
    FILE_ID = "2106622428:-36647524721549568:0:1eb794cc4867c3ebd7c2f54fcdd42a151a9ec6f7595b78a8"

    try:
        await message.answer_photo(
            photo=FILE_ID,
            caption=welcome_text,
            reply_markup=start_registration_kb()
        )
    except Exception as e:
        print(f"❌ خطا در ارسال پیام یکپارچه: {e}")
        await message.answer(text=welcome_text, reply_markup=start_registration_kb())


@router.message(F.photo)
async def catch_photo_id(message: types.Message):
    """ابزار کمکی برای دریافت file_id معتبر از عکس‌های ارسالی"""
    # استخراج شناسه باکیفیت‌ترین نسخه عکس
    photo_id = message.photo[-1].file_id
    
    await message.reply(
        "📸 شناسه جدید و معتبر عکس شما:\n\n"
        f"<code>{photo_id}</code>\n\n"
        "این شناسه را کپی کرده و در متغیر FILE_ID در کد خود جایگزین کنید."
    )


@router.callback_query(F.data == "start_registration")
async def process_start_registration(callback: types.CallbackQuery, state: FSMContext):
    # تنظیم وضعیت روی دریافت شماره موبایل
    await state.set_state(RegistrationForm.cg_phone_number)
    
    await callback.message.answer(
        "ابتدا اطلاعات شما (به عنوان مراقب) را دریافت می‌کنیم.\n\n"
        "📱 لطفاً شماره موبایل خود را با استفاده از دکمه زیر ارسال کنید:",
        reply_markup=phone_keyboard()
    )
    await callback.answer()

@router.message(RegistrationForm.cg_phone_number)
async def process_cg_phone(message: types.Message, state: FSMContext):
    # اگر کاربر از دکمه استفاده کرد contact مقدار دارد، در غیر این صورت متنی که تایپ کرده ذخیره می‌شود
    phone = message.contact.phone_number if message.contact else message.text
    
    await state.update_data(cg_phone_number=phone)
    await state.set_state(RegistrationForm.cg_fullname)
    
    await message.answer(
        "👤 لطفاً نام و نام خانوادگی خود را وارد کنید:",
        reply_markup=ReplyKeyboardRemove() # حذف دکمه شماره موبایل
    )
# ==========================================
# بخش اول: دریافت اطلاعات مراقب (Caregiver)
# ==========================================

@router.message(RegistrationForm.cg_fullname)
async def process_cg_fullname(message: types.Message, state: FSMContext):
    await state.update_data(cg_fullname=message.text)
    await state.set_state(RegistrationForm.cg_national_code)
    await message.answer("🆔 لطفاً کد ملی خود را وارد کنید:")

@router.message(RegistrationForm.cg_national_code)
async def process_cg_national_code(message: types.Message, state: FSMContext):
    await state.update_data(cg_national_code=message.text)
    await state.set_state(RegistrationForm.cg_age)
    await message.answer("🔢 لطفاً سن خود را (به عدد) وارد کنید:")

@router.message(RegistrationForm.cg_age)
async def process_cg_age(message: types.Message, state: FSMContext):
    await state.update_data(cg_age=message.text)
    await state.set_state(RegistrationForm.cg_sex)
    await message.answer("⚧ جنسیت خود را انتخاب کنید:", reply_markup=sex_keyboard())

@router.message(RegistrationForm.cg_sex)
async def process_cg_sex(message: types.Message, state: FSMContext):
    await state.update_data(cg_sex=message.text)
    await state.set_state(RegistrationForm.cg_marital_status)
    await message.answer("💍 وضعیت تاهل خود را مشخص کنید:", reply_markup=marital_status_keyboard())

@router.message(RegistrationForm.cg_marital_status)
async def process_cg_marital_status(message: types.Message, state: FSMContext):
    await state.update_data(cg_marital_status=message.text)
    await state.set_state(RegistrationForm.cg_relation)
    await message.answer(
        "👨‍👩‍👧‍👦 نسبت شما با بیمار چیست؟ (مثلاً: فرزند، همسر، خواهر/برادر)",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(RegistrationForm.cg_relation)
async def process_cg_relation(message: types.Message, state: FSMContext):
    await state.update_data(cg_relation=message.text)
    await state.set_state(RegistrationForm.cg_education)
    await message.answer("🎓 میزان تحصیلات خود را انتخاب کنید:", reply_markup=education_keyboard())

@router.message(RegistrationForm.cg_education)
async def process_cg_education(message: types.Message, state: FSMContext):
    await state.update_data(cg_education=message.text)
    await state.set_state(RegistrationForm.cg_job)
    await message.answer("💼 شغل شما چیست؟", reply_markup=ReplyKeyboardRemove())

@router.message(RegistrationForm.cg_job)
async def process_cg_job(message: types.Message, state: FSMContext):
    await state.update_data(cg_job=message.text)
    await state.set_state(RegistrationForm.cg_living_with_patient)
    await message.answer("🏠 آیا با بیمار در یک منزل زندگی می‌کنید؟", reply_markup=yes_no_keyboard())

@router.message(RegistrationForm.cg_living_with_patient)
async def process_cg_living(message: types.Message, state: FSMContext):
    await state.update_data(cg_living_with_patient=message.text)
    await state.set_state(RegistrationForm.cg_special_disease)
    await message.answer(
        "⚕️ آیا خودتان بیماری خاصی دارید؟ (اگر خیر، بنویسید «ندارم»)",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(RegistrationForm.cg_special_disease)
async def process_cg_special_disease(message: types.Message, state: FSMContext):
    await state.update_data(cg_special_disease=message.text)
    
    # ==========================================
    # بخش دوم: دریافت اطلاعات بیمار (Patient)
    # ==========================================
    await state.set_state(RegistrationForm.pt_fullname)
    await message.answer(
        "✅ اطلاعات شما به عنوان مراقب ثبت شد.\n\n"
        "حالا لطفاً اطلاعات بیمار را وارد کنید:\n"
        "👤 نام و نام خانوادگی بیمار را بنویسید:"
    )

@router.message(RegistrationForm.pt_fullname)
async def process_pt_fullname(message: types.Message, state: FSMContext):
    await state.update_data(pt_fullname=message.text)
    await state.set_state(RegistrationForm.pt_age)
    await message.answer("🔢 سن بیمار را (به عدد) وارد کنید:")

@router.message(RegistrationForm.pt_age)
async def process_pt_age(message: types.Message, state: FSMContext):
    await state.update_data(pt_age=message.text)
    await state.set_state(RegistrationForm.pt_sex)
    await message.answer("⚧ جنسیت بیمار را انتخاب کنید:", reply_markup=sex_keyboard())

@router.message(RegistrationForm.pt_sex)
async def process_pt_sex(message: types.Message, state: FSMContext):
    await state.update_data(pt_sex=message.text)
    await state.set_state(RegistrationForm.pt_stage)
    await message.answer("🫁 مرحله (Stage) بیماری ایشان در چه وضعیتی است؟", reply_markup=copd_stage_keyboard())

@router.message(RegistrationForm.pt_stage)
async def process_pt_stage(message: types.Message, state: FSMContext):
    await state.update_data(pt_stage=message.text)
    await state.set_state(RegistrationForm.pt_disease_duration)
    await message.answer(
        "⏱ چه مدت است که ایشان با بیماری COPD درگیر هستند؟ (مثلاً: ۲ سال، ۶ ماه)",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(RegistrationForm.pt_disease_duration)
async def process_pt_duration(message: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(pt_disease_duration=message.text)
    user_data = await state.get_data()
    
    bale_id = message.from_user.id # type: ignore
    
    try:
        # ۲. ثبت اطلاعات مراقب
        new_caregiver = Caregiver(
            user_id=bale_id,
            phone_number=user_data.get('cg_phone_number'),
            fullname=user_data.get('cg_fullname'),
            national_code=user_data.get('cg_national_code'),
            age=int(user_data.get('cg_age', 0)),
            sex=user_data.get('cg_sex'),
            marital_status=user_data.get('cg_marital_status'),
            relation=user_data.get('cg_relation'),
            education=user_data.get('cg_education'),
            job=user_data.get('cg_job'),
            living_with_patient=user_data.get('cg_living_with_patient'),
            special_disease=user_data.get('cg_special_disease')
        )
        session.add(new_caregiver)
        
        # ۳. ثبت اطلاعات بیمار
        new_patient = Patient(
            user_id=bale_id,
            fullname=user_data.get('pt_fullname'),
            age=int(user_data.get('pt_age', 0)),
            sex=user_data.get('pt_sex'),
            stage=user_data.get('pt_stage'),
            disease_duration=user_data.get('pt_disease_duration')
        )
        session.add(new_patient)
        
        # ذخیره نهایی در دیتابیس
        await session.commit()
        
    except Exception as e:
        await session.rollback()
        print(f"❌ Database Insert Error: {e}")
        await message.answer("❌ خطایی در ثبت اطلاعات در پایگاه داده رخ داد. لطفاً /start را مجدداً ارسال کنید.")
        return

    # پاک کردن وضعیت فرم
    # await state.clear()
    
    # ==========================================
    # تغییرات جدید: اتصال به جریان پرسشنامه‌ها
    # ==========================================
    
    # ۱. انتقال به وضعیت پرسشنامه اول (به جای state.clear)
    await state.set_state(SurveyFlow.waiting_for_survey_1)
    
    # ۲. تولید کیبورد شیشه‌ای با تزریق آیدی بله
    keyboard = survey_keyboard(
        base_url=SURVEY_URLS[1], 
        bale_id=bale_id, 
        survey_step=1
    )
    
    # ۳. ارسال پیام به همراه کیبورد و حذف کیبورد متنی قبلی
    await message.answer(
        "🎉 ثبت‌نام اولیه شما با موفقیت در سیستم ذخیره شد!\n\n"
        "برای شخصی‌سازی بهتر آموزش‌ها و دریافت برنامه مراقبتی دقیق، نیاز است که پرسشنامه‌های پزشکی را تکمیل کنید.\n\n"
        "👇 لطفاً روی دکمه زیر کلیک کنید، در محیط وب به سوالات پاسخ دهید و در نهایت دکمه «تکمیل کردم» را همینجا فشار دهید:",
        reply_markup=keyboard
    )
