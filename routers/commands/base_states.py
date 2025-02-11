from aiogram.fsm.state import StatesGroup, State


class BaseStates(StatesGroup):
    WAITING_FOR_AGREEMENT = State()
    GET_NAME = State()
    GET_EMAIL = State()
    GET_ENG_LVL = State()