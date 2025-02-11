import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

from aiogram import Router, types, F
from aiogram.enums import ChatAction
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from config.services import scheduler, bot

from keyboards.base_commands import ButtonText, button_agreement, keyboards_get_eng_lvl
from reminders.reminders import send_reminder
from .base_states import BaseStates
from .base_validation import NAME_REGEX, EMAIL_REGEX

import database.users.requests as rq
from database.resources.requests import keyboards_resources

router = Router(name=__name__)

load_dotenv(os.path.join('config', '.env'))


@router.message(CommandStart())
async def start_message(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user_exists = await rq.check_user_exists(user_id)
    keyboard = await keyboards_resources()
    if user_exists:
        await message.answer(
            text=f"Привет, <b>{user_exists}</b>! А я тебя узнал"
        )
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Скорее чекай ссылки на полезные ресурсы для изучения английского 👇",
            reply_markup=keyboard,
        )

    else:
        await message.answer(
            text=f"Нажимая кнопку «Согласен(-на)», вы подтверждаете, что ознакомились с прикрепленным документом и даете согласие на обработку персональных данных в соответствии с Политикой в отношении обработки и защиты персональных данных.",
            reply_markup=button_agreement(),
        )

        file_id = os.getenv('FILE_ID')
        # file_path = 'media/Agreement.pdf'

        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.UPLOAD_DOCUMENT,
        )

        await message.bot.send_document(
            chat_id=message.chat.id,
            document=file_id,
        )

        # document_message = await message.bot.send_document(
        #     chat_id=message.chat.id,
        #     document=types.FSInputFile(
        #         path=file_path,
        #         filename="Согласие на обработку персональных данных.pdf"
        #     )
        # )

        # file_id = document_message.document.file_id
        # print(f"file_id: {file_id}")

        await state.set_state(BaseStates.WAITING_FOR_AGREEMENT)


@router.message(StateFilter(BaseStates.WAITING_FOR_AGREEMENT))
async def handle_non_agreement(message: types.Message, state: FSMContext):
    if message.text != ButtonText.AGREEMENT:
        await message.answer(
            text=f"Чтобы продолжить, необходимо принять согласие на обработку персональных данных",
            reply_markup=button_agreement(),
        )
    else:
        await message.answer(
            text=f"Привет! Это мой бот (Милены), в который я буду присылать полезные материалы для изучения английского языка: подборки, сайты, уроки, упражнения и еще много всего.\nОбещаю не спамить! А чтобы я смогла присылать тебе материалы, которые будут актуальны именно тебе, давай познакомимся 👇",
            reply_markup=ReplyKeyboardRemove(),
        )
        await rq.get_tg_user_info(message.from_user.id, message.from_user.username)
        await state.update_data(user_tg_id=message.from_user.id)
        await message.bot.send_chat_action(
            chat_id=message.chat.id,
            action=ChatAction.TYPING,
        )
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Как тебя зовут?\n<i>пример: Милена</i>",
        )

        job_id = f'reminder_job_{message.from_user.id}'
        reminder_time = datetime.now() + timedelta(minutes=720)
        scheduler.add_job(
            send_reminder,
            'date',
            run_date=reminder_time,
            args=[message.chat.id],
            misfire_grace_time=100,
            id=job_id,
        )

        await state.set_state(BaseStates.GET_NAME)


@router.message(BaseStates.GET_NAME, F.text)
async def get_name(message: types.Message, state: FSMContext):
    user_name = message.text.strip().capitalize()

    if re.match(NAME_REGEX, user_name):
        await state.update_data(user_name=user_name)
        await rq.get_user_name(message.from_user.id, user_name)
        await message.answer(f"Дай свою электронку\n<i>пример: egorovamln_help@gmail.com</i>")
        await state.set_state(BaseStates.GET_EMAIL)

    else:
        await message.answer("Имя может содержать только буквы, пробелы, апострофы и дефисы.")

@router.message(BaseStates.GET_EMAIL, F.text)
async def get_email(message: types.Message, state: FSMContext):
    user_email = message.text

    if re.match(EMAIL_REGEX, user_email):
        await state.update_data(user_email=user_email)
        await rq.get_user_email(message.from_user.id, user_email)
        await message.bot.send_message(
            chat_id=message.chat.id,
            text=f"Какой у тебя уровень английского? Выбери, какой тебе кажется наиболее близким к реальности",
            reply_markup=keyboards_get_eng_lvl().as_markup(),
        )
    else:
        await message.answer("Пожалуйста, напиши корректный email.")

@router.callback_query(lambda c: c.data.startswith("level_"))
async def handle_eng_lvl(callback_query: CallbackQuery, state: FSMContext):
    lvl = callback_query.data.split("_")[1]
    data = await state.get_data()
    user_tg_id = data.get('user_tg_id')
    user_email = data.get('user_email')
    await state.update_data(level=lvl)
    await rq.get_user_tag(user_email, lvl)
    await callback_query.message.answer(
        text=f"Приятно познакомиться! Не блокируй бота, чтобы получать свежие материалы."
    )
    await callback_query.message.delete()

    await callback_query.message.bot.send_chat_action(
        chat_id=callback_query.message.chat.id,
        action=ChatAction.TYPING,
    )

    keyboard = await keyboards_resources()

    await callback_query.message.bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"Скорее чекай ссылки на полезные ресурсы для изучения английского 👇",
        reply_markup=keyboard,
    )

    await callback_query.answer()

    job_id = f'reminder_job_{user_tg_id}'
    scheduler.remove_job(job_id)

    await state.clear()


