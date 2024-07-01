from aiogram import Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.bot.commands import CoupleCommands, GeneralCommands
from bot.bot.database.couple import get_user_couple
from bot.bot.database.users import get_user_by_user_id
from bot.bot.utils import get_couple_info_message

from couple.models import Couple
from bot.bot.utils import get_couple_info_message


async def command_couple_info_handler(message: types.Message, state: FSMContext):
    """
    Меню информации об отношениях
    """
    user = await get_user_by_user_id(message.chat.id)
    if not user:
        await message.answer(
            f"Сначала зарегистрируйтесь - {GeneralCommands.register.value}",
        )
        return

    couple: Couple = await get_user_couple(user)
    if not couple:
        await message.answer(
            "У вас нет пары :(",
        )
        return

    couple_info_message = await get_couple_info_message(couple=couple)

    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="Дата начала отношений ❤️", callback_data="couple_date_start"
        )
    )
    builder.row(
        types.InlineKeyboardButton(text="Желания 🔮", callback_data="couple_wish_menu")
    )
    builder.row(
        types.InlineKeyboardButton(
            text="Покинуть пару ❌", callback_data="couple_leave"
        )
    )

    await state.set_data({"user": user, "couple": couple})
    await message.answer(
        couple_info_message,
        parse_mode="HTML",
        reply_markup=builder.as_markup(),
    )


async def register_couple_info_handlers_(dp: Dispatcher):
    dp.message.register(
        command_couple_info_handler,
        Command(CoupleCommands.couple_info.command),
    )
