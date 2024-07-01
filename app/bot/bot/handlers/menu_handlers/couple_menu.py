from aiogram.types import Message

from aiogram import Dispatcher, types, F
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

from bot.bot.handlers.couple_handlers import (
    command_couple_info_handler,
    command_couple_create_handler,
    command_couple_join_handler,
)


class CoupleJoinState(StatesGroup):
    get_unique_id = State(state="get_unique_id")


async def command_couple_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Меню пары
    """
    state_data = await state.get_data()
    user: User = state_data.get(
        "user", await get_user_by_user_id(callback.message.chat.id)
    )
    couple: Couple = await get_user_couple(user)

    builder = InlineKeyboardBuilder()
    if not couple:
        builder = InlineKeyboardBuilder()

        builder.row(
            types.InlineKeyboardButton(
                text="❤️ Создать пару", callback_data="couple_create"
            )
        )
        builder.row(
            types.InlineKeyboardButton(
                text="❤️ Присоединиться к паре", callback_data="couple_join"
            )
        )

        await callback.message.answer("Меню пары", reply_markup=builder.as_markup())
    else:
        await command_couple_info_handler(callback.message, state)

    await callback.message.delete()


async def callback_couple_menu_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Переход в главное меню пары
    """
    await callback.message.delete()
    await command_couple_info_handler(callback.message, state)


async def callback_couple_create_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Переход к созданию пары
    """
    await callback.message.delete()
    await command_couple_create_handler(callback.message, state)


async def callback_couple_join_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Переход к присоединению к паре
    """
    await callback.message.delete()
    await command_couple_join_handler(callback.message, state)


async def register_couple_menu_handlers(dp: Dispatcher):
    dp.callback_query.register(
        command_couple_menu_handler,
        F.data == "couple_main_menu",
    )

    dp.callback_query.register(
        callback_couple_menu_handler,
        F.data == "couple_info_menu",
    )
    dp.callback_query.register(
        callback_couple_create_handler,
        F.data == "couple_create",
    )
    dp.callback_query.register(
        callback_couple_join_handler,
        F.data == "couple_join",
    )
