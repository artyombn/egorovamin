import logging

from sqlalchemy import BigInteger, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

import os
from dotenv import load_dotenv


load_dotenv(os.path.join('config', '.env'))
engine = create_async_engine(url=os.getenv('DB_URL'))

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    tag: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

class Mailing(Base):
    __tablename__ = 'mailings'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(nullable=True)
    tag: Mapped[str] = mapped_column(nullable=True)
    document_file_id: Mapped[str] = mapped_column(nullable=True)
    image_file_id: Mapped[str] = mapped_column(nullable=True)
    button_text: Mapped[str] = mapped_column(nullable=True)
    button_url: Mapped[str] = mapped_column(nullable=True)

class ButtonResource(Base):
    __tablename__ = 'resources'

    id: Mapped[int] = mapped_column(primary_key=True)
    button_text: Mapped[str] = mapped_column(nullable=True)
    button_url: Mapped[str] = mapped_column(nullable=True)


async def async_main():
    try:
        logging.info("Starting database creation.")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("Database created.")
    except Exception as e:
        logging.error(f"Error while creating database: {e}")