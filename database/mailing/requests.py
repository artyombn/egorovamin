from database.models import async_session
from database.models import User, Mailing
from sqlalchemy import select

from typing import Dict, List


async def get_active_users():
    async with async_session() as session:
        users = await session.execute(
            select(User.tg_id).filter(User.is_active)
        )
    return users.scalars().all()

async def change_active(tg_id: int, is_active: bool):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if user:
            user.is_active = is_active
            await session.commit()
        else:
            print(f"User with tg_id {tg_id} not found")


async def active_users_by_tag(tags: List[str]):
    async with async_session() as session:
        users = await session.execute(
            select(User.tg_id).filter(User.is_active, User.tag.in_(tags))
        )
    return users.scalars().all()


async def save_mailing_to_db(data: Dict):
    async with async_session() as session:
        async with session.begin():

            photo_id = data.get('msg_photo')
            document_id = data.get('msg_document')
            text = data.get('msg_text')
            tag = data.get('msg_tag')
            btn_text = data.get('btn_text')
            btn_url = data.get('btn_url')

            if isinstance(tag, list):
                tags_as_string = ",".join(tag)
            else:
                tags_as_string = tag

            result = Mailing(
                tag=tags_as_string,
                image_file_id=photo_id,
                document_file_id=document_id,
                text=text,
                button_text=btn_text,
                button_url=btn_url
            )

            session.add(result)

    await session.commit()


async def show_all_mailings():
    async with async_session() as session:
        mailings = await session.execute(
            select(Mailing)
        )
    return mailings.scalars().all()

async def delete_mailing(mailing_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Mailing).where(Mailing.id == mailing_id)
        )
        mailing = result.scalar_one_or_none()

        if mailing:
            await session.delete(mailing)
            await session.commit()
            return mailing
        else:
            return None
