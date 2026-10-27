from aiogram.fsm.state import State, StatesGroup


class SupportContactStates(StatesGroup):
    waiting_message = State()
    waiting_idea = State()
