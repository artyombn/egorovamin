from config.services import bot


async def send_reminder(chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text="Пожалуйста, поделись своими данными, чтобы я могла отправлять тебе полезные ресурсы.\nОбещаю не спамить!)\n\nНажми на команду /start",
    )