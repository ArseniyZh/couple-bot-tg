from aiogram import Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message

from couple.models import Couple

from bot.bot.commands import CoupleCommands, GeneralCommands
from bot.bot.database.users import get_user_by_user_id
from bot.bot.database.couple import get_user_couple, create_couple
from bot.bot.handlers.couple_handlers.couple_info import command_couple_info_handler


async def command_couple_create_handler(message: Message, state: FSMContext):
    """
    Создание пары
    """
    user = await get_user_by_user_id(message.chat.id)
    if not user:
        await message.answer(
            f"Сначала зарегистрируйтесь - {GeneralCommands.register.value}",
        )
        return

    if await get_user_couple(user):
        await message.answer(
            f"У вас уже есть пара",
        )
        return

    couple: Couple = await create_couple(user_1=user)
    await message.answer(
        f"Пара создана! \n"
        f"Код для приглашения - `{couple.unique_id}`\n\n"
        "Поделитесь этим кодом со своим партнером.",
        parse_mode="Markdown",
    )
    await command_couple_info_handler(message, state)


async def register_couple_create_handler(dp: Dispatcher):
    dp.message.register(
        command_couple_create_handler,
        Command(CoupleCommands.couple_create.command),
    )
