from aiogram.fsm.state import State, StatesGroup

class RegistrationForm(StatesGroup):
    # --- اطلاعات مراقب ---
    cg_fullname = State()     
    cg_age = State()          
    cg_relation = State()     
    cg_job = State()          
    cg_education = State()    
    
    # --- اطلاعات بیمار ---
    pt_fullname = State()     
    pt_stage = State()        
    pt_education = State()    
    pt_marital = State()      
    pt_duration = State()