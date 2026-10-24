from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    waiting_grant_tg_id = State()
    waiting_broadcast_text = State()
    waiting_user_query = State()
    waiting_promo_line = State()
