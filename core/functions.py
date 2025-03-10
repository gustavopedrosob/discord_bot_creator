import logging
import re
from datetime import datetime

from core.config import instance as config


def has_number(string: str) -> bool:
    return any(char.isnumeric() for char in string)


def has_symbols(string: str) -> bool:
    return bool(re.search(r"[-!$%^&*()_+|~=`{}\[\]:\";'<>?,./\\´§¨#@ªº°]", string))


def get_time(string: str):
    return datetime.now().strftime(string)


def config_log_level(level: int):
    logging.getLogger("main").setLevel(level)
    logging.getLogger("bot").setLevel(level)
    config.set("log_level", level)
    config.save()
