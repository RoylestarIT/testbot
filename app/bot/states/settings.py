from aiogram.fsm.state import State, StatesGroup


class ConnectWbStates(StatesGroup):
    waiting_api_key = State()
    waiting_shop_name = State()


class ConnectOzonStates(StatesGroup):
    waiting_client_id = State()
    waiting_api_key = State()
    waiting_shop_name = State()


class ToneProfileStates(StatesGroup):
    waiting_description = State()
    waiting_examples = State()
    waiting_edit_description = State()
    waiting_edit_examples = State()


class ReplyTemplateStates(StatesGroup):
    waiting_label = State()
    waiting_text = State()
