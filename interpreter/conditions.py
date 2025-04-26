import logging
import re
import typing

import discord
import emojis

from core.translator import (
    Translator,
    FIELDS_TRANSLATIONS,
    OPERATORS_TRANSLATIONS,
    BOOL_TRANSLATIONS,
)
from models.condition import MessageCondition
from core.log_handler import LogHandler


logger = logging.getLogger(__name__)
logger.addHandler(LogHandler())
translate = Translator.translate


class MessageConditionValidator:
    STR_FIELDS = (
        "message",
        "author name",
        "channel name",
        "guild name",
    )
    INT_FIELDS = (
        "mentions to bot",
        "mentions",
        "bot author",
        "emojis",
    )
    STR_OPERATORS = (
        "equal to",
        "not equal to",
        "contains",
        "not contains",
        "starts with",
        "ends with",
        "regex",
    )
    INT_OPERATORS = (
        "equal to",
        "not equal to",
        "is greater than",
        "is less than",
        "is greater or equal to",
        "is less or equal to",
    )

    def __init__(
        self,
        conditions: list[MessageCondition],
        message: discord.Message,
    ):
        self.conditions = conditions
        self.message = message
        self.conditions_count = len(conditions)
        self.conditions_validated = 0

    def is_valid(self, condition: MessageCondition) -> bool:
        if condition.field == "message":
            return self._validate_str_condition(
                condition, str(self.message.clean_content)
            )
        elif condition.field == "author name":
            return self._validate_str_condition(condition, self.message.author.name)
        elif condition.field == "channel name":
            return self._validate_str_condition(condition, self.message.channel.name)
        elif condition.field == "guild name":
            return self._validate_str_condition(condition, self.message.guild.name)
        elif condition.field == "mentions to bot":
            return self._validate_int_condition(
                condition, len(list(user.bot for user in self.message.mentions))
            )
        elif condition.field == "mentions":
            return self._validate_int_condition(condition, len(self.message.mentions))
        elif condition.field == "bot author":
            return self._validate_int_condition(condition, int(self.message.author.bot))
        elif condition.field == "emojis":
            return self._validate_int_condition(
                condition, emojis.count(self.message.clean_content)
            )
        else:
            raise ValueError(f"Invalid field: {condition.field}")

    def is_valid_all(self) -> bool:
        return all(self.is_valid(condition) for condition in self.conditions)

    def _validate_str_condition(self, condition: MessageCondition, value: str) -> bool:
        new_value = value
        condition_value = condition.value
        if condition.case_insensitive:
            new_value = value.lower()
            condition_value = condition_value.lower()
        if condition.operator == "equal to":
            result = new_value == condition_value
        elif condition.operator == "not equal to":
            result = new_value != condition_value
        elif condition.operator == "contains":
            result = condition_value in new_value
        elif condition.operator == "not contains":
            result = condition_value not in new_value
        elif condition.operator == "starts with":
            result = new_value.startswith(condition_value)
        elif condition.operator == "ends with":
            result = new_value.endswith(condition_value)
        elif condition.operator == "regex":
            flag = re.IGNORECASE if condition.case_insensitive else 0
            result = re.match(condition.value, value, flag) is not None
        else:
            raise ValueError(f"Invalid operator: {condition.operator}")
        self.conditions_validated += 1
        self._validate_condition_log(
            condition, condition.value, value, result, condition.case_insensitive
        )
        return result

    def _validate_condition_log(
        self,
        condition: MessageCondition,
        condition_value: typing.Union[str, int],
        value: typing.Union[str, int],
        result: bool,
        case_insensitive: typing.Optional[bool] = None,
    ) -> None:
        format_kwargs = dict(
            conditions_validated=self.conditions_validated,
            conditions_count=self.conditions_count,
            field=FIELDS_TRANSLATIONS[condition.field],
            value=repr(value),
            operator=OPERATORS_TRANSLATIONS[condition.operator].lower(),
            condition_value=repr(condition_value),
            result=BOOL_TRANSLATIONS[result],
        )
        if case_insensitive:
            format_kwargs["case_insensitive"] = Translator.translate(
                "ConditionValidator", "Case insensitive"
            ).lower()
            log = Translator.translate(
                "ConditionValidator",
                "Validating condition ({conditions_validated}/{conditions_count}): field {field} {value} {case_insensitive} {operator} {condition_value} ({result})",
            ).format(**format_kwargs)
        else:
            log = Translator.translate(
                "ConditionValidator",
                "Validating condition ({conditions_validated}/{conditions_count}): field {field} {value} {operator} {condition_value} ({result})",
            ).format(**format_kwargs)
        logger.debug(log)

    def _validate_int_condition(self, condition: MessageCondition, value: int) -> bool:
        condition_value = int(condition.value)
        if condition.operator == "equal to":
            result = condition_value == value
        elif condition.operator == "not equal to":
            result = condition_value != value
        elif condition.operator == "is greater than":
            result = condition_value > value
        elif condition.operator == "is less than":
            result = condition_value < value
        elif condition.operator == "is greater or equal to":
            result = condition_value >= value
        elif condition.operator == "is less or equal to":
            result = condition_value <= value
        else:
            raise ValueError(f"Invalid operator: {condition.operator}")
        self.conditions_validated += 1
        self._validate_condition_log(condition, condition_value, value, result)
        return result
