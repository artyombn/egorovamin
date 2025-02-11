from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import async_session
from database.models import ButtonResource
from sqlalchemy import select, update, delete

from typing import Dict, List

# async def save_btn_resources_to_database(data: Dict):
#     async with async_session() as session:
#         async with session.begin():
#             btn_text = data.get('btn_text')
#             btn_url = data.get('btn_url')
#
#             btn_text_split = btn_text.split("\n")
#             btn_url_split = btn_url.split("\n")
#
#             for btn_txt in btn_text_split:
#                 result_btn_text = ButtonResource(
#                     button_text=btn_txt,
#                 )
#
#                 session.add(result_btn_text)
#
#             for btn_ur in btn_url_split:
#                 result_btn_url = ButtonResource(
#                     button_url=btn_ur,
#                 )
#
#                 session.add(result_btn_url)
#
#     await session.commit()


async def update_button_resource(all_buttons: List, btn_text_split: List, btn_url_split: List):
    async with async_session() as session:
        async with session.begin():

            for btn, btn_txt, btn_ur in zip(all_buttons, btn_text_split, btn_url_split):
                btn.button_text = btn_txt
                btn.button_url = btn_ur



async def save_btn_resources_to_database(data: Dict):
    async with async_session() as session:
        async with session.begin():
            btn_text = data.get('btn_text')
            btn_url = data.get('btn_url')
            btn_text_split = btn_text.split("\n")
            btn_url_split = btn_url.split("\n")

            if btn_text and btn_url:
                buttons = await session.execute(select(ButtonResource))
                all_buttons = buttons.scalars().all()
                await update_button_resource(all_buttons, btn_text_split, btn_url_split)
            else:
                for btn_txt, btn_ur in zip(btn_text_split, btn_url_split):
                    result = ButtonResource(
                        button_text=btn_txt,
                        button_url=btn_ur,
                    )

                    session.add(result)

    await session.commit()


async def get_buttons(session: AsyncSession):
    result = await session.execute(select(ButtonResource))
    return result.scalars().all()


async def show_resources_button():
    async with async_session() as session:
        all_buttons = await get_buttons(session)
        builder = InlineKeyboardBuilder()
        for btn in all_buttons:
            builder.button(
                text=btn.button_text,
                url=btn.button_url,
            )
        builder.adjust(1)

        return builder.as_markup()


async def keyboards_resources():
    async with async_session() as session:
        all_buttons = await get_buttons(session)
        builder = InlineKeyboardBuilder()

        for btn in all_buttons:
            builder.button(
                text=btn.button_text,
                url=btn.button_url,
            )
        builder.adjust(1)

    return builder.as_markup()
