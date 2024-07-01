from users.models import User
from couple.models import Couple

import datetime


async def get_couple_info_message(couple: Couple, user: User = None) -> str:
    # Участники пары
    couple_info_message = "<b>Участники пары</b>\n"

    user_1: User
    user_2: User
    if user_1 := couple.user_1:
        couple_info_message += f"{user_1.get_tg_username}\n"
    if user_2 := couple.user_2:
        couple_info_message += f"{user_2.get_tg_username}\n"

    # Дата начала отношений
    couple_info_message += "\n<b>Дата начала отношений</b>\n"
    if date_start := couple.date_start:
        couple_info_message += (
            f"Вы начали встречаться <b>{couple.formatted_date_start}</b>. "
            f"Прошло {(datetime.datetime.now().date() - date_start).days} д."
        )
    else:
        couple_info_message += "<i>Вы можете назначить эту дату</i>"
    couple_info_message += "\n"

    couple_info_message += f'\n\n <span class="tg-spoiler">Код пары: <i><b>{couple.unique_id}</b></i></span> \n'

    return couple_info_message
