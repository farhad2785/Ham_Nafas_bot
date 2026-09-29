from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

# ایمپورت ماژول‌هایی که در مراحل قبل ساختیم
from states.registration import RegistrationForm
from keyboards.inline import start_registration_kb
from keyboards.reply import education_keyboard, copd_stage_keyboard, marital_status_keyboard
from aiogram.types import ReplyKeyboardRemove

# ساخت روتر اختصاصی برای این فایل
router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """هندلر پیام شروع ربات هم‌نفس"""
    await state.clear() # پاک کردن وضعیت‌های قبلی در صورت وجود
    
    welcome_text = (
        "سلام! به ربات *هم‌نفس* خوش آمدید. 🩵\n\n"
        "مراقبت از عزیزان مبتلا به بیماری‌های مزمن تنفسی (COPD) مسیری پر از فداکاری است. "
        "برای اینکه بتوانیم محتوا و پرسشنامه‌ها را دقیقاً متناسب با شرایط شما و بیمارتان تنظیم کنیم، "
        "لطفاً ابتدا فرآیند ثبت‌نام را تکمیل کنید."
    )
    
    FILE_ID = "174735753:3732142107797626624:1:1eb794cc4867c3ebbbef6dd7a1e4ee1c"
    
    try:
        await message.answer_photo(
            photo=FILE_ID,
            caption=welcome_text,
            reply_markup=start_registration_kb()
        )
    except Exception as e:
        print(f"❌ خطا در ارسال پیام یکپارچه: {e}")
        await message.answer(text=welcome_text, reply_markup=start_registration_kb())

@router.callback_query(F.data == "start_registration")
async def process_start_registration(callback: types.CallbackQuery, state: FSMContext):
    """شروع فرم ثبت‌نام و درخواست نام مراقب"""
    await state.set_state(RegistrationForm.cg_fullname)
    
    await callback.message.answer(  #type: ignore
        "ابتدا اطلاعات شما (به عنوان مراقب) را دریافت می‌کنیم.\n\n"
        "👤 لطفاً نام و نام خانوادگی خود را وارد کنید:"
    )
    await callback.answer()
    
# ==========================================
# بخش اول: دریافت اطلاعات مراقب (Caregiver)
# ==========================================

@router.message(RegistrationForm.cg_fullname)
async def process_cg_fullname(message: types.Message, state: FSMContext):
    # ذخیره نام مراقب
    await state.update_data(cg_fullname=message.text)
    
    # رفتن به مرحله بعد
    await state.set_state(RegistrationForm.cg_age)
    await message.answer("🔢 لطفاً سن خود را (به عدد) وارد کنید:")

@router.message(RegistrationForm.cg_age)
async def process_cg_age(message: types.Message, state: FSMContext):
    await state.update_data(cg_age=message.text)
    await state.set_state(RegistrationForm.cg_relation)
    await message.answer("👨‍👩‍👧‍👦 نسبت شما با بیمار چیست؟ (مثلاً: فرزند، همسر، خواهر/برادر)")

@router.message(RegistrationForm.cg_relation)
async def process_cg_relation(message: types.Message, state: FSMContext):
    await state.update_data(cg_relation=message.text)
    await state.set_state(RegistrationForm.cg_job)
    await message.answer("💼 شغل شما چیست؟")

@router.message(RegistrationForm.cg_job)
async def process_cg_job(message: types.Message, state: FSMContext):
    await state.update_data(cg_job=message.text)
    await state.set_state(RegistrationForm.cg_education)
    
    # فراخوانی کیبورد تحصیلات
    await message.answer(
        "🎓 میزان تحصیلات خود را از منوی زیر انتخاب کنید:",
        reply_markup=education_keyboard()
    )

@router.message(RegistrationForm.cg_education)
async def process_cg_education(message: types.Message, state: FSMContext):
    await state.update_data(cg_education=message.text)
    
    # ==========================================
    # بخش دوم: دریافت اطلاعات بیمار (Patient)
    # ==========================================
    await state.set_state(RegistrationForm.pt_fullname)
    
    # حذف کیبورد قبلی تا کاربر بتواند متن تایپ کند
    await message.answer(
        "✅ اطلاعات شما ثبت شد.\n\n"
        "حالا لطفاً اطلاعات بیمار را وارد کنید:\n"
        "👤 نام و نام خانوادگی بیمار را بنویسید:",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(RegistrationForm.pt_fullname)
async def process_pt_fullname(message: types.Message, state: FSMContext):
    await state.update_data(pt_fullname=message.text)
    await state.set_state(RegistrationForm.pt_stage)
    
    await message.answer(
        "🫁 مرحله (Stage) بیماری ایشان در چه وضعیتی است؟",
        reply_markup=copd_stage_keyboard()
    )

@router.message(RegistrationForm.pt_stage)
async def process_pt_stage(message: types.Message, state: FSMContext):
    await state.update_data(pt_stage=message.text)
    await state.set_state(RegistrationForm.pt_education)
    
    await message.answer(
        "🎓 میزان تحصیلات بیمار را انتخاب کنید:",
        reply_markup=education_keyboard()
    )

@router.message(RegistrationForm.pt_education)
async def process_pt_education(message: types.Message, state: FSMContext):
    await state.update_data(pt_education=message.text)
    await state.set_state(RegistrationForm.pt_marital)
    
    await message.answer(
        "💍 وضعیت تاهل بیمار را مشخص کنید:",
        reply_markup=marital_status_keyboard()
    )

@router.message(RegistrationForm.pt_marital)
async def process_pt_marital(message: types.Message, state: FSMContext):
    await state.update_data(pt_marital=message.text)
    await state.set_state(RegistrationForm.pt_duration)
    
    await message.answer(
        "⏱ چه مدت است که ایشان با بیماری COPD درگیر هستند؟ (مثلاً: ۲ سال، ۶ ماه)",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(RegistrationForm.pt_duration)
async def process_pt_duration(message: types.Message, state: FSMContext):
    # ذخیره آخرین فیلد
    await state.update_data(pt_duration=message.text)
    
    # استخراج کل داده‌های جمع‌آوری شده
    user_data = await state.get_data()
    
    # در اینجا باید اطلاعات user_data را در دیتابیس (مثلاً PostgreSQL) ذخیره کنیم.
    # به طور موقت برای تست، آن‌ها را در ترمینال چاپ می‌کنیم:
    print(f"--- Registration Data for User {message.from_user.id} ---")
    print(user_data)
    
    # پاک کردن FSM وضعیت ثبت‌نام (برای آماده‌سازی جهت ورود به پرسشنامه‌ها)
    await state.clear()
    
    # پیام پایانی این بخش
    await message.answer(
        "🎉 ثبت‌نام اولیه شما با موفقیت انجام شد!\n\n"
        "برای شخصی‌سازی بهتر آموزش‌ها و پشتیبانی، نیاز است که ۳ پرسشنامه کوتاه پزشکی و روان‌سنجی را تکمیل کنید. "
        "آیا برای شروع پرسشنامه اول آماده‌اید؟",
        reply_markup=ReplyKeyboardRemove() # اینجا می‌توانیم کیبورد شیشه‌ای شروع پرسشنامه‌ها را قرار دهیم
    )