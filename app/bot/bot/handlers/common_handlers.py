from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from bot.bot.commands import GeneralCommands, formatted_commands_message
from bot.bot.handlers.menu_handlers.main_menu_handlers import command_main_menu_handler


async def command_start_handler(message: Message, state: FSMContext):
    """
    Реагирует на команду `/start`
    """
    await message.answer(
        f"Чтобы посмотреть список команд - отправьте {GeneralCommands.commands_list.value}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await command_main_menu_handler(message, state)


async def command_commands_list_handler(message: Message):
    """
    Реагирует на команду `/commands_list`
    """
    commands_message = (
        "Список доступных команд: \n\n"
        + await formatted_commands_message(user_id=message.chat.id)
    )
    await message.answer(commands_message)


async def register_common_handlers(dp: Dispatcher):
    dp.message.register(command_start_handler, Command(GeneralCommands.start.command))
    dp.message.register(
        command_commands_list_handler, Command(GeneralCommands.commands_list.command)
    )
