import asyncio
import logging

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config.services import scheduler, bot
from routers import router as main_router
from database.models import async_main
from database.fill_db import async_fill_db


async def main():
    logging.basicConfig(level=logging.INFO)
    # await async_main()
    # await bot.delete_webhook(drop_pending_updates=True)

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(main_router)

    # await async_fill_db()

    logging.info("Starting scheduler...")
    scheduler.start()

    logging.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
