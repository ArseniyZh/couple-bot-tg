from .menu_handlers import *
from .common_handlers import *
from .register_handler import *
from .couple_handlers import *


async def register_all_handlers(dp: Dispatcher):
    """
    Входная точка регистрации всех хендлеров
    """
    await menu_handlers.register_menu_handlers(dp)
    await common_handlers.register_common_handlers(dp)
    await register_handler.register_handlers_registration(dp)
    await couple_handlers.register_couple_handlers(dp)
