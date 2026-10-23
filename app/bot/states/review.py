from aiogram.fsm.state import State, StatesGroup


class ManualReviewStates(StatesGroup):
    waiting_text = State()
    waiting_rating = State()
    waiting_tone = State()
    viewing_variants = State()
