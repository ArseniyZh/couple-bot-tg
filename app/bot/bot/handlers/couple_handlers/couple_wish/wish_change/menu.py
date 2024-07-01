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
    save_wish,
    delete_wish,
)
from bot.bot.database.users import get_user_by_user_id

from bot.bot.handlers.couple_handlers.couple_wish.own_wish import (
    callback_couple_wish_menu_own_wish_handler,
)
from bot.bot.handlers.couple_handlers.couple_wish.wish_change.state import (
    ChangeWishState,
)


async def command_wish_change_menu_handler(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    wish: Wish = state_data.get("wish")
    wish_description = wish.description if wish.description else ""
    wish_date_to = wish.date_to.strftime("%d.%m.%Y") if wish.date_to else ""

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Изменить описание", callback_data="change_wish_description_change"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Изменить дату исполнения", callback_data="change_wish_date_to_change"
        )
    )
    if wish_description:
        builder.row(
            types.InlineKeyboardButton(
                text="Сохранить ✅", callback_data="save_wish_button_submit_change"
            )
        )
    builder.row(
        types.InlineKeyboardButton(
            text="Удалить ❌", callback_data="delete_wish_button_change"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад ◀️", callback_data="couple_wish_menu_own_wish"
        )
    )

    prev_message = await message.answer(
        "Ваше желание:\n\n"
        f"<b>Описание*:</b> {wish_description}\n\n"
        f"<b>Дата исполнения:</b> {wish_date_to}",
        reply_markup=builder.as_markup(),
    )
    await state.update_data(prev_message=prev_message)


async def callback_change_wish_description_change_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Ввод описания желания
    """
    get_descriprion_message = await callback.message.answer(
        "Введите описание своего желания",
    )
    await state.update_data(get_descriprion_message=get_descriprion_message)
    await state.set_state(ChangeWishState.change_wish_description_get_message)
    await callback.message.delete()


async def message_change_wish_description_get_message__change_handler(
    message: types.Message, state: FSMContext
):
    """
    Получение описания желания
    """
    state_data = await state.get_data()
    wish: Wish = state_data.get("wish")

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
    await state.set_state(ChangeWishState.wish_change_menu)
    await command_wish_change_menu_handler(message, state)


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
    await state.set_state(state=ChangeWishState.set_date_to_change)


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
    wish: Wish = state_data.get("wish")

    if not wish:
        await callback.message.answer(f"Что-то пошло не так. Попробуйте сначала")
        await command_wish_change_menu_handler(callback.message, state)
        return

    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback.from_user)
    ).process_selection(callback, callback_data)
    if selected:
        state_data = await state.get_data()
        wish.date_to = date
        await state.set_data({"wish": wish})
        await callback.message.delete()
        await state.set_state(ChangeWishState.wish_change_menu)
        await command_wish_change_menu_handler(callback.message, state)


async def callback_save_wish_button_submit_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Сохранение желания
    """
    state_data = await state.get_data()
    wish: Wish = state_data.get("wish")
    user: User = await get_user_by_user_id(callback.message.chat.id)
    couple: Couple = await get_user_couple(user)

    if not wish or not couple or not user or not wish.description:
        await callback.message.answer(f"Что-то пошло не так. Попробуйте сначала")
        return

    await save_wish(wish)

    if couple_user := await get_couple_user(couple, user):
        await bot.send_message(
            chat_id=couple_user.user_id, text="Партнер изменил одно из своих желаний!"
        )

    await state.clear()
    await callback_couple_wish_menu_own_wish_handler(callback, state)


async def callback_delete_wish_button_submit_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Удаление желания
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Да, удалить ❌", callback_data="delete_wish"),
        types.InlineKeyboardButton(
            text="Нет, оставить ✅", callback_data="not_delete_wish"
        ),
    )

    await callback.message.answer(
        callback.message.text, reply_markup=builder.as_markup()
    )
    await callback.message.delete()


async def callback_delete_wish(callback: types.CallbackQuery, state: FSMContext):
    """
    Удаление желания
    """
    state_data = await state.get_data()
    wish: Wish = state_data.get("wish")

    await delete_wish(wish)
    await state.clear()
    await callback_couple_wish_menu_own_wish_handler(callback, state)


async def callback_not_delete_wish(callback: types.CallbackQuery, state: FSMContext):
    """
    Удаление желания
    """
    await callback.message.delete()
    await command_wish_change_menu_handler(callback.message, state)


async def register_wish_change_menu_handlers(dp: Dispatcher):
    dp.message.register(
        command_wish_change_menu_handler,
        ChangeWishState.wish_change_menu,
    )

    dp.callback_query.register(
        callback_change_wish_description_change_handler,
        F.data == "change_wish_description_change",
    )
    dp.message.register(
        message_change_wish_description_get_message__change_handler,
        ChangeWishState.change_wish_description_get_message,
    )

    dp.callback_query.register(
        callback_change_wish_date_to_handler,
        F.data == "change_wish_date_to_change",
    )
    dp.callback_query.register(
        process_dialog_calendar,
        DialogCalendarCallback.filter(),
        ChangeWishState.set_date_to_change,
    )

    dp.callback_query.register(
        callback_save_wish_button_submit_handler,
        F.data == "save_wish_button_submit_change",
    )

    dp.callback_query.register(
        callback_delete_wish_button_submit_handler,
        F.data == "delete_wish_button_change",
    )

    dp.callback_query.register(
        callback_delete_wish,
        F.data == "delete_wish",
    )

    dp.callback_query.register(
        callback_not_delete_wish,
        F.data == "not_delete_wish",
    )
