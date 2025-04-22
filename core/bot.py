import asyncio
import logging
import random
import typing

import discord
from charset_normalizer.utils import is_arabic_isolated_form
from discord import MessageType

from core.config import instance as config
from core.database import Database
from core.translator import Translator
from interpreter.conditions import MessageConditions
from interpreter.variable import Variable
from models.message import Message
from models.reaction import MessageReaction
from widgets.log_handler import log_handler

logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
translate = Translator.translate


class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.database = Database(config.get("database"))

    async def on_ready(self):
        logger.info(translate("Bot", "Bot started!"))

    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        group = self.database.get_group(guild.id)
        if group and group.welcome_message and group.welcome_message_channel:
            channel = guild.get_channel(group.welcome_message_channel)
            welcome_message = group.welcome_message.format(member=member.name)
            await channel.send(welcome_message)
            logger.info(
                translate(
                    "Bot", 'Sending welcome message "{}" on channel "{}" at "{}" group.'
                ).format(welcome_message, channel.name, guild.name)
            )

    async def on_member_remove(self, member: discord.Member):
        guild = member.guild
        group = self.database.get_group(guild.id)
        if group and group.goodbye_message and group.goodbye_message_channel:
            channel = guild.get_channel(group.goodbye_message_channel)
            goodbye_message = group.goodbye_message.format(member=member.name)
            await channel.send(goodbye_message)
            logger.info(
                translate(
                    "Bot", 'Sending goodbye message "{}" on channel "{}" at "{}" group.'
                ).format(goodbye_message, channel.name, guild.name)
            )

    async def on_message(self, discord_message: discord.Message):
        if discord_message.author != self.user and discord_message.type == MessageType.default:
            logger.info(
                translate("Bot", 'Identified message "{}".').format(
                    discord_message.clean_content
                )
            )

            for message in self.database.get_messages():
                message_condition = MessageConditions(
                    discord_message, message.expected_messages, self.user
                )
                conditions_to_confirm = message_condition.filter(message.conditions)
                logger.debug(
                    translate("Bot", "Validating message conditions {}: {}").format(
                        message.name, conditions_to_confirm
                    )
                )

                if all(conditions_to_confirm.values()):
                    if message.delay:
                        await self.apply_delay(message.delay)
                    if message.replies:
                        await self.send_replies(
                            message,
                            discord_message,
                        )
                    if message.where_reaction == "author":
                        await self.send_reactions(message.reactions, discord_message)
                    if message.pin_or_del == "delete":
                        await self.remove_message(discord_message)
                    if message.pin_or_del == "pin":
                        await self.pin_message(discord_message)
                    if message.kick_or_ban == "ban":
                        await self.ban_member(discord_message.author)
                    if message.kick_or_ban == "kick":
                        await self.kick_member(discord_message.author)

    @staticmethod
    async def apply_delay(delay: int):
        logger.info(
            translate("Bot", "Waiting {} seconds delay to next execution!").format(
                delay
            )
        )
        await asyncio.sleep(delay)

    @staticmethod
    async def send_reactions(
        reactions: list[MessageReaction], discord_message: discord.Message
    ):
        for reaction in reactions:
            reaction_text = random.choice(list(reaction.reaction))
            try:
                await discord_message.add_reaction(reaction_text)
                logger.info(
                    translate(
                        "Bot",
                        'Adding reaction "{}" to the message "{}" by the author {}.',
                    ).format(
                        reaction_text,
                        discord_message.clean_content,
                        discord_message.author,
                    )
                )
            except discord.HTTPException:
                print(reaction_text)

    async def send_replies(
        self,
        message: Message,
        discord_message: discord.Message,
    ):
        for reply in message.replies:
            reply_text = random.choice(reply.text.split("|"))
            reply_text = Variable(discord_message).apply_variable(reply_text)
            if (
                message.where_reply == "group"
                and discord_message.channel.guild is not None
            ):
                await self.send_reply(
                    reply_text, discord_message, discord_message.channel, message
                )
            elif message.where_reply == "private":
                dm_channel = await discord_message.author.create_dm()
                await self.send_reply(reply_text, discord_message, dm_channel, message)

    async def send_reply(
        self,
        reply: str,
        discord_message: discord.Message,
        channel: discord.abc.Messageable,
        message: Message,
    ):
        if message.where_reply == "group":
            log = translate(
                "Bot",
                'Replying on group "{}" to the message "{}" by the author {}.',
            ).format(reply, discord_message.clean_content, discord_message.author)
        else:
            log = translate(
                "Bot",
                'Replying on private "{}" to the message "{}" by the author {}.',
            ).format(reply, discord_message.clean_content, discord_message.author)
        logger.info(log)
        reply_message = await self.send_message(channel, reply)
        if message.where_reaction == "bot" and reply_message:
            await self.send_reactions(message.reactions, reply_message)

    @staticmethod
    async def send_message(
        channel: discord.abc.Messageable, message: str
    ) -> Message | None:
        try:
            reply = await channel.send(message)
        except discord.errors.HTTPException as exception:
            if exception.code == 50035 and exception.status == 400:
                logger.error(
                    translate(
                        "Bot",
                        "Content must be 2000 or fewer in length.",
                    ).format(message, channel)
                )
                return None
            return None
        else:
            return reply

    @staticmethod
    async def remove_message(message: discord.Message):
        try:
            await message.delete()
        except discord.Forbidden:
            logger.error(
                translate(
                    "Bot",
                    'Don\'t have permission to remove message "{}" by the author {}.',
                ).format(message.clean_content, message.author)
            )
        else:
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
        try:
            await member.kick()
        except discord.Forbidden:
            logger.error(
                translate("Bot", 'Don\'t have permission to kick "{}".').format(
                    member.name
                )
            )
        else:
            logger.info(translate("Bot", 'Kicking member "{}".').format(member.name))

    @staticmethod
    async def ban_member(member: discord.Member):
        try:
            await member.ban()
        except discord.Forbidden:
            logger.error(
                translate("Bot", 'Don\'t have permission to ban "{}".').format(
                    member.name
                )
            )
        else:
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
