from aiogram import Dispatcher, Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from couple.models import Couple
from users.models import User

from bot.bot.database.couple import (
    get_user_couple,
    leave_from_couple,
    get_couple_user,
)
from bot.bot.database.users import get_user_by_user_id
from bot.bot.handlers.couple_handlers.couple_info import command_couple_info_handler
from bot.bot.handlers.menu_handlers.main_menu_handlers import command_main_menu_handler


async def callback_couple_leave_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Меню для подтверждения покидания пары
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Нет, остаться ✅", callback_data="couple_leave_confirm_no"
        ),
        types.InlineKeyboardButton(
            text="Да, покинуть ❌", callback_data="couple_leave_confirm_yes"
        ),
    )

    await callback.message.delete()
    await callback.message.answer(
        "Вы уверены, что хотите покинуть пару?",
        reply_markup=builder.as_markup(),
    )


async def callback_couple_leave_confirm_yes_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Хендлер для подтверждения покидания пары
    """
    state_data = await state.get_data()
    user: User = state_data.get(
        "user", await get_user_by_user_id(callback.from_user.id)
    )
    couple: Couple = state_data.get("couple", await get_user_couple(user))

    couple_user = await get_couple_user(couple, user)
    leaved = await leave_from_couple(couple, user)
    await callback.message.delete()
    if leaved:
        await callback.message.answer("Вы покинули пару.")
        await state.set_data({"user": user})

        if couple_user:
            await bot.send_message(
                chat_id=couple_user.user_id, text="Партнер покинул пару :("
            )

        await command_main_menu_handler(callback.message, state)
    else:
        await callback.message.answer("Не удалось покинуть пару.")


async def callback_couple_leave_confirm_no_handler(
    callback: types.CallbackQuery, state: FSMContext, bot: Bot
):
    """
    Хендлер для возврата в меню информации о паре
    """
    await callback.message.delete()
    await command_couple_info_handler(message=callback.message, state=state)


async def register_couple_leave_handlers(dp: Dispatcher):
    dp.callback_query.register(
        callback_couple_leave_handler,
        F.data == "couple_leave",
    )
    dp.callback_query.register(
        callback_couple_leave_confirm_yes_handler, F.data == "couple_leave_confirm_yes"
    )
    dp.callback_query.register(
        callback_couple_leave_confirm_no_handler, F.data == "couple_leave_confirm_no"
    )
