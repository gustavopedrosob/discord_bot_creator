import asyncio
import logging
import typing

import discord
from discord import Intents, Client

from core.config import instance as config
from core.functions import random_choose
from core.messages import messages
from interfaces.main.log_handler import LogHandler
from interpreter.conditions import MessageConditions
from interpreter.variable import Variable

logger = logging.getLogger(__name__)


class Bot(Client):
    def __init__(self):
        super().__init__(intents=Intents.all())

    @staticmethod
    async def on_ready():
        logger.info("Bot iniciado!")

    async def on_message(self, message: discord.Message):
        logger.info(f'Identificada mensagem "{message.content}".')

        for message_data in messages.content().values():
            await self.message_and_reply(
                message=message,
                conditions=message_data["conditions"],
                expected_message=message_data["expected message"],
                reply=message_data["reply"],
                reaction=message_data["reaction"],
                delay=message_data["delay"],
                pin_or_del=message_data["pin or del"],
                kick_or_ban=message_data["kick or ban"],
                where_reply=message_data["where reply"],
                where_reaction=message_data["where reaction"],
            )

    @staticmethod
    async def apply_delay(delay: int):
        logger.info(f"Aguardando delay de {delay} segundos para a proxima execução!")
        await asyncio.sleep(delay)

    @staticmethod
    async def send_reaction(reactions: list[list[str]], message: discord.Message):
        for reaction in reactions:
            code_reaction = reaction
            reaction = random_choose(reaction)
            try:
                await message.add_reaction(reaction)
                logger.info(
                    f'Adicionando a reação "{code_reaction}" a mensagem "{message.content}" do autor {message.author}.'
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
            reply = random_choose(reply)
            reply = Variable(message).apply_variable(reply)
            if where == "group":
                message = await message.channel.send(reply)
                if where_reaction == "bot":
                    await self.send_reaction(reactions, message)
            elif where == "private":
                dm_channel = await message.author.create_dm()
                message = await dm_channel.send(reply)
                if where_reaction == "bot":
                    await self.send_reaction(reactions, message)
            logger.info(
                f'Enviando a resposta "{reply}" à mensagem "{message.content}" do autor {message.author}.'
            )

    @staticmethod
    async def remove_message(message: discord.Message):
        await message.delete()
        logger.info(
            f'Removendo mensagem "{message.content}" do autor {message.author}.'
        )

    @staticmethod
    async def pin_message(message: discord.Message):
        await message.pin()
        logger.info(f'Fixando mensagem "{message.content}" do autor {message.author}.')

    @staticmethod
    async def kick_member(member: discord.Member):
        await member.kick()
        logger.info(f'Expulsando jogador "{member.name}".')

    @staticmethod
    async def ban_member(member: discord.Member):
        await member.ban()
        logger.info(f'Banindo jogador "{member.name}".')

    async def message_and_reply(
        self,
        message: discord.Message,
        conditions: list[str],
        expected_message: list[str],
        reply: list[list[str]],
        reaction: list[list[str]],
        delay: int,
        pin_or_del: typing.Optional[str],
        kick_or_ban: typing.Optional[str],
        where_reply: typing.Optional[str],
        where_reaction: typing.Optional[str],
    ):

        message_condition = MessageConditions(
            message, expected_message=expected_message
        )

        conditions_to_confirm = list(
            map(lambda x: message_condition.string_conditions[x], conditions)
        )

        # é importante adicionar a condição expected message se tiver alguma mensagem esperada porque, senão podem ocorrer erros inesperados.
        if expected_message:
            conditions_to_confirm.append(message.content in expected_message)

        logger.info(f"Verificando condições {conditions_to_confirm}")

        if all(conditions_to_confirm):
            if delay:
                await self.apply_delay(delay)
            if reply:
                await self.send_reply(
                    reply, reaction, message, where_reply, where_reaction
                )
            if where_reaction == "author":
                await self.send_reaction(reaction, message)
            if pin_or_del == "delete":
                await self.remove_message(message)
            if pin_or_del == "pin":
                await self.pin_message(message)
            if kick_or_ban == "ban":
                await self.ban_member(message.author)
            if kick_or_ban == "kick":
                await self.kick_member(message.author)


class IntegratedBot(Bot):
    def __init__(self, app):
        self.app = app
        super().__init__()

        log_handler = LogHandler(self.app)
        log_handler.setLevel(logging.INFO)
        logger.addHandler(log_handler)

    async def on_ready(self):
        logger.info("Bot iniciado!")
        self.app.change_init_bot_button()


if __name__ == "__main__":
    messages.load()
    bot = Bot()
    bot.run(config.get("token"))
