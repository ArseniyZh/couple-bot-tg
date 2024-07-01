from typing import Optional
import datetime

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram_calendar import (
    DialogCalendar,
    DialogCalendarCallback,
    get_user_locale,
)

from couple.models import Couple, Wish
from users.models import User

from bot.bot.database.couple import (
    get_user_couple,
    create_wish,
    get_couple_user,
    get_wish_by_id,
)
from bot.bot.database.users import get_user_by_user_id

from bot.bot.handlers.couple_handlers.couple_wish.own_wish import (
    callback_couple_wish_menu_own_wish_handler,
)
from bot.bot.handlers.couple_handlers.couple_wish.wish_change.state import (
    ChangeWishState,
)
from bot.bot.handlers.couple_handlers.couple_wish.wish_change.menu import (
    command_wish_change_menu_handler,
)


async def callback_own_wish_get_wish_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    await callback.message.delete()
    await command_wish_get_wish_handler(message=callback.message, state=state)


async def command_wish_get_wish_handler(message: types.Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Назад ◀️", callback_data="couple_wish_menu_own_wish"
        )
    )

    await state.set_state(ChangeWishState.get_wish)
    prev_message = await message.answer(
        (
            "Пришли идентификатор желания. Пример:\n"
            'У такого желания <b>"[Желание #43]</b>" идентификатор - 43'
        ),
        reply_markup=builder.as_markup(),
    )
    await state.update_data(prev_message=prev_message)
    await state.set_state(ChangeWishState.get_wish)


async def message_wish_get_wish_handler(
    message: types.CallbackQuery, state: FSMContext
):
    wish_id = message.text

    prev_message: types.Message = (await state.get_data()).get("prev_message")
    await prev_message.delete()
    if not wish_id.isdigit():
        await message.delete()
        await command_wish_get_wish_handler(message, state)
        return

    user = await get_user_by_user_id(message.from_user.id)
    wish: Wish = await get_wish_by_id(int(wish_id))
    if not wish or wish.user != user:
        await message.delete()
        await message.answer("Желание не найдено")
        await command_wish_get_wish_handler(message, state)
        return

    await state.update_data(wish=wish)
    await state.set_state(ChangeWishState.wish_change_menu)
    await message.delete()
    await command_wish_change_menu_handler(message, state)


async def register_wish_change_get_wish_handlers(dp: Dispatcher):
    dp.callback_query.register(
        callback_own_wish_get_wish_handler,
        F.data == "own_wish_change",
    )
    dp.message.register(
        message_wish_get_wish_handler,
        ChangeWishState.get_wish,
    )
