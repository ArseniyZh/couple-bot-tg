from .base import (
    ListPointer,
    CommandsGroup,
    Command,
    CheckPerm,
    commands_classes_dict,
    formatted_commands_message,
)

from bot.bot.database.users import get_user_by_user_id


class GeneralCommands(CommandsGroup):
    class Meta:
        commands_title = "Основные команды"
        group_sequence = 0

    main_menu = Command(
        command="main_menu",
        description="Главное меню",
        output_sequence=0,
    )
    start = Command(
        command="start",
        description="Начать взаимодействие с ботом",
        output_sequence=1,
    )
    register = Command(
        command="register",
        description="Зарегистрировать аккаунт",
        output_sequence=2,
    )
    commands_list = Command(
        command="commands_list",
        description="Просмотреть список команд",
    )


class CoupleCommands(CommandsGroup):
    class Meta:
        commands_title = "Команды для пар"
        group_sequence = 1
        list_pointer = ListPointer.heart

    couple_create = Command(
        command="couple_create",
        description="Создать пару",
        output_sequence=2,
    )
    couple_join = Command(
        command="couple_join",
        description="Присоединиться к паре",
        output_sequence=3,
    )
    couple_info = Command(
        command="couple_info",
        description="Меню пары",
        output_sequence=4,
    )

    # couple_wish_menu = Command(
    #     command="couple_wish_menu",
    #     description="Меню желаний пары",
    #     output_sequence=5,
    # )
