# myapp/management/commands/mycommand.py
from django.core.management.base import BaseCommand

from bot.bot.main import main
import asyncio


class Command(BaseCommand):
    help = "Описание вашей команды"

    def handle(self, *args, **kwargs):
        # Здесь можно поместить код вашей команды
        asyncio.run(main())
