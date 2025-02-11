import re

from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import Command, StateFilter

from aiogram.fsm.context import FSMContext

import os
from dotenv import load_dotenv

from database.export_to_csv import export_users_to_csv
from .admin_states import CreateMailing, SetRecources
from keyboards.admin_commands import get_kb_confirm, remove_mailing_button
import routers.commands.admin_sender as sender

from .base_validation import URL_REGEX
from keyboards.admin_commands import admin_keyboard, AdminButtonText, to_cancel_mailing, show_mailing_keyboards, to_cancel_resorces_process, photo_button_cancel
from database.mailing.requests import show_all_mailings
from database.resources.requests import save_btn_resources_to_database, show_resources_button

load_dotenv(os.path.join('config', '.env'))
router = Router(name=__name__)

ADMIN_ACCESS = F.from_user.id.in_({int(os.getenv("ADMIN1")), int(os.getenv("ADMIN2"))})


@router.message(Command("admin", prefix="!"), ADMIN_ACCESS)
async def secret_admin_message(message: types.Message):
    await message.bot.send_message(
        text=f"Hi, Admin!",
        chat_id=message.chat.id,
        reply_markup=admin_keyboard(),
    )

@router.message(F.text == AdminButtonText.MAILING_ALL, ADMIN_ACCESS)
async def mailing_all(message: types.Message, state: FSMContext):
    start_mailing_smg = await message.answer(
        text=f"<b>Создание рассылки!</b>\n\nОтправь текст для рассылки:",
        reply_markup=to_cancel_mailing(),
    )
    await state.update_data(start_mailing_msg_id=start_mailing_smg.message_id)
    await state.set_state(CreateMailing.get_text)


@router.message(CreateMailing.get_text, F.text, ADMIN_ACCESS)
async def set_mailing_text_handler(message: types.Message, state: FSMContext):
    await state.update_data(msg_text=message.md_text)

    data = await state.get_data()
    start_mailing_message = data.get('start_mailing_msg_id')
    await message.bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=[start_mailing_message],
    )

    text = f"Отлично! Добавь фото/документ/кнопку при необходимости или нажми <i>Далее</i>"
    reply_markup = photo_button_cancel()

    sent_message = await message.answer(
        text=text,
        reply_markup=reply_markup,
    )

    await state.update_data(
        saved_message_text=text,
        saved_reply_markup=reply_markup,
        saved_message_id=sent_message.message_id,
    )


@router.message(CreateMailing.get_text, ~F.text, ADMIN_ACCESS)
async def handle_non_main_text_message(message: types.Message):
    await message.answer(
        text="Необходимо прислать текстовое сообщение. Попробуй снова",
        reply_markup=to_cancel_mailing(),
    )


@router.message(CreateMailing.get_photo_doc, (F.photo | F.document) & ADMIN_ACCESS)
async def set_mailing_photo_or_doc_hundler(message: types.Message, state: FSMContext):
    if message.photo:
        await state.update_data(msg_photo=message.photo[-1].file_id)
    elif message.document:
        await state.update_data(msg_document=message.document.file_id)

    data = await state.get_data()
    msg_photo_request = data.get('msg_photo_request_id')
    await message.bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=[msg_photo_request],
    )

    saved_text = data.get("saved_message_text")
    saved_reply_markup = data.get("saved_reply_markup")
    saved_message_id = data.get("saved_message_id")

    if saved_text and saved_reply_markup:
        sent_message = await message.answer(
            text=saved_text,
            reply_markup=saved_reply_markup
        )
        await state.update_data(saved_message_id=sent_message.message_id)



    # await state.set_state(CreateMailing.get_keyboard_text)
    # await message.answer(
    #     text="Отправь текст, который будет отображаться на кнопке:",
    #     reply_markup=to_cancel_mailing(),
    # )


@router.message(CreateMailing.get_photo_doc, ~(F.photo | F.document) & ADMIN_ACCESS)
async def handle_non_photo_message(message: types.Message):
    await message.answer(
        text=f"Необходимо предоставить фото или документ",
        reply_markup=to_cancel_mailing(),
    )


