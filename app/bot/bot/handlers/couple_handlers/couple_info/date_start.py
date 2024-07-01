from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Dispatcher, Bot, types, F

from aiogram_calendar import (
    DialogCalendar,
    DialogCalendarCallback,
    get_user_locale,
)

from couple.models import Couple
from users.models import User

from bot.bot.database.users import get_user_by_user_id
from bot.bot.database.couple import (
    get_user_couple,
    reset_date_start,
    set_date_start,
    get_couple_user,
)
from bot.bot.handlers.couple_handlers.couple_info import command_couple_info_handler


class SetDateStart(StatesGroup):
    set_date_start = State(state="set_date_start")


async def callback_couple_date_start_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Меню для назначения даты начала отношений
    """
    state_data = await state.get_data()
    user: User = state_data.get(
        "user", await get_user_by_user_id(callback.from_user.id)
    )
    couple: Couple = state_data.get("couple", await get_user_couple(user))

    builder = InlineKeyboardBuilder()
    first_row = [
        types.InlineKeyboardButton(
            text="Поставить дату 🕒", callback_data="couple_date_start_set"
        ),
    ]

    if couple.date_start:
        first_row.append(
            types.InlineKeyboardButton(
                text="Сбросить дату ❌", callback_data="couple_date_start_reset"
            ),
        )
    builder.row(*first_row)
    builder.row(
        types.InlineKeyboardButton(
            text="Назад", callback_data="couple_date_start_backward"
        ),
    )

    couple_date_message = "Дата начала отношений"
    if formatted_date_start := couple.formatted_date_start:
        couple_date_message += f": {formatted_date_start}"

    await callback.message.delete()
    await callback.message.answer(couple_date_message, reply_markup=builder.as_markup())


async def callback_couple_date_start_set_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Сообщение с выбором даты
    """
    await callback.message.answer(
        "Выберите дату: ",
        reply_markup=await DialogCalendar(
            locale=await get_user_locale(callback.from_user)
        ).start_calendar(),
    )

    await state.set_state(state=SetDateStart.set_date_start)
    await callback.message.delete()


async def process_dialog_calendar(
    callback_query: types.CallbackQuery,
    callback_data,
    state: FSMContext,
    bot: Bot,
):
    """
    Хендлер после выбора даты. Процесс смены даты
    """
    selected, date = await DialogCalendar(
        locale=await get_user_locale(callback_query.from_user)
    ).process_selection(callback_query, callback_data)

    if selected:
        state_data = await state.get_data()
        user: User = state_data.get(
            "user", await get_user_by_user_id(callback_query.from_user.id)
        )
        couple: Couple = state_data.get("couple", await get_user_couple(user))

        await set_date_start(couple, date)
        await state.set_state(state=None)

        if couple_user := await get_couple_user(couple, user):
            await bot.send_message(
                chat_id=couple_user.user_id,
                text=f"Партнер поменял дату начала отношений на {date.strftime("%d.%m.%Y")}",
            )

        await callback_query.message.delete()
        await command_couple_info_handler(message=callback_query.message, state=state)


async def callback_couple_date_start_reset_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Сброс даты начала отношений
    """
    state_data = await state.get_data()
    user: User = state_data.get(
        "user", await get_user_by_user_id(callback.from_user.id)
    )
    couple: Couple = state_data.get("couple", await get_user_couple(user))

    await reset_date_start(couple)

    if couple_user := await get_couple_user(couple, user):
        await bot.send_message(
            chat_id=couple_user.user_id, text=f"Партнер сбросил дату начала отношений"
        )

    await callback.message.delete()
    await command_couple_info_handler(message=callback.message, state=state)


async def callback_couple_date_start_backward_handler(
    callback: types.CallbackQuery,
    state: FSMContext,
):
    """
    Возвращение в меню информации о паре
    """
    await callback.message.delete()
    await command_couple_info_handler(message=callback.message, state=state)


async def register_couple_date_start_handlers(dp: Dispatcher):
    dp.callback_query.register(
        callback_couple_date_start_handler,
        F.data == "couple_date_start",
    )
    dp.callback_query.register(
        callback_couple_date_start_set_handler,
        F.data == "couple_date_start_set",
    )
    dp.callback_query.register(
        process_dialog_calendar,
        DialogCalendarCallback.filter(),
        SetDateStart.set_date_start,
    )
    dp.callback_query.register(
        callback_couple_date_start_reset_handler,
        F.data == "couple_date_start_reset",
    )
    dp.callback_query.register(
        callback_couple_date_start_backward_handler,
        F.data == "couple_date_start_backward",
    )
