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
)
from bot.bot.database.users import get_user_by_user_id

from bot.bot.handlers.couple_handlers.couple_wish.own_wish import (
    callback_couple_wish_menu_own_wish_handler,
)


class CreateWishState(StatesGroup):
    """
    Состояние создания желания
    """

    wish_main = State(state="wish_main")
    change_wish_description_get_message = State("change_wish_description_get_message")
    set_date_to = State(state="set_date_to")


class WishStorage:
    """
    Хранилище данных о желании
    """

    description = ""
    date_to: Optional[datetime.date] = None

    def __init__(
        self, description: str = None, date_to: Optional[datetime.date] = None
    ) -> None:
        self.description = description
        self.date_to = date_to


async def callback_couple_wish_create_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Переход в меню создания желания
    """
    state_data = await state.get_data()
    wish: WishStorage = state_data.get("wish", WishStorage())
    await state.set_data({"wish": wish})

    if message_wish_success_created := (await state.get_data()).get(
        "message_wish_success_created"
    ):
        await callback.message.bot.delete_message(message_wish_success_created)

    await state.set_state(CreateWishState.wish_main)
    await message_couple_wish_create_handler(callback.message, state)


async def message_couple_wish_create_handler(message: types.Message, state: FSMContext):
    """
    Меню создания желания
    """
    state_data = await state.get_data()
    wish: WishStorage = state_data.get("wish", WishStorage())
    wish_description = wish.description if wish.description else ""
    wish_date_to = wish.date_to.strftime("%d.%m.%Y") if wish.date_to else ""
    await state.set_data({"wish": wish})

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Изменить описание", callback_data="change_wish_description"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Изменить дату исполнения", callback_data="change_wish_date_to"
        )
    )
    if wish.description:
        builder.row(
            types.InlineKeyboardButton(
                text="Создать ✅", callback_data="create_wish_button_submit"
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад ◀️", callback_data="couple_wish_create_backward"
        )
    )

    await message.delete()
    await message.answer(
        "Ваше желание:\n\n"
        f"<b>Описание*:</b> {wish_description}\n\n"
        f"<b>Дата исполнения:</b> {wish_date_to}",
        reply_markup=builder.as_markup(),
    )


async def callback_change_wish_description_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Ввод описания желания
    """
    get_descriprion_message = await callback.message.answer(
        "Введите описание своего желания",
    )
    await state.update_data(get_descriprion_message=get_descriprion_message)
    await state.set_state(CreateWishState.change_wish_description_get_message)
    await callback.message.delete()


async def message_change_wish_description_get_message_handler(
    message: types.Message, state: FSMContext
):
    """
    Получение описания желания
    """
    state_data = await state.get_data()
    wish: WishStorage = state_data.get("wish")

    if not wish:
        await message.answer(f"Что-то пошло не так. Попробуйте сначала")
        return

    description = message.text
    wish.description = description

    if get_descriprion_message := state_data.get("get_descriprion_message"):
        await message.bot.delete_message(
            chat_id=message.chat.id, message_id=get_descriprion_message.message_id
        )

    await state.set_data({"wish": wish})
    await state.set_state(CreateWishState.wish_main)
    await message_couple_wish_create_handler(message, state)


async def callback_change_wish_date_to_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Выбор даты исполнения желания
    """
    await callback.message.delete()
    await callback.message.answer(
        "Выберите дату: ",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(callback.from_user)
        ).start_calendar(),
    )
    await state.set_state(state=CreateWishState.set_date_to)


async def process_dialog_calendar(
    callback: types.CallbackQuery,
    callback_data,
    state: FSMContext,
    bot: Bot,
):
    """
    Процесс назначения даты исполнения желания
    """
    state_data = await state.get_data()
    wish: WishStorage = state_data.get("wish")

    if not wish:
        await callback.message.answer(f"Что-то пошло не так. Попробуйте сначала")
        await message_couple_wish_create_handler(callback.message, state)
        return

    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback.from_user)
    ).process_selection(callback, callback_data)
    if selected:
        state_data = await state.get_data()
        wish.date_to = date
        await state.set_data({"wish": wish})

        await state.set_state(CreateWishState.wish_main)
        await message_couple_wish_create_handler(callback.message, state)


async def callback_create_wish_button_submit_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Создание желания
    """
    state_data = await state.get_data()
    wish: WishStorage = state_data.get("wish")
    user: User = await get_user_by_user_id(callback.message.chat.id)
    couple: Couple = await get_user_couple(user)

    if not wish or not couple or not user or not wish.description:
        await callback.message.answer(f"Что-то пошло не так. Попробуйте сначала")
        return

    await create_wish(couple, user, wish.description, wish.date_to)
    message_wish_success_created = await callback.message.answer(
        f"Желание успешно создано!"
    )
    await state.update_data(message_wish_success_created=message_wish_success_created)

    if couple_user := await get_couple_user(couple, user):
        await bot.send_message(
            chat_id=couple_user.user_id, text="Партнер создал новое желание!"
        )

    await state.clear()
    await callback_couple_wish_menu_own_wish_handler(callback, state)


async def callback_couple_wish_create_backward_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Возвращение в меню желаний
    """
    await callback_couple_wish_menu_own_wish_handler(callback, state)


async def register_couple_wish_create_handlers(dp: Dispatcher):
    dp.callback_query.register(
        callback_couple_wish_create_handler,
        F.data == "couple_wish_menu_create",
    )

    dp.callback_query.register(
        callback_change_wish_description_handler,
        F.data == "change_wish_description",
    )

    dp.message.register(
        message_couple_wish_create_handler,
        CreateWishState.wish_main,
    )
    dp.message.register(
        message_change_wish_description_get_message_handler,
        CreateWishState.change_wish_description_get_message,
    )

    dp.callback_query.register(
        callback_change_wish_date_to_handler,
        F.data == "change_wish_date_to",
    )

    dp.callback_query.register(
        process_dialog_calendar,
        DialogCalendarCallback.filter(),
        CreateWishState.set_date_to,
    )

    dp.callback_query.register(
        callback_create_wish_button_submit_handler,
        F.data == "create_wish_button_submit",
    )

    dp.callback_query.register(
        callback_couple_wish_create_backward_handler,
        F.data == "couple_wish_create_backward",
    )
