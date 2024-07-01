from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.bot.handlers.couple_handlers.couple_info import command_couple_info_handler


async def callback_couple_wish_menu_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Меню желаний
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Мои желания 💅", callback_data="couple_wish_menu_own_wish"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Желания партнера 💋",
            callback_data="couple_wish_menu_couple_user_wish",
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Назад ◀️", callback_data="couple_wish_menu_backward"
        )
    )
    await callback.message.answer("Меню желаний", reply_markup=builder.as_markup())
    if callback.message:
        await callback.message.delete()


async def callback_couple_wish_menu_backward_handler(
    callback: types.CallbackQuery, state: FSMContext
):
    """
    Возвращение в меню информации о пары
    """
    if message_wish_success_created := (await state.get_data()).get(
        "message_wish_success_created"
    ):
        await callback.message.bot.delete_message(message_wish_success_created)
    await callback.message.delete()
    await command_couple_info_handler(callback.message, state)


async def register_couple_wish_menu_handlers(dp: Dispatcher):
    dp.callback_query.register(
        callback_couple_wish_menu_handler,
        F.data == "couple_wish_menu",
    )
    dp.callback_query.register(
        callback_couple_wish_menu_backward_handler,
        F.data == "couple_wish_menu_backward",
    )
