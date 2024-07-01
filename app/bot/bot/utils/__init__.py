from aiogram import Bot, types
from bot.bot.commands.base import commands_classes_dict

import asyncio


from .couple import *


def run_async_in_thread(loop, coro):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)


async def _update_user_commands(bot: Bot, user_id: int):
    commands_classes = await commands_classes_dict(check_perm=True, user_id=user_id)
    commands = [
        types.BotCommand(command=_command.command, description=_command.description)
        for _command in commands_classes
    ]
    scope = types.BotCommandScopeChat(chat_id=user_id)
    await bot.set_my_commands(commands, scope=scope)


async def update_user_commands(bot: Bot, user_id: int):
    loop = asyncio.get_event_loop()
    loop.create_task(_update_user_commands(bot, user_id))


# async def send_message_to_couple_user(bot: Bot, couple: Couple, user: User, message: str) -> bool:
#     if couple_user := await get_couple_user(couple, user):
#         await bot.send_message(
#             chat_id=couple_user.user_id, text=message
#         )
