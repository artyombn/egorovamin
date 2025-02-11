from database.models import async_session
from database.models import User
from sqlalchemy import select, update, delete


async def check_user_exists(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user and user.tag:
            return user.name
        else:
            return False


async def get_tg_user_info(tg_id: int, username: str):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, username=username))
            await session.commit()

async def get_user_name(tg_id: int, name: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if user:
            user.name = name
            await session.commit()
        else:
            print(f"User with tg_id {tg_id} not found")

async def get_user_email(tg_id: int, email: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if user:
            user.email = email
            await session.commit()
        else:
            print(f"User with tg_id {tg_id} not found")


async def get_user_tag(email: str, tag: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            user.tag = tag
            await session.commit()
        else:
            print(f"User with email {email} not found")