import os

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv(os.path.join('config', '.env'))
scheduler = AsyncIOScheduler()
bot = Bot(token=os.getenv('TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
