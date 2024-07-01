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

from couple.models import Couple
from users.models import User

from bot.bot.database.couple import (
    get_user_couple,
    create_wish,
    get_couple_user,
    get_user_wishes,
)
from bot.bot.database.users import get_user_by_user_id

from bot.bot.handlers.couple_handlers.couple_wish import (
    callback_couple_wish_menu_handler,
)

from bot.bot.utils.paginated_message import CoupleUserWishPaginatedMessage

from bot.bot.handlers.couple_handlers.couple_wish import (
    callback_couple_wish_menu_handler,
)

couple_user_wish_paginated_message = CoupleUserWishPaginatedMessage(
    object_name="own_wish",
    per_page=10,
    exit_func=callback_couple_wish_menu_handler,
)


async def callback_couple_user_wish_menu_own_wish_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Желания партнера
    """
    user: User = await get_user_by_user_id(callback.from_user.id)
    couple: Couple = await get_user_couple(user)
    if couple_user := await get_couple_user(couple, user):
        couple_user_wishes = await get_user_wishes(couple_user)
        await couple_user_wish_paginated_message.set_data(iterable=couple_user_wishes)

    await couple_user_wish_paginated_message.answer_paginated_message(callback.message)
    await callback.message.delete()


async def register_couple_user_wish_own_wish_menu_handlers(dp: Dispatcher):
    dp.callback_query.register(
        callback_couple_user_wish_menu_own_wish_handler,
        F.data == "couple_wish_menu_couple_user_wish",
    )
    await couple_user_wish_paginated_message.register_paginated_callbacks_handlers(dp)
