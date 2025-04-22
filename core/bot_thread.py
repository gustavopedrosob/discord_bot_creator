import discord
from PySide6.QtCore import Signal, QThread
from discord import (
    LoginFailure,
)

from core.config import instance as config
from core.integrated_bot import IntegratedBot


class QBotThread(QThread):
    bot_ready = Signal()
    log = Signal(str, int)
    login_failure = Signal()
    guild_join = Signal(str)
    guild_remove = Signal(str)
    guild_update = Signal(str)

    def __init__(self):
        super().__init__()
        self.__bot = IntegratedBot(self)

    def run(self):
        if self.__bot.is_closed():
            self.__bot = IntegratedBot(self)
        try:
            self.__bot.run(config.get("token"))
        except LoginFailure:
            self.login_failure.emit()

    def groups(self) -> dict[int, discord.Guild]:
        return {guild.id: guild for guild in self.__bot.guilds}

    def leave_group(self, group_id: int):
        group = self.__bot.get_guild(group_id)
        self.__bot.loop.create_task(self.__bot.leave_guild(group))

    def close(self):
        self.__bot.loop.create_task(self.__bot.close())
