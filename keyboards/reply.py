from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def education_keyboard():
    kb = [
        [KeyboardButton(text="زیر دیپلم"), KeyboardButton(text="دیپلم")],
        [KeyboardButton(text="لیسانس"), KeyboardButton(text="فوق لیسانس و بالاتر")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="تحصیلات را انتخاب کنید...")

def copd_stage_keyboard():
    kb = [
        [KeyboardButton(text="Stage 1 (خفیف)"), KeyboardButton(text="Stage 2 (متوسط)")],
        [KeyboardButton(text="Stage 3 (شدید)"), KeyboardButton(text="Stage 4 (بسیار شدید)")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def marital_status_keyboard():
    kb = [
        [KeyboardButton(text="متاهل"), KeyboardButton(text="مجرد")],
        [KeyboardButton(text="همسر فوت شده")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def sex_keyboard():
    kb = [[KeyboardButton(text="مرد"), KeyboardButton(text="زن")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def yes_no_keyboard():
    kb = [[KeyboardButton(text="بله"), KeyboardButton(text="خیر")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def phone_keyboard():
    kb = [[KeyboardButton(text="📱 ارسال شماره موبایل", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)