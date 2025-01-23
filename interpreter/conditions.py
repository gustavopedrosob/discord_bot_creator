import discord
import emojis

from core.functions import has_number, has_symbols


class MessageConditions:
    def __init__(
        self,
        message: discord.Message,
        expected_message: list[str],
    ):

        expected_message = message.clean_content in expected_message
        not_expected_message = not expected_message
        mention_someone = len(message.mentions) >= 1
        not_mention_someone = not mention_someone
        mention_everyone = message.mention_everyone
        not_mention_everyone = not mention_everyone
        author_is_bot = message.author.bot
        not_author_is_bot = not author_is_bot
        number_in_message = has_number(message.clean_content)
        not_number_in_message = not number_in_message
        symbols_in_message = has_symbols(message.clean_content)
        not_symbols_in_message = not symbols_in_message
        emojis_in_message = emojis.count(message.clean_content)
        not_emojis_in_message = not emojis_in_message

        self.string_conditions = {
            "expected message": expected_message,
            "not expected message": not_expected_message,
            "mention someone": mention_someone,
            "not mention someone": not_mention_someone,
            "mention everyone": mention_everyone,
            "not mention everyone": not_mention_everyone,
            "author is bot": author_is_bot,
            "not author is bot": not_author_is_bot,
            "number in message": number_in_message,
            "not number in message": not_number_in_message,
            "symbols in message": symbols_in_message,
            "not symbols in message": not_symbols_in_message,
            "emojis in message": emojis_in_message,
            "not emojis in message": not_emojis_in_message,
        }

    def filter(self, conditions: list[str]) -> dict[str, bool]:
        return {
            key: value
            for key, value in self.string_conditions.items()
            if key in conditions
        }
