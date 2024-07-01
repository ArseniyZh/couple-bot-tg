from aiogram.fsm.state import State, StatesGroup

class ChangeWishState(StatesGroup):
    get_wish = State(state="get_wish")
    wish_change_menu = State(state="wish_change_menu")
    change_wish_description_get_message = State("change_wish_description_get_message")
    set_date_to_change = State("set_date_to_change")