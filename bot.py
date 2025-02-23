import asyncio
import logging
import random
import typing

import discord
from PySide6.QtCore import QTranslator, QCoreApplication
from discord import Intents, Client

from core.config import instance as config
from core.messages import messages
from interfaces.main.log_handler import log_handler
from interpreter.conditions import MessageConditions
from interpreter.variable import Variable

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)

translate = QCoreApplication.translate


class Bot(Client):
    def __init__(self):
        super().__init__(intents=Intents.all())

    async def on_ready(self):
        logger.info(translate("Bot", "Bot started!"))

    async def on_message(self, message: discord.Message):
        if message.author != self.user:
            logger.info(
                translate("Bot", 'Identified message "{}".').format(
                    message.clean_content
                )
            )

            for message_name, message_data in messages.content().items():
                message_condition = MessageConditions(
                    message, message_data["expected message"], self.user
                )
                conditions_to_confirm = message_condition.filter(
                    message_data["conditions"]
                )
                logger.debug(
                    translate("Bot", "Validating message conditions {}: {}").format(
                        message_name, conditions_to_confirm
                    )
                )

                if all(conditions_to_confirm.values()):
                    if message_data["delay"]:
                        await self.apply_delay(message_data["delay"])
                    if message_data["reply"]:
                        await self.send_reply(
                            message_data["reply"],
                            message_data["reaction"],
                            message,
                            message_data["where reply"],
                            message_data["where reaction"],
                        )
                    if message_data["where reaction"] == "author":
                        await self.send_reaction(message_data["reaction"], message)
                    if message_data["pin or del"] == "delete":
                        await self.remove_message(message)
                    if message_data["pin or del"] == "pin":
                        await self.pin_message(message)
                    if message_data["kick or ban"] == "ban":
                        await self.ban_member(message.author)
                    if message_data["kick or ban"] == "kick":
                        await self.kick_member(message.author)

    @staticmethod
    async def apply_delay(delay: int):
        logger.info(
            translate("Bot", "Waiting {} seconds delay to next execution!").format(
                delay
            )
        )
        await asyncio.sleep(delay)

    @staticmethod
    async def send_reaction(reactions: list[list[str]], message: discord.Message):
        for reaction in reactions:
            code_reaction = reaction
            reaction = random.choice(reaction)
            try:
                await message.add_reaction(reaction)
                logger.info(
                    translate(
                        "Bot",
                        'Adding reaction "{}" to the message "{}" by the author {}.',
                    ).format(code_reaction, message.clean_content, message.author)
                )
            except discord.HTTPException:
                print(reaction)

    async def send_reply(
        self,
        replies: list[list[str]],
        reactions: list[list[str]],
        message: discord.Message,
        where: str,
        where_reaction: str,
    ):
        for reply in replies:
            reply = random.choice(reply)
            reply = Variable(message).apply_variable(reply)
            if where == "group" and message.channel.guild is not None:
                logger.info(
                    translate(
                        "Bot",
                        'Replying on group "{}" to the message "{}" by the author {}.',
                    ).format(reply, message.clean_content, message.author)
                )
                reply_message = await message.channel.send(reply)
                if where_reaction == "bot":
                    await self.send_reaction(reactions, reply_message)
            elif where == "private":
                logger.info(
                    translate(
                        "Bot",
                        'Replying on private "{}" to the message "{}" by the author {}.',
                    ).format(reply, message.clean_content, message.author)
                )
                dm_channel = await message.author.create_dm()
                reply_message = await dm_channel.send(reply)
                if where_reaction == "bot":
                    await self.send_reaction(reactions, reply_message)

    @staticmethod
    async def remove_message(message: discord.Message):
        await message.delete()
        logger.info(
            translate("Bot", 'Removing message "{}" by the author {}.').format(
                message.clean_content, message.author
            )
        )

    @staticmethod
    async def pin_message(message: discord.Message):
        await message.pin()
        logger.info(
            translate("Bot", 'Pinning message "{}" by the author {}.').format(
                message.clean_content, message.author
            )
        )

    @staticmethod
    async def kick_member(member: discord.Member):
        await member.kick()
        logger.info(translate("Bot", 'Kicking member "{}".').format(member.name))

    @staticmethod
    async def ban_member(member: discord.Member):
        await member.ban()
        logger.info(translate("Bot", 'Banning member "{}".').format(member.name))

    async def close(self):
        await super().close()
        logger.info(translate("Bot", "Bot finished!"))

    @staticmethod
    async def leave_guild(guild: discord.Guild):
        await guild.leave()
        logger.info(translate("Bot", 'Leaving guild "{}"').format(guild.name))

    def get_guild(self, guild_id: int) -> typing.Optional[discord.Guild]:
        return next(filter(lambda g: g.id == guild_id, self.guilds))


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


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%x %X",
    )
    translator = QTranslator()
    translator.load(f"translations/build/{config.get("language")}.qm")
    translate = translator.translate
    messages.load(config.get("file"))
    bot = Bot()
    bot.run(config.get("token"))
