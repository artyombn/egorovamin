from aiogram.fsm.state import StatesGroup, State


class CreateMailing(StatesGroup):
    get_text = State()
    get_tag = State()
    get_text_tag = State()
    get_photo_doc = State()
    get_keyboard_text = State()
    get_keyboard_url = State()
    confirm_sender = State()
    go_next_without_components = State()


class SetRecources(StatesGroup):
    get_btn_text = State()
    get_btn_url = State()
