import logging
import os
import yaml


class Config:
    __content: dict

    def __init__(self):
        if os.path.exists("config.yaml"):
            self.load()
        else:
            self.__content = {
                "token": "",
                "language": "en_us",
                "file": "source/message and reply.json",
                "log_level": logging.INFO,
            }
            self.save()

    def load(self):
        with open("config.yaml", "r") as arquivo:
            self.__content = yaml.load(arquivo, Loader=yaml.FullLoader)

    def save(self):
        with open("config.yaml", "w") as arquivo:
            yaml.dump(self.__content, arquivo)

    def get(self, variable):
        return self.__content[variable]

    def set(self, variable, value):
        self.__content[variable] = value


instance = Config()
