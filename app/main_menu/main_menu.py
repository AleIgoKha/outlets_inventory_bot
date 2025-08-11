from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext

import app.main_menu.keyboard as kb
from app.com_func import User, Admin

main_menu = Router()


# Главное меню
@main_menu.message(or_f(User(), Admin()), Command('start'))
async def start_handler(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.delete()
    
    # удаляем все id всех сообщений в чате
    redis = bot.redis
    chat_id = message.chat.id
    key = f"chat:{chat_id}:messages"
    message_ids = await redis.lrange(key, 0, -1)  # Get all stored message IDs

    for msg_id in message_ids:
        try:
            await bot.delete_message(chat_id, int(msg_id))
        except Exception:
            pass  # Ignore errors (e.g., message already deleted)

    await redis.delete(key)  # Clear the stored list
    await redis.close()
    
    # печатаем сообщение и сохраняем его id
    sent_message = await message.answer(text='🏠 <b>ГЛАВНОЕ МЕНЮ</b>', reply_markup=kb.main_menu, parse_mode='HTML')
    message_id = sent_message.message_id
    await redis.rpush(f"chat:{chat_id}:messages", message_id)
    await redis.close()
    
    
    
    # # Удаляем все другие сообщения, кроме последнего с меню пока не будет 5 сообщений подряд, которые уже удалены
    # message_id = sent_message.message_id
    # chat_id = sent_message.chat.id
    # for id in range(message_id - 1, 0, -1):
    #     try:
    #         bad_tries = 0
    #         await bot.delete_message(chat_id=chat_id, message_id=id)
    #     except TelegramBadRequest as e:
    #         print(e)
    #         bad_tries += 1
    #         if bad_tries <= 5:
    #             continue
    #         else:
    #             break
            
            

            

# Возвращение через колбэк в главное меню или при вызове функции
@main_menu.callback_query(F.data == 'main:menu')
async def main_menu_handler(callback:CallbackQuery, state: FSMContext,):
    await state.clear()
    await callback.message.edit_text(text='🏠 <b>ГЛАВНОЕ МЕНЮ</b>', reply_markup=kb.main_menu, parse_mode='HTML')