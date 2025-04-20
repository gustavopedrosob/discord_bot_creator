import logging
from core.bot import Bot
from core.config import instance as config


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%x %X",
    )
    bot = Bot()
    bot.run(config.get("token"))
