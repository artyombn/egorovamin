from typing import List

from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import async_session
from database.resources.requests import get_buttons


class AdminButtonText:
    MAILING_ALL = "Создать рассылку"
    MAILING_SHOW = "Показать успешные рассылки"
    RESOURCES_SETTING = "Управление основными ресурсами"
    GET_CSV_FILE = "Выгрузить данные пользователей в CSV файл"

def get_kb_confirm() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"Отправить сейчас",
            callback_data=f"start_mailing",
        ),
        InlineKeyboardButton(
            text=f"Отменить",
            callback_data=f"cancel_mailing",
        )
    )

    return builder

def to_cancel_mailing():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Отменить рассылку",
        callback_data=f"cancel_mailing",
    )
    builder.adjust(1)

    return builder.as_markup()

def photo_button_cancel():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Добавить фото или документ",
        callback_data=f"add_mailing_photo_or_doc",
    )
    builder.button(
        text=f"Добавить кнопку",
        callback_data=f"add_mailing_button",
    )
    builder.button(
        text=f"Добавить Тег",
        callback_data=f"add_mailing_tag",
    )
    builder.button(
        text=f"Далее",
        callback_data=f"go_mailing_next",
    )
    builder.button(
        text=f"Отменить рассылку",
        callback_data=f"cancel_mailing",
    )
    builder.adjust(1,2,1,1)

    return builder.as_markup()

def to_cancel_resorces_process():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Отменить изменения",
        callback_data=f"cancel_resources_process",
    )
    builder.adjust(1)

    return builder.as_markup()


def admin_keyboard():
    button1 = KeyboardButton(text=AdminButtonText.MAILING_ALL)
    button3 = KeyboardButton(text=AdminButtonText.MAILING_SHOW)
    button4 = KeyboardButton(text=AdminButtonText.RESOURCES_SETTING)
    button5 = KeyboardButton(text=AdminButtonText.GET_CSV_FILE)
    markup = ReplyKeyboardMarkup(
        keyboard=[[button1], [button3, button4], [button5]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return markup

def show_mailing_keyboards(btn_text: str, btn_url: str, mailing_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=btn_text,
        url=btn_url,
    )
    builder.button(
        text=f"Удалить",
        callback_data=f"remove_mailing_by_id:{mailing_id}",
    )

    builder.adjust(1)
    return builder.as_markup()

def remove_mailing_button(mailing_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"Удалить",
        callback_data=f"remove_mailing_by_id:{mailing_id}",
    )
    builder.adjust(1)
    return builder.as_markup()


# def previw_resources_button():
#     builder = InlineKeyboardBuilder()
#     for btn in all_buttons:
#         builder.button(
#             text=btn.button_text,
#             url=btn.button_url,
#         )
#     builder.adjust(1)