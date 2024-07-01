from .info import *
from .date_start import *
from .leave import *


async def register_couple_info_handlers(dp: Dispatcher):
    """
    Регистрация хендлеров couple_info
    """
    await register_couple_info_handlers_(dp)
    await register_couple_date_start_handlers(dp)
    await register_couple_leave_handlers(dp)
