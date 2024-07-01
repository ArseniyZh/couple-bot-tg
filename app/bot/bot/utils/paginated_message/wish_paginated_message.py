from typing import Any, Coroutine

from aiogram.utils.keyboard import InlineKeyboardBuilder
from .base import *

from couple.models import Wish


class WishPaginatedMessage(PaginatedMessage):
    async def get_formatted_object(self, _object: Wish) -> str:
        formatted_object = (
            f"<b>[Желание #{_object.id}]</b>\n"
            f"<pre>{_object.description}"
        )

        if formatted_date_to := _object.formatted_date_to:
            formatted_object += (
                f"\n\n\n🕒 Желаемая дата исполнения: <code>{formatted_date_to}</code>"
            )
            
        formatted_object += "</pre>"

        return formatted_object

    async def callback_exit_handler(
        self, callback: types.CallbackQuery, state: FSMContext
    ):
        await self.exit_func(callback, state)


class OwnWishPaginatedMessage(WishPaginatedMessage):
    async def manage_builder(self, builder: InlineKeyboardBuilder):
        await super().manage_builder(builder)
        builder.row(
            types.InlineKeyboardButton(
                text="Добавить желание ✅", callback_data="couple_wish_menu_create"
            ),
            types.InlineKeyboardButton(
                text="Изменить желание", callback_data="own_wish_change"
            ),
        )

    async def get_message_text(self) -> str:
        message = "Мои желания:\n\n"

        for object in self.current_iterable:
            message += (await self.get_formatted_object(object)) + "\n\n"
        if not self.current_iterable:
            message += "Нет желаний"

        return message


class CoupleUserWishPaginatedMessage(WishPaginatedMessage):
    async def get_message_text(self) -> str:
        message = "Желания партнера:\n\n"

        for object in self.current_iterable:
            message += (await self.get_formatted_object(object)) + "\n\n"
        if not self.current_iterable:
            message += "Нет желаний"

        return message
