import os
import asyncio
import redis.asyncio as aioredis
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from dotenv import load_dotenv

from app.message_remover import messages_remover
from app.main_menu.main_menu import main_menu

from app.main_menu.outlets_menu.outlets_menu import outlets_menu
from app.main_menu.outlets_menu.outlet_menu.outlet_menu import outlet_menu
from app.main_menu.outlets_menu.outlet_menu.outlet_operations.outlet_operations import outlet_operations
from app.main_menu.outlets_menu.outlet_menu.stock_menu.stock_menu import stock_menu
from app.main_menu.outlets_menu.outlet_menu.outlet_statistics.outlet_statistics import outlet_statistics
from app.main_menu.outlets_menu.outlet_menu.report_menu.report_menu import report_menu

from app.database.models import async_main
from app.middlewares import MessagesRemover, OutOfPagesAnswer

async def main():
    load_dotenv()
    redis = await aioredis.from_url(os.getenv(f'REDIS_URL'))
    bot = Bot(token=os.getenv('TG_TOKEN'))
    bot.redis = redis
    dp = Dispatcher(storage=RedisStorage(redis))
    dp.message.middleware(MessagesRemover())
    dp.callback_query.middleware(OutOfPagesAnswer())
    dp.include_routers(main_menu,
                       outlets_menu,
                       outlet_menu,
                       outlet_operations,
                       stock_menu,
                       outlet_statistics,
                       report_menu,
                       messages_remover)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)
    
async def on_startup(*args):
    await async_main()
    print('The application has started')

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass