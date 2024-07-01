from .get_wish import *
from .menu import *


async def register_wish_change_handlers(dp: Dispatcher):
    await register_wish_change_get_wish_handlers(dp)
    await register_wish_change_menu_handlers(dp)
