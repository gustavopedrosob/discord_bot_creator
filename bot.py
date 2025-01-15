import asyncio
import logging
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
        if message.author != self.user:
            logger.info(f'Identificada mensagem "{message.content}".')

            for message_data in messages.content().values():
                message_condition = MessageConditions(
                    message, expected_message=message_data["expected message"]
                )

                conditions_to_confirm = list(
                    map(
                        lambda x: message_condition.string_conditions[x],
                        message_data["conditions"],
                    )
                )

                # é importante adicionar a condição expected message se tiver alguma mensagem esperada porque, senão podem ocorrer erros inesperados.
                if message_data["expected message"]:
                    conditions_to_confirm.append(
                        message.content in message_data["expected message"]
                    )

                logger.info(f"Verificando condições {conditions_to_confirm}")

                if all(conditions_to_confirm):
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
