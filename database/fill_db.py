from sqlalchemy.ext.asyncio import AsyncSession
from database.models import engine, User, Mailing, ButtonResource


async def async_fill_db():
    async with AsyncSession(engine) as session:
        artyombn = User(
            id=1,
            tg_id=237716145,
            username='artyombn',
            name='Артём',
            email='balabashinan@gmail.com',
            tag='B2',
            is_active=True,
        )

        milena = User(
            id=2,
            tg_id=631809226,
            username='egorovamln',
            name='Милена',
            email='egorovamln@icloud.com',
            tag='C1',
            is_active=True,
        )


        session.add(artyombn)
        session.add(milena)

        mailing1 = Mailing(
            id=1,
            text='Проверка новой рассылки по тегу',
            tag='B1',
            document_file_id=None,
            image_file_id='AgACAgIAAxkBAAIETWbjU74ga74oXBOtSnfhRseKAvZJAAJj6DEbL_0ZSw86DgSZemaaAQADAgADeQADNgQ',
            button_text='Нажми сюда',
            button_url='https://text.ru',
        )

        session.add(mailing1)

        resourse1 = ButtonResource(
            id=1,
            button_text='Подготовься к путешествию',
            button_url='https://drive.google.com/file/d/1wYDlUQ7-ZBEOR0-JGD_24zqGvDZX-8Nt/view?usp=sharing',
        )

        resourse2 = ButtonResource(
            id=2,
            button_text='Как спланировать обучение правильно',
            button_url='https://drive.google.com/file/d/1uhPysXTQwqe-aKXGU5UP0G8i2i6VjaV1/view?usp=sharing',
        )

        resourse3 = ButtonResource(
            id=3,
            button_text='Подборка подкастов на английском',
            button_url='https://teletype.in/@egorovamln/english_podcast_jam',
        )


        session.add(resourse1)
        session.add(resourse2)
        session.add(resourse3)

        await session.commit()