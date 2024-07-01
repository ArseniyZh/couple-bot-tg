from .main_menu_handlers import *
from .couple_menu import *


async def register_menu_handlers(dp: Dispatcher):
    await register_main_menu_handlers(dp)
    await register_couple_menu_handlers(dp)
