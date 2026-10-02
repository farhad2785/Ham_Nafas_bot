from aiogram.fsm.state import State, StatesGroup

class SurveyFlow(StatesGroup):
    waiting_for_survey_1 = State()
    waiting_for_survey_2 = State()
    waiting_for_survey_3 = State()