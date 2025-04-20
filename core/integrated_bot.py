import discord
from core.bot import Bot


class IntegratedBot(Bot):
    def __init__(self, thread_executor):
        self.thread_executor = thread_executor
        super().__init__()

    async def on_ready(self):
        await super().on_ready()
        self.thread_executor.bot_ready.emit()

    async def on_guild_join(self, guild: discord.Guild):
        self.thread_executor.guild_join.emit(str(guild.id))

    async def on_guild_remove(self, guild: discord.Guild):
        self.thread_executor.guild_remove.emit(str(guild.id))

    async def on_guild_update(self, _: discord.Guild, after: discord.Guild):
        self.thread_executor.guild_update.emit(str(after.id))
