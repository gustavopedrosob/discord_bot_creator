import discord
import emojis

from core.functions import have_in

symbols = [
    "'",
    '"',
    "!",
    "@",
    "#",
    "$",
    "%",
    "¨",
    "&",
    "*",
    "(",
    ")",
    "-",
    "_",
    "+",
    "=",
    "§",
    "`",
    "´",
    "[",
    "{",
    "ª",
    "~",
    "^",
    "]",
    "}",
    "º",
    ",",
    ".",
    "<",
    ">",
    ":",
    ";",
    "?",
    "/",
    "°",
    "|",
]
numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]


class MessageConditions:
    def __init__(
        self,
        message: discord.Message,
        expected_author: discord.Member = None,
        expected_message=None,
    ):

        expected_message = (
            False
            if expected_message is None
            else (
                message.clean_content == expected_message
                if type(expected_message) == str
                else message.clean_content in expected_message
            )
        )
        not_expected_message = not expected_message
        mention_someone = True if len(message.mentions) >= 1 else False
        not_mention_someone = not mention_someone
        mention_everyone = message.mention_everyone
        not_mention_everyone = not mention_everyone
        author_is_expected = (
            False if expected_author == None else message.author == expected_author
        )
        not_author_is_expected = not author_is_expected
        author_is_bot = message.author.bot
        not_author_is_bot = not author_is_bot
        number_in_message = have_in(numbers, message.clean_content)
        not_number_in_message = not number_in_message
        symbols_in_message = have_in(symbols, message.clean_content)
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
            "author is expected": author_is_expected,
            "not author is expected": not_author_is_expected,
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