@router.message(CreateMailing.get_keyboard_text, F.text.func(lambda text: len(text) <= 34) & ADMIN_ACCESS)
async def set_mailing_btn_text_handler(message: types.Message, state: FSMContext):
    await state.update_data(btn_text=message.text)

    data = await state.get_data()

    await state.set_state(CreateMailing.get_keyboard_url)
    await message.answer(
        text=f"Отправь ссылку для кнопки:",
        reply_markup=to_cancel_mailing(),
    )

@router.message(CreateMailing.get_keyboard_text, ~(F.text), ADMIN_ACCESS)
async def handle_non_text_btn_message(message: types.Message):
    await message.answer(
        text=f"Кнопка может принимать только текст",
        reply_markup=to_cancel_mailing(),
    )


@router.message(CreateMailing.get_keyboard_text, F.text.func(lambda text: len(text) > 34) & ADMIN_ACCESS)
async def handle_too_long_btn_text(message: types.Message):
    await message.reply(
        text=f"Текст для кнопки не может быть длиннее 34 символов. Попробуй снова",
        reply_markup=to_cancel_mailing(),
    )


@router.message(CreateMailing.get_keyboard_url, F.text, ADMIN_ACCESS)
async def set_mailing_btn_url_handler(message: types.Message, state: FSMContext):

    url = message.text
    if re.match(URL_REGEX, url):
        await state.update_data(btn_url=url)
        await state.set_state(CreateMailing.go_next_without_components)

        data = await state.get_data()

        saved_text = data.get("saved_message_text")
        saved_reply_markup = data.get("saved_reply_markup")
        saved_message_id = data.get("saved_message_id")

        if saved_text and saved_reply_markup:
            sent_message = await message.answer(
                text=saved_text,
                reply_markup=saved_reply_markup
            )
            await state.update_data(saved_message_id=sent_message.message_id)

    else:
        await message.answer(
            text=f"Используй корректный URL, начинающийся с http:// или https://.",
            reply_markup=to_cancel_mailing(),
        )


@router.message(CreateMailing.get_keyboard_url, ~(F.text), ADMIN_ACCESS)
async def handle_no_btn_url_text(message: types.Message):
    await message.answer(
        text=f"Ссылка может принимать только текст",
        reply_markup=to_cancel_mailing(),
    )


@router.message(CreateMailing.get_tag, F.text, ADMIN_ACCESS)
async def get_tag_handler(message: types.Message, state: FSMContext):
    message_tags = message.text.split(",")
    tags = [tag.strip() for tag in message_tags]
    await state.update_data(msg_tag=tags)
    await state.set_state(CreateMailing.go_next_without_components)

    data = await state.get_data()
    saved_text = data.get("saved_message_text")
    saved_reply_markup = data.get("saved_reply_markup")
    saved_message_id = data.get("saved_message_id")

    if saved_text and saved_reply_markup:
        sent_message = await message.answer(
            text=saved_text,
            reply_markup=saved_reply_markup
        )
        await state.update_data(saved_message_id=sent_message.message_id)


