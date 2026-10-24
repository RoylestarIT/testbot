from aiogram.fsm.state import State, StatesGroup


class PromoRedeemStates(StatesGroup):
    waiting_code = State()
