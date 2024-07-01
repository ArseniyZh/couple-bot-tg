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

from bot.bot.utils.paginated_message import OwnWishPaginatedMessage

from bot.bot.handlers.couple_handlers.couple_wish import (
    callback_couple_wish_menu_handler,
)

own_wish_paginated_message = OwnWishPaginatedMessage(
    object_name="own_wish",
    per_page=10,
    exit_func=callback_couple_wish_menu_handler,
)


async def callback_couple_wish_menu_own_wish_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Мои желания
    """
    user = await get_user_by_user_id(callback.from_user.id)
    user_wishes = await get_user_wishes(user)

    await own_wish_paginated_message.set_data(iterable=user_wishes)
    await own_wish_paginated_message.answer_paginated_message(callback.message)
    await callback.message.delete()
    await state.clear()


async def register_couple_wish_own_wish_menu_handlers(dp: Dispatcher):
    dp.callback_query.register(
        callback_couple_wish_menu_own_wish_handler,
        F.data == "couple_wish_menu_own_wish",
    )
    await own_wish_paginated_message.register_paginated_callbacks_handlers(dp)
