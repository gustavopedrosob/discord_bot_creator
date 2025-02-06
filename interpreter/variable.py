import discord

from core.functions import get_time


class Variable:
    def __init__(self, message: discord.Message):
        self.keys = {
            "author name": message.author.name,
            "guild name": (
                message.guild.name
                if isinstance(message.channel, discord.GroupChannel)
                else "N/A"
            ),
            "day": get_time("%d"),
            "month": get_time("%m"),
            "year": get_time("%Y"),
            "d-m-y": get_time("%d/%m/%Y"),
        }

    def apply_variable(self, string: str):
        return string.format(**self.keys)
