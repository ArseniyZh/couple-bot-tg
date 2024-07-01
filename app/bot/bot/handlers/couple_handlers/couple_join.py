from aiogram.types import Message

from aiogram import Dispatcher, Bot
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from couple.models import Couple
from users.models import User

from bot.bot.commands import CoupleCommands, GeneralCommands
from bot.bot.database.users import get_user_by_user_id
from bot.bot.database.couple import (
    get_user_couple,
    join_to_couple,
    get_couple_by_unique_id,
    get_couple_user,
)

from bot.bot.handlers.couple_handlers.couple_info import command_couple_info_handler


class CoupleJoinState(StatesGroup):
    get_unique_id = State(state="get_unique_id")


async def command_couple_join_handler(message: Message, state: FSMContext):
    """
    Входная точка для присоединения к паре
    """
    user = await get_user_by_user_id(message.chat.id)
    if not user:
        await message.answer(
            f"Сначала зарегистрируйтесь - {GeneralCommands.register.value}",
        )
        return

    if await get_user_couple(user):
        await message.answer(
            f"У вас уже есть пара",
        )
        return

    sent_code_message = await message.answer("Пришлите код пары, чтобы присоединиться")
    await state.update_data({"user": user, "sent_code_message": sent_code_message})
    await state.set_state(CoupleJoinState.get_unique_id)


async def command_couple_join_get_unique_id_handler(
    message: Message, state: FSMContext, bot: Bot
):
    """
    Процесс присоединения к паре
    """
    unique_id = message.text
    couple: Couple = await get_couple_by_unique_id(unique_id=unique_id)
    user: User = (await state.get_data()).get("user")

    if not user:
        await message.answer("Что-то пошло не так.")
        return

    if not couple:
        await message.answer("Неверный код.")
        return

    joined: bool = await join_to_couple(couple, user)

    if joined:
        state_data = await state.get_data()

        sent_code_message = state_data.get("sent_code_message")
        await message.delete()
        await sent_code_message.delete()

        await message.answer("Вы успешно присоединились к паре!")
        if couple_user := await get_couple_user(couple, user):
            await bot.send_message(
                chat_id=couple_user.user_id, text="Партнер присоединился к вашей паре!"
            )

        await command_couple_info_handler(message, state)
    else:
        await message.answer("Не удалось присоединиться к паре :(")
        return

    await state.clear()


async def register_couple_join_handlers(dp: Dispatcher):
    dp.message.register(
        command_couple_join_handler, Command(CoupleCommands.couple_join.command)
    )
    dp.message.register(
        command_couple_join_get_unique_id_handler, CoupleJoinState.get_unique_id
    )
