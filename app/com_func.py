import os
import pytz
import json
import base64
import asyncio
from datetime import datetime, timedelta
from functools import wraps
from contextlib import asynccontextmanager
from aiogram.types import Message
from aiogram.filters import Filter
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from dotenv import load_dotenv


from app.database.models import async_session


load_dotenv()

user_list = list(map(int, os.getenv("USERS", "").split(',')))

class User(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in user_list

admin_list = list(map(int, os.getenv("ADMINS", "").split(',')))


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in admin_list


# session context manager
@asynccontextmanager
async def get_session():
    async with async_session() as session:
        try:
            yield session
        finally:
            pass


# decorator factory
def with_session(commit: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with get_session() as session:
                try:
                    result = await func(session, *args, **kwargs)
                    if commit:
                        await session.commit()
                    return result
                except Exception:
                    if commit:
                        await session.rollback()
                    raise
        return wrapper
    return decorator


# функция, которая отправляет сообщение в Pub/sub, чтобы запустить синхронизацию DWH


async def trigger_dwh_pipeline():
    encoded_key = os.environ["RAILWAY_BQ_CONNECTION_JSON"]
    decoded_key = base64.b64decode(encoded_key).decode("utf-8")
    credentials_info = json.loads(decoded_key)
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    publisher = pubsub_v1.PublisherClient(credentials=credentials)
    topic_path = "projects/cheese-analytics-dwh/topics/dwh-sync-trigger"
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, publisher.publish, topic_path, b"trigger")


# границы начала и конца дня
def get_utc_day_bounds(date_time: datetime):
    tz = pytz.timezone("Europe/Chisinau")
    
    # Скорее всего этот участок кода более не нужен
    # Если это были цифры введенные человеком
    if date_time.tzinfo is None:
        date_time = tz.localize(date_time)
    # Эта Все что ниже - важная часть

    # обнуляем дату
    date_time = date_time.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

    # присваиваем дате полночь по кишиневу и делаем это значение стартом дня
    start_of_day = tz.localize(date_time)
    start_of_day = start_of_day.astimezone(pytz.utc)

    # важно, что сначала делаем смещение на 1 день вперед на обнуленную дату
    # присваиваем дате полночь по кишиневу и делаем это значение стартом следующего дня
    end_of_day = date_time + timedelta(days=1)
    end_of_day = tz.localize(end_of_day)
    end_of_day = end_of_day.astimezone(pytz.utc)
    
    return start_of_day, end_of_day


# функция для локализации инпута и now()
def localize_user_input(date_time):
    """Used for naive user input: assume it's in Chisinau local time."""
    if date_time is None:
        return None
    tz = pytz.timezone("Europe/Chisinau")
    return tz.localize(date_time) if date_time.tzinfo is None else date_time.astimezone(tz)

# Фурнкция для правильного отображения времени с часовым поясом
def represent_utc_3(date_time):
    """Used for UTC datetime from DB: convert to Chisinau local time."""
    if date_time is None:
        return None
    tz = pytz.timezone("Europe/Chisinau")
    if date_time.tzinfo is None:
        date_time = pytz.utc.localize(date_time)
    return date_time.astimezone(tz)