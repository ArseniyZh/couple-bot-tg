from django.conf import settings

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from bot.bot.handlers import register_all_handlers
from bot.bot.commands.base import commands_classes_dict


TOKEN = settings.BOT_TOKEN

storage = MemoryStorage()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


async def set_commands(bot: Bot):
    """
    Установка всех комманд бота
    """
    commands_classes = (await commands_classes_dict(check_perm=False)).values()
    _commands = []
    for i in commands_classes:
        _commands.extend(i)
    commands = [
        types.BotCommand(command=_command.command, description=_command.description)
        for _command in _commands
    ]
    await bot.set_my_commands(commands)


async def main():
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    await register_all_handlers(dp)
    await set_commands(bot)

    # And the run events dispatching
    await dp.start_polling(bot)
