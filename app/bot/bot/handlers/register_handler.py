from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.bot.commands import GeneralCommands
from bot.bot.database.users import create_user, get_user_by_user_id


class RegistrationForm(StatesGroup):
    """
    Состояние регистрации
    """

    start = State(state="start")
    contact = State(state="contact")


async def command_register_handler(message: Message, state: FSMContext):
    """
    Начало регистрации
    """
    if await get_user_by_user_id(message.chat.id):
        await message.answer("Вы уже зарегистрированы")
        return

    await state.set_state(RegistrationForm.start)
    kb = [
        [types.KeyboardButton(text="Отправить контакт", request_contact=True)],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await message.answer(
        "Пожалуйста, отправьте ваш контактный номер телефона.", reply_markup=keyboard
    )
    await state.set_state(RegistrationForm.contact)


async def contact_handler(message: Message, state: FSMContext):
    """
    Процесс регистрации
    """
    contact = message.contact
    await create_user(
        first_name=contact.first_name,
        last_name=contact.last_name,
        phone_number=contact.phone_number,
        tg_username=message.from_user.username,
        user_id=contact.user_id,
    )
    await message.answer(
        "Спасибо, вы зарегистрировались.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.clear()


async def register_handlers_registration(dp: Dispatcher):
    dp.message.register(
        command_register_handler,
        Command(GeneralCommands.register.command),
    )
    dp.message.register(
        contact_handler,
        RegistrationForm.contact,
        lambda message: message.contact,
    )
