from aiogram.types import Message

from aiogram import Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from couple.models import Couple
from users.models import User

from bot.bot.commands import CoupleCommands, GeneralCommands
from bot.bot.database.users import get_user_by_user_id
from bot.bot.database.couple import (
    get_user_couple,
    join_to_couple,
    get_couple_by_unique_id,
    get_couple_user,
)


class CoupleJoinState(StatesGroup):
    get_unique_id = State(state="get_unique_id")


async def command_main_menu_handler(message: Message, state: FSMContext):
    """
    Главное меню
    """

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Меню отношений ❤️", callback_data="couple_main_menu"
        )
    )
    await message.answer("Главное меню", reply_markup=builder.as_markup())


async def register_main_menu_handlers(dp: Dispatcher):
    dp.message.register(
        command_main_menu_handler,
        Command(GeneralCommands.main_menu.command),
    )
