from aiogram.fsm.state import State, StatesGroup

class RegistrationForm(StatesGroup):
    # --- اطلاعات مراقب ---
    cg_fullname = State()
    cg_phone_number = State()
    cg_national_code = State()
    cg_age = State()
    cg_sex = State()
    cg_marital_status = State()
    cg_relation = State()
    cg_education = State()
    cg_job = State()
    cg_living_with_patient = State()
    cg_special_disease = State()
    
    # --- اطلاعات بیمار ---
    pt_fullname = State()
    pt_age = State()
    pt_sex = State()
    pt_stage = State()
    pt_disease_duration = State()
