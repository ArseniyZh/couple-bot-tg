from .couple_create import *
from .couple_join import *
from .couple_info import *
from .couple_wish import *


async def register_couple_handlers(dp: Dispatcher):
    """
    Регистрация хендлеров для пары
    """
    await register_couple_create_handler(dp)
    await register_couple_join_handlers(dp)
    await register_couple_info_handlers(dp)
    await register_couple_wish_handlers(dp)
