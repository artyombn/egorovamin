from typing import List

from aiogram.types import Message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode


def generate_keyboard(
        btn_text: str = None,
        btn_url: str = None,
) -> InlineKeyboardMarkup | None:
    btn_builder = InlineKeyboardBuilder()
    btn_builder.row(
        InlineKeyboardButton(
            text=btn_text,
            url=btn_url,
        )
    )
    return btn_builder.as_markup()


async def check_preview_message_components(
        message: Message,
        photo_id: str,
        document_id: str,
        text: str,
        tag: List,
        btn_text: str,
        btn_url: str,
):
    if btn_text and btn_url:
        keyboard = generate_keyboard(btn_text, btn_url)
    else:
        keyboard = None

    if tag:
        if photo_id:
            sent_message = await message.answer_photo(
                caption=f'{text}\n\n\\#Теги: {tag}',
                photo=photo_id,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        elif document_id:
            sent_message = await message.answer_document(
                caption=f'{text}\n\n\\#Теги: {tag}',
                document=document_id,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            sent_message = await message.answer(
                text=f'{text}\n\n\\#Теги: {tag}',
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
    else:
        if photo_id:
            sent_message = await message.answer_photo(
                caption=text,
                photo=photo_id,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        elif document_id:
            sent_message = await message.answer_document(
                caption=text,
                document=document_id,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            sent_message = await message.answer(
                text=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.MARKDOWN_V2,
            )


    return sent_message