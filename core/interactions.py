import json
import typing
from pathlib import Path


class Interactions:
    def __init__(self):
        self.__content = {}

    def load(self, path: Path):
        with open(path, "r") as json_file:
            self.__content = json.load(json_file)

    def save(self, path: Path):
        with open(path, "w") as file:
            file.write(json.dumps(self.__content))

    def set(self, key: str, data: dict):
        self.__content[key] = data

    def get(self, key: str):
        return self.__content[key]

    def delete(self, key: str):
        self.__content.pop(key)

    def clear(self):
        self.__content = {}

    def message_names(self) -> typing.List[str]:
        return list(self.get("messages").keys())

    def content(self) -> dict:
        return self.__content

    def new_id(self) -> str:
        int_message_names = list(
            filter(lambda name: name.isnumeric(), self.message_names())
        )
        return str(int(int_message_names[-1]) + 1) if int_message_names else "1"

    def is_valid(self) -> bool:
        return all(
            map(lambda message: isinstance(message, str), self.message_names())
        ) and all(
            map(lambda message: self.is_message(message), self.get("messages").values())
        )

    @staticmethod
    def is_message(message: dict) -> bool:
        fields = [
            "expected message",
            "reply",
            "reaction",
            "conditions",
            "pin or del",
            "kick or ban",
            "where reply",
            "where reaction",
            "delay",
        ]
        return all(map(lambda field: field in message, fields))


interactions = Interactions()
