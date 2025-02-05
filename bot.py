import asyncio
import logging
import random

import discord
from discord import Intents, Client
from core.config import instance as config
from core.messages import messages
from interfaces.main.log_handler import log_handler
from interpreter.conditions import MessageConditions
from interpreter.variable import Variable
from PySide6.QtCore import QCoreApplication

translate = QCoreApplication.translate
logger = logging.getLogger(__name__)
logger.addHandler(log_handler)


class Bot(Client):
    def __init__(self):
        super().__init__(intents=Intents.all())

    @staticmethod
    async def on_ready():
        logger.info(translate("Bot", "Bot start"))

    async def on_message(self, message: discord.Message):
        if message.author != self.user:
            logger.info(translate("Bot", "New message") % message.clean_content)

            for message_name, message_data in messages.content().items():
                message_condition = MessageConditions(
                    message, expected_message=message_data["expected message"]
                )
                conditions_to_confirm = message_condition.filter(
                    message_data["conditions"]
                )
                logger.info(
                    translate("Bot", "Validating conditions")
                    % (message_name, conditions_to_confirm)
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
        logger.info(translate("Bot", "Delay") % delay)
        await asyncio.sleep(delay)

    @staticmethod
    async def send_reaction(reactions: list[list[str]], message: discord.Message):
        for reaction in reactions:
            code_reaction = reaction
            reaction = random.choice(reaction)
            try:
                await message.add_reaction(reaction)
                logger.info(
                    translate("Bot", "New reaction")
                    % (code_reaction, message.clean_content, message.author)
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
                    translate("Bot", "Group reply")
                    % (reply, message.clean_content, message.author)
                )
                reply_message = await message.channel.send(reply)
                if where_reaction == "bot":
                    await self.send_reaction(reactions, reply_message)
            elif where == "private":
                logger.info(
                    translate("Bot", "Private reply")
                    % (reply, message.clean_content, message.author)
                )
                dm_channel = await message.author.create_dm()
                reply_message = await dm_channel.send(reply)
                if where_reaction == "bot":
                    await self.send_reaction(reactions, reply_message)

    @staticmethod
    async def remove_message(message: discord.Message):
        await message.delete()
        logger.info(
            translate("Bot", "Remove message") % (message.clean_content, message.author)
        )

    @staticmethod
    async def pin_message(message: discord.Message):
        await message.pin()
        logger.info(
            translate("Bot", "Pin message") % (message.clean_content, message.author)
        )

    @staticmethod
    async def kick_member(member: discord.Member):
        await member.kick()
        logger.info(translate("Bot", "Kick member") % member.name)

    @staticmethod
    async def ban_member(member: discord.Member):
        await member.ban()
        logger.info(translate("Bot", "Ban member") % member.name)

    async def close(self):
        await super().close()
        logger.info(translate("Bot", "Bot close"))


class IntegratedBot(Bot):
    def __init__(self, thread_executor):
        self.thread_executor = thread_executor
        super().__init__()

    async def on_ready(self):
        await super().on_ready()
        self.thread_executor.bot_ready.emit()


if __name__ == "__main__":
    messages.load(config.get("file"))
    bot = Bot()
    bot.run(config.get("token"))
