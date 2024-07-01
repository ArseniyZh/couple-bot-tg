from typing import Any, Optional


class ListPointer:
    information = "ℹ️"
    heart = "❤️"


class CommandsGroup:
    """
    Базовый класс для групп команд.
    """

    _commands_classes = []

    class Meta:
        """
        Класс для хранения метаданных о группе команд.
        """

        commands_title = "Команды"
        """Заголовок группы команд."""

        list_pointer = "ℹ️"
        """Список указателей для группы команд."""

        group_sequence = 1000
        """Порядковый номер группы команд."""

    async def get_commands_classes(
        self,
        sort: Optional[bool] = True,
        check_perm: Optional[bool] = True,
        *args,
        **kwargs,
    ) -> list["Command"]:
        """
        Возвращает список классов команд для группы команд.

        Args:
            sort (bool): Булевое значение, указывающее, нужно ли сортировать список команд.
            check_perm (bool): Булевое значение, указывающее, нужно ли проверять права пользователя на выполнение команды.
            *args: Дополнительные позиционные аргументы.
            **kwargs: Дополнительные ключевые аргументы.

        Returns:
            list[Command]: Список классов команд.
        """
        commands: list[Command] = []

        if _commands := self._commands_classes:
            commands = _commands
        else:
            for _attr in dir(self):
                attr = getattr(self, _attr)
                if issubclass(type(attr), Command):
                    attr: Command

                    # Проверяем права пользователя
                    if check_perm and not await attr.check_perm(*args, **kwargs):
                        continue

                    # Установите указатель списка, если он не установлен
                    if attr.list_pointer is None:
                        self_meta = getattr(self, "Meta")
                        list_pointer = (
                            getattr(
                                self_meta,
                                "list_pointer",
                                CommandsGroup.Meta.list_pointer,
                            )
                            if self_meta
                            else CommandsGroup.Meta.list_pointer
                        )
                        attr.list_pointer = list_pointer

                    commands.append(attr)

        if sort:
            commands.sort(key=lambda command: command.output_sequence)
        self._commands_classes = commands
        return commands

    def __str__(self) -> str:
        """
        Returns строковое представление группы команд.

        Returns:
            str: Строковое представление группы команд.
        """
        meta = self.Meta
        return f"{meta.commands_title} ({meta.group_sequence})"

    def __repr__(self) -> str:
        """
        Returns строковое представление группы команд.

        Returns:
            str: Строковое представление группы команд.
        """
        return self.__str__()


class CheckPerm:
    """
    Класс для проверки разрешений пользователя на выполнение команды.
    """

    def __init__(
        self, func: callable, reverse_bool: Optional[bool] = False, *args, **kwargs
    ) -> None:
        """
        Инициализирует объект CheckPerm.

        Args:
            func: Функция для проверки разрешений.
            reverse_bool: Если True, результат проверки будет инвертирован.
        """
        self.func = func
        self.reverse_bool = reverse_bool

    async def __call__(self, *args: Any, **kwargs: Any) -> bool:
        """
        Проверяет разрешения пользователя на выполнение команды.

        Args:
            *args: Позиционные аргументы.
            **kwargs: Ключевые аргументы.

        Returns:
            bool: True, если пользователь имеет разрешение на выполнение команды, иначе False.
        """
        has_perm = bool(await self.func(*args, **kwargs))
        return not has_perm if self.reverse_bool else has_perm

    @staticmethod
    async def check_perm_false(*args, **kwargs):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение команды.

        Всегда возвращает False.

        Args:
            *args: Позиционные аргументы.
            **kwargs: Ключевые аргументы.

        Returns:
            bool: False.
        """
        return False

    @staticmethod
    async def check_perm_true(*args, **kwargs):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение команды.

        Всегда возвращает True.

        Args:
            *args: Позиционные аргументы.
            **kwargs: Ключевые аргументы.

        Returns:
            bool: True.
        """
        return True


