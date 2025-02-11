import time
from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from database.mailing.requests import get_active_users, active_users_by_tag, save_mailing_to_db, delete_mailing
import routers.commands.admin_sender as sender
from config.services import bot
from keyboards.admin_commands import to_cancel_mailing
from routers.commands.admin_commands import set_mailing_photo_or_doc_hundler, set_final_mailing_steps
from routers.commands.admin_states import CreateMailing


router = Router(name=__name__)

@router.callback_query(F.data == "cancel_mailing")
async def cancel_sending(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Рассылка отменена')
    await state.clear()
    await callback.answer()

@router.callback_query(F.data == "start_mailing")
async def start_sending(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tag = data.get('msg_tag')
    await callback.message.answer('Рассылка началась')

    await save_mailing_to_db(data)

    await state.clear()
    await callback.answer()

    if tag:
        user_ids = await active_users_by_tag(tag)
    else:
        user_ids = await get_active_users()
    t_start = time.time()
    message_id = data.get('message_id')

    count = await sender.start_sender(
        bot=bot,
        data=data,
        user_ids=user_ids,
        from_chat_id=callback.message.chat.id,
        message_id=message_id,
    )

    await callback.message.answer(f"Отправлено {count}/{len(user_ids)} за {round(time.time() - t_start)}с")


@router.callback_query(F.data == "cancel_resources_process")
async def cancel_resour_process(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Изменения ресурсов отменены')
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "add_mailing_photo_or_doc")
async def q_add_mailing_photo_or_doc(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    saved_msg_id = data.get('saved_message_id')

    if saved_msg_id:
        await callback.message.bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=[saved_msg_id],
        )

    await state.set_state(CreateMailing.get_photo_doc)
    msg_photo_request = await callback.message.answer(
        text=f'Пришли фото или документ, который будет прикреплен к сообщению:',
        reply_markup=to_cancel_mailing(),
    )
    await state.update_data(msg_photo_request_id=msg_photo_request.message_id)
    await callback.answer()


@router.callback_query(F.data == "add_mailing_button")
async def q_add_mailing_button(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    saved_msg_id = data.get('saved_message_id')

    if saved_msg_id:
        await callback.message.bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=[saved_msg_id],
        )


    await state.set_state(CreateMailing.get_keyboard_text)
    await callback.message.answer(
        text=f'Отправь текст, который будет отображаться на кнопке:',
        reply_markup=to_cancel_mailing(),
    )
    await callback.answer()



@router.callback_query(F.data == "add_mailing_tag")
async def q_add_mailing_tag(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    saved_msg_id = data.get('saved_message_id')

    if saved_msg_id:
        await callback.message.bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=[saved_msg_id],
        )

    await state.set_state(CreateMailing.get_tag)
    await callback.message.answer(
        text=f'По каким тегам будем делать рассылку?\n'
             f'<i>Список тегов: A1, A2, B1, B2, C1</i>\n'
             f'<i>(теги должны быть на английском через запятую)</i>',
        reply_markup=to_cancel_mailing(),
    )
    await callback.answer()


@router.callback_query(F.data == "go_mailing_next")
async def q_go_mailing_next(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    saved_msg_id = data.get('saved_message_id')

    if saved_msg_id:
        await callback.message.bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=[saved_msg_id],
        )

    await state.set_state(CreateMailing.go_next_without_components)
    await set_final_mailing_steps(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith("remove_mailing_by_id"))
async def q_remove_mailing_button(callback: CallbackQuery, state: FSMContext):

    mailing_id = int(callback.data.split(":")[1])

    mailing = await delete_mailing(mailing_id)
    if mailing:
        await callback.message.delete()
    else:
        print(f"Рассылка №{mailing_id} не найдена.")





# Параллельная отправка через Celery

# async def start_sending(callback: CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     await callback.message.answer('Рассылка началась')
#     await state.clear()
#     await callback.answer()
#
#     user_ids = await get_active_users()
#     t_start = time.time()
#     message_id = data.get('message_id')
#
#     # Параллельная отправка сообщений
#     tasks = [sender.start_sender(
#         bot=bot,
#         data=data,
#         user_ids=user_ids[i:i + 50],  # Разбивка на пачки по 50
#         from_chat_id=callback.message.chat.id,
#         message_id=message_id
#     ) for i in range(0, len(user_ids), 50)]
#
#     results = await asyncio.gather(*tasks)
#
#     total_count = sum(results)
#     await callback.message.answer(f"Отправлено {total_count}/{len(user_ids)} за {round(time.time() - t_start)}с")
