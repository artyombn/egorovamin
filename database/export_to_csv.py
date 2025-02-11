import pandas as pd
from sqlalchemy import select
from database.models import User, async_session


async def export_users_to_csv(file_name: str):
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        users_data = [
            {
                'id': user.id,
                'tg_id': user.tg_id,
                'username': user.username,
                'name': user.name,
                'email': user.email,
                'tag': user.tag,
                'is_active': user.is_active
            }
            for user in users
        ]

        df = pd.DataFrame(users_data)
        df.columns = ['ID', 'Telegram ID', 'Username', 'Имя пользователя', 'Электронная почта', 'Тег', 'Активен']

        df.to_csv(file_name, index=False, encoding='utf-8-sig')

        file_path = 'users_data.csv'

    return file_path