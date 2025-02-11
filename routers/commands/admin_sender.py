import asyncio
from typing import Dict, List

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter

from aiogram.types import Message, InlineKeyboardMarkup

from database.mailing.requests import change_active
from routers.commands.check_preview import check_preview_message_components, generate_keyboard


async def send_preview_with_photo_doc_keyboard(
        message: Message,
        photo_id: str,
        document_id: str,
        text: str,
        tag: List,
        btn_text: str,
        btn_url: str,
) -> int:
    sent_message = await check_preview_message_components(
        message,
        photo_id,
        document_id,
        text,
        tag,
        btn_text,
        btn_url,
    )

    return sent_message.message_id


async def send_preview(
        message: Message,
        data: Dict,
) -> int:
    photo_id = data.get('msg_photo')
    document_id = data.get('msg_document')
    text = data.get('msg_text')
    tag = data.get('msg_tag')
    btn_text = data.get('btn_text')
    btn_url = data.get('btn_url')
    message_id = await send_preview_with_photo_doc_keyboard(
        message,
        photo_id=photo_id,
        document_id=document_id,
        text=text,
        tag=tag,
        btn_text=btn_text,
        btn_url=btn_url
    )
    return message_id


async def send_mail(
        bot: Bot,
        user_id: str,
        from_chat_id: int,
        message_id: int,
        keyboard: InlineKeyboardMarkup = None
) -> bool:
    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            reply_markup=keyboard,
        )
    except TelegramRetryAfter as e:
        await asyncio.sleep(e.retry_after)
        return await send_mail(bot, user_id, from_chat_id, message_id, keyboard)
    except Exception as e:
        print(e)
        await change_active(user_id, False)
        return False
    else:
        return True

async def start_sender(
        bot: Bot,
        data: Dict,
        user_ids: List[str],
        from_chat_id: int,
        message_id: int
) -> int:
    count = 0
    btn_text = data.get('btn_text')
    btn_url = data.get('btn_url')

    keyboard = None

    if btn_text and btn_url:
        keyboard = generate_keyboard(btn_text, btn_url)
    for u_id in user_ids:
        if await send_mail(bot, u_id, from_chat_id, message_id, keyboard):
            count += 1
        await asyncio.sleep(0.05)
    return count