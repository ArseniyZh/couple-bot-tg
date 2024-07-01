from typing import Any

from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


class PaginatedMessage:
    def __init__(
        self,
        iterable: list = None,
        object_name: str = None,
        page: int = 0,
        per_page: int = 10,
        exit_func: callable = None,
    ) -> None:
        self.exit_func = exit_func
        self.iterable = iterable if iterable is not None else []
        if object_name is None or object_name == "":
            raise ValueError("object_name can't be None or empty")
        self.object_name = object_name
        self.page = page
        self.per_page = per_page

    @property
    def current_iterable(self):
        return self.iterable[
            self.page * self.per_page : (self.page + 1) * self.per_page
        ]

    def __get_page_backward_callback_name(self):
        return f"page_backward_{self.object_name}"

    def __get_page_forward_callback_name(self):
        return f"page_forward_{self.object_name}"

    def __get_exit_callback_name(self):
        return f"exit_{self.object_name}"

    async def get_current_base_keyboard(self) -> list[list[types.InlineKeyboardButton]]:
        keyboard = []
        
        # row 1
        keyboard.append(
            [
            types.InlineKeyboardButton(
                text="<",
                callback_data=(
                    self.__get_page_backward_callback_name()
                    if self.page > 0
                    else "none"
                ),
            ),
            types.InlineKeyboardButton(
                text=f"Страница {self.page + 1}/{len(self.iterable) // self.per_page + 1}",
                callback_data="none",
            ),
            types.InlineKeyboardButton(
                text=">",
                callback_data=(
                    self.__get_page_forward_callback_name()
                    if (len(self.current_iterable) == self.per_page)
                    and (self.page < len(self.iterable) - (self.page) * self.per_page)
                    else "none"
                ),
            ),
        ]
        )

        if self.exit_func is not None:
            # row 2
            keyboard.append(
                [
                    types.InlineKeyboardButton(
                    text="Выход",
                    callback_data=self.__get_exit_callback_name(),
                ),
                ]
            )

        return keyboard

    async def manage_builder(self, builder: InlineKeyboardBuilder):
        current_base_keyboard: list[list[types.InlineKeyboardButton]] = (
            await self.get_current_base_keyboard()
        )

        for row in current_base_keyboard:
            builder.row(*row)

    async def get_builder_markup(self) -> types.InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        await self.manage_builder(builder)
        return builder.as_markup()

    def get_formatted_object(self, _object: Any) -> str:
        return str(_object)

    async def get_message_text(self) -> str:
        _iterable = self.current_iterable
        message = ""

        for _object in _iterable:
            message += self.get_formatted_object(_object) + "\n"

        return message

    async def answer_paginated_message(self, message: types.Message):
        await message.answer(
            await self.get_message_text(), reply_markup=await self.get_builder_markup()
        )

    async def callback_backward_page_handler(
        self, callback: types.CallbackQuery, state: FSMContext
    ):
        self.page -= 1
        await callback.message.delete()

        await self.answer_paginated_message(callback.message)

    async def callback_forward_page_handler(
        self, callback: types.CallbackQuery, state: FSMContext
    ):
        self.page += 1
        await callback.message.delete()

        await self.answer_paginated_message(callback.message)

    async def callback_exit_handler(self, *args, **kwargs):
        if self.exit_func is not None:
            await self.exit_func(*args, **kwargs)

    async def set_data(
        self,
        iterable: list = None,
        object_name: str = None,
        page: int = None,
        per_page: int = None,
    ):
        self.iterable = iterable if iterable is not None else self.iterable
        self.object_name = object_name if object_name is not None else self.object_name
        self.page = page if page is not None else self.page
        self.per_page = per_page if per_page is not None else self.per_page

    async def clear_data(self):
        self.iterable = []
        self.page = 0
        self.per_page = 10

    async def register_paginated_callbacks_handlers(self, dp: Dispatcher):
        dp.callback_query.register(
            self.callback_backward_page_handler,
            F.data == self.__get_page_backward_callback_name(),
        )
        dp.callback_query.register(
            self.callback_forward_page_handler,
            F.data == self.__get_page_forward_callback_name(),
        )
        dp.callback_query.register(
            self.callback_exit_handler, F.data == self.__get_exit_callback_name()
        )
