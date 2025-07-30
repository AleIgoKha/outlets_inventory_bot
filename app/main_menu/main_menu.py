from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

import app.main_menu.keyboard as kb

main_menu = Router()

admin_list = [524794800, 405514693, 450847990, 7634611527]

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in admin_list


# Главное меню
@main_menu.message(Admin(), Command('start'))
async def start_handler(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    await message.delete()
    sent_message = await message.answer(text='🏠 <b>ГЛАВНОЕ МЕНЮ</b>', reply_markup=kb.main_menu, parse_mode='HTML')
    # Удаляем все другие сообщения, кроме последнего с меню пока не будет 5 сообщений подряд, которые уже удалены
    message_id = sent_message.message_id
    chat_id = sent_message.chat.id
    for id in range(message_id - 1, 0, -1):
        try:
            bad_tries = 0
            await bot.delete_message(chat_id=chat_id, message_id=id)
        except TelegramBadRequest:
            bad_tries += 1
            if bad_tries <= 5:
                continue
            else:
                break

# Возвращение через колбэк в главное меню или при вызове функции
@main_menu.callback_query(F.data == 'main:menu')
async def main_menu_handler(callback:CallbackQuery, state: FSMContext,):
    await state.clear()
    await callback.message.edit_text(text='🏠 <b>ГЛАВНОЕ МЕНЮ</b>', reply_markup=kb.main_menu, parse_mode='HTML')