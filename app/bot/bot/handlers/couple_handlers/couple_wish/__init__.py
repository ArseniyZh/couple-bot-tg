from .menu import *
from .wish_create import *
from .own_wish import *
from .couple_user_wish import *
from .wish_change import *


async def register_couple_wish_handlers(dp: Dispatcher):
    """
    Регистрация хендлеров couple_wish
    """
    await register_couple_wish_menu_handlers(dp)
    await register_couple_wish_create_handlers(dp)
    await register_couple_wish_own_wish_handlers(dp)
    await register_couple_user_wish_own_wish_menu_handlers(dp)
    await register_wish_change_handlers(dp)