@router.message(CreateMailing.go_next_without_components, F.text, ADMIN_ACCESS)
async def set_final_mailing_steps(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = await sender.send_preview(
        message,
        data,
    )

    await state.update_data(message_id=message_id)
    await message.answer(
        text=f"<b>Сообщение для рассылки сформировано!</b>\n\nЧтобы начать, нажми на кнопку ниже",
        reply_markup=get_kb_confirm().as_markup(),
        parse_mode=ParseMode.HTML,
    )
    await state.set_state(CreateMailing.confirm_sender)



@router.message(F.text == AdminButtonText.MAILING_SHOW, ADMIN_ACCESS)
async def handle_show_all_mailings(message: types.Message):
    result = await show_all_mailings()

    if not result:
        await message.answer("Нет успешных рассылок.")
        return

    await message.answer(
        text=f'Список успешных рассылок:'
    )

    for mail in result:

        if mail.button_text and mail.button_url:
            markup = show_mailing_keyboards(mail.button_text, mail.button_url, mail.id)
        else:
            markup = remove_mailing_button(mail.id)

        if mail.tag:
            tag_exists = f'Тег: **{mail.tag}**\n'
        else:
            tag_exists = f'Тег: **Рассылка по всем**\n'

        if mail.document_file_id:
            await message.bot.send_document(
                chat_id=message.chat.id,
                document=mail.document_file_id,
                caption=f'\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n'
                        f'Рассылка **№{mail.id}**:\n'
                        f'Текст: {mail.text}\n\n'
                        f'{tag_exists}'
                        f'\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n',
                parse_mode="MarkdownV2",
                reply_markup=markup,
            )
        elif mail.image_file_id:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=mail.image_file_id,
                caption=f'\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n'
                        f'Рассылка **№{mail.id}**:\n'
                        f'Текст: {mail.text}\n\n'
                        f'{tag_exists}'
                        f'\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n',
                parse_mode="MarkdownV2",
                reply_markup=markup,
            )
        else:
            await message.bot.send_message(
                chat_id=message.chat.id,
                text=f'\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n'
                        f'Рассылка **№{mail.id}**:\n'
                        f'Текст: {mail.text}\n\n'
                        f'{tag_exists}'
                        f'\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n',
                parse_mode="MarkdownV2",
                reply_markup=markup,
            )


@router.message(F.text == AdminButtonText.GET_CSV_FILE, ADMIN_ACCESS)
async def get_csv_file(message: types.Message):
    doc = await export_users_to_csv("users_data.csv")

    await message.bot.send_document(
        chat_id=message.chat.id,
        caption=f'Файл успешно создан',
        document=types.FSInputFile(
            path=doc,
            filename="База данных пользователей.csv"
        )
    )


@router.message(F.text == AdminButtonText.RESOURCES_SETTING, ADMIN_ACCESS)
async def set_recources_buttons(message: types.Message, state: FSMContext):
    await message.answer(
        text=f'Какой текст поместить на 3 кнопки?\n<i>Пришли текст для 3 кнопок с новой строки</i>\nПример:\n\nТекст кнопки 1\nТекст кнопки 2\nТекст кнопки 3',
        reply_markup=to_cancel_resorces_process(),
    )
    await state.set_state(SetRecources.get_btn_text)


@router.message(SetRecources.get_btn_text, F.text.func(lambda text: len(text) <= 105) & ADMIN_ACCESS)
async def get_btn_text(message: types.Message, state: FSMContext):
    await state.update_data(btn_text=message.md_text)
    data = await state.get_data()
    await message.answer(
        text=f'Теперь пришли ссылки для каждой кнопки соответственно. <i>В том же формате.\n</i>Пример:\n\nhttps://google.com\nhttps://mail.ru\nhttps://yandex.ru',
        reply_markup=to_cancel_resorces_process(),
        disable_web_page_preview=True,
    )
    await state.set_state(SetRecources.get_btn_url)


@router.message(SetRecources.get_btn_text, F.text.func(lambda text: len(text) > 105) & ADMIN_ACCESS)
async def get_btn_text_too_long(message: types.Message, state: FSMContext):
    await message.reply(
        text=f"Общий текст для кнопок не может быть длиннее 105 символов (1 кнопка = 34 символа). Попробуй снова",
        reply_markup=to_cancel_resorces_process(),
    )


@router.message(SetRecources.get_btn_url, F.text)
async def get_btn_url(message: types.Message, state: FSMContext):
    await state.update_data(btn_url=message.text)
    data = await state.get_data()
    await save_btn_resources_to_database(data)

    keyboard = await show_resources_button()

    await message.answer(
        text=f'Данные для кнопок успешно записаны! Результат отображения кнопок прикреплен к этому сообщению.',
        reply_markup=keyboard,
    )
    await state.clear()