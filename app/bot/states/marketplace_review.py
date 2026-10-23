from aiogram.fsm.state import State, StatesGroup


class MarketplaceReviewStates(StatesGroup):
    viewing_variants = State()
    awaiting_publish_confirm = State()
    waiting_edit_text = State()
