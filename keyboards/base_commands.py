from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

class ButtonText:
    AGREEMENT = "Я согласен(-на)"
    ENG_LVLs = ['A1', 'A2', 'B1', 'B2', 'C1']

def button_agreement():
    button = KeyboardButton(text=ButtonText.AGREEMENT)
    markup = ReplyKeyboardMarkup(
        keyboard=[[button]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    return markup

def keyboards_get_eng_lvl():
    builder = InlineKeyboardBuilder()

    for lvl in ButtonText.ENG_LVLs:
        builder.button(
            text=lvl,
            callback_data=f"level_{lvl}",
        )

    builder.adjust(2)
    return builder