class Command:
    """
    Класс, представляющий команду бота.
    """

    def __init__(
        self,
        command: str,
        prefix: Optional[str] = "/",
        description: Optional[str] = "",
        output_sequence: Optional[int] = 1000,
        check_perm: Optional[callable] = CheckPerm.check_perm_true,
        list_pointer: Optional[str] = None,
    ):
        """
        Инициализирует объект команды.

        Args:
            command (str): Команда бота.
            prefix (str, optional): Префикс команды. По умолчанию "/".
            description (str, optional): Описание команды. По умолчанию "".
            output_sequence (int, optional): Последовательность вывода команды.
                   По умолчанию 1000.
            check_perm (callable, optional): Функция для проверки разрешения пользователя на выполнение команды.
                   По умолчанию CheckPerm.check_perm_true.
            list_pointer (str, optional): Указатель на иконку команды в списке команд. По умолчанию None.
        """
        self.command = command
        self.prefix = prefix
        self.description = description
        self.output_sequence = output_sequence
        self.check_perm = check_perm
        self.list_pointer = list_pointer

    def __str__(self) -> str:
        """
        Возвращает значение команды в виде строки.

        Returns:
            str: Значение команды в виде строки.
        """
        return self.value

    @property
    def value(self):
        """
        Возвращает значение команды в виде строки.

        Returns:
            str: Значение команды в виде строки.
        """
        return f"{self.prefix}{self.command}"


async def commands_classes_dict(
    sort: Optional[bool] = True, check_perm: Optional[bool] = True, *args, **kwargs
) -> dict[CommandsGroup, list[Command]]:
    """
    Возвращает словарь, где ключами являются классы групп команд,
    а значениями - списки команд соответствующей группы.

    Args:
        sort (bool, optional): Сортировать ли список команд по последовательности вывода.
            По умолчанию True.
        check_perm (bool, optional): Проверять ли права пользователя на выполнение команды.
            По умолчанию True.
        *args: Дополнительные позиционные аргументы.
        **kwargs: Дополнительные ключевые аргументы.

    Returns:
        dict[CommandsGroup, list[Command]]: Словарь команд.
    """
    _commands: dict[CommandsGroup, list[Command]] = {}

    commands_groups = CommandsGroup.__subclasses__()
    if sort:
        commands_groups.sort(key=lambda x: x.Meta.group_sequence)

    commands_group: CommandsGroup
    for commands_group in commands_groups:
        commands: list[Command] = await commands_group().get_commands_classes(
            sort=sort, check_perm=check_perm, *args, **kwargs
        )
        _commands[commands_group] = commands

    return _commands


async def formatted_commands_message(
    sort: Optional[bool] = True, check_perm: Optional[bool] = True, *args, **kwargs
) -> str:
    """
    Возвращает строку с форматированным списком команд.
    Каждая команда отображается с указателем и описанием.

    Args:
        sort (bool, optional): Сортировать ли список команд по последовательности вывода.
            По умолчанию True.
        check_perm (bool, optional): Проверять ли права пользователя на выполнение команды.
            По умолчание True.
        *args: Дополнительные позиционные аргументы.
        **kwargs: Дополнительные ключевые аргументы.

    Returns:
        str: Строка с форматированным списком команд.
    """
    commands_dict: dict[CommandsGroup, list[Command]] = await commands_classes_dict(
        sort=sort, check_perm=check_perm, *args, **kwargs
    )
    formatted_commands: list[str] = []

    for command_group, commands_list in commands_dict.items():
        command_message = f"<b>{command_group.Meta.commands_title}</b>\n"

        for command in commands_list:
            command_message += (
                f"{command.list_pointer} {command.prefix}{command.command}"
            )
            if description := command.description:
                command_message += f" - {description}"
            command_message += "\n"

        formatted_commands.append(command_message)

    return "\n".join(formatted_commands)
