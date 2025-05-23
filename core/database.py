import typing
from datetime import datetime
from logging import LogRecord
from multiprocessing import Lock
from pathlib import Path

from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker, Session, Query

from core.config import Config
from core.singleton import SingletonMeta
from models.base import Base
from models.group import Group
from models.log import Log
from models.message import Message


class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.__engine = None
        self.__session = None
        self.lock = Lock()

    def add(self, obj):
        with self.lock:
            self.__session.add(obj)

    def add_all(self, objs):
        with self.lock:
            self.__session.add_all(objs)

    def commit(self):
        with self.lock:
            self.__session.commit()

    def new_session(self):
        connect_args = {"check_same_thread": False}
        self.__engine = create_engine(
            f"sqlite:///{Config.get("database")}", connect_args=connect_args
        )
        Base.metadata.create_all(self.__engine)
        session_factory = sessionmaker(bind=self.__engine)
        return session_factory()

    def update_session(self):
        self.end_session()
        self.__session = self.new_session()

    def end_session(self):
        if self.__session:
            self.__session.close()
        if self.__engine:
            self.__engine.dispose()

    def backup(self, new_database: typing.Union[str, Path]):
        with self.lock:
            self.__session.execute(text(f"VACUUM INTO '{str(new_database)}'"))

    def merge(self, obj):
        with self.lock:
            self.__session.merge(obj)

    def delete(self, obj):
        with self.lock:
            self.__session.delete(obj)

    def message_names(self) -> typing.List[str]:
        with self.lock:
            return [str(i[0]) for i in self.__session.query(Message.name).all()]

    def get_messages(self):
        with self.lock:
            return self.__session.query(Message).all()

    def get_message(self, name: str) -> typing.Optional[Message]:
        with self.lock:
            return self.__session.query(Message).filter_by(name=name).first()

    def get_group(self, id_: int) -> typing.Optional[Group]:
        with self.lock:
            return self.__session.query(Group).filter_by(id=id_).first()

    def get_session(self) -> Session:
        return self.__session

    def delete_messages(self):
        for message in self.get_messages():
            with self.lock:
                self.__session.delete(message)

    def new_name(self) -> str:
        int_message_names = list(
            filter(lambda name: name.isnumeric(), self.message_names())
        )
        return str(int(int_message_names[-1]) + 1) if int_message_names else "1"

    def new_message_id(self) -> int:
        with self.lock:
            max_id = self.__session.query(func.max(Message.id)).scalar()
            if max_id is None:
                return 1
            return max_id + 1

    def new_log(self, record: LogRecord):
        created = datetime.fromtimestamp(record.created)
        log = Log(
            datetime=created,
            message=record.getMessage(),
            level_number=record.levelno,
        )
        if Config.get("database") == ":memory:":
            self.__session.add(log)
        else:
            with self.new_session() as session:
                session.add(log)
                session.commit()

    def need_to_commit(self) -> bool:
        return self.__session.new or self.__session.dirty or self.__session.deleted

    def get_logs_query(
        self,
        message: typing.Optional[str] = None,
        date: typing.Optional[datetime.date] = None,
        log_level: typing.Optional[int] = None,
    ) -> Query:
        with self.lock:
            if Config.get("database") == ":memory:":
                query = self.__session.query(Log)
            else:
                query = self.new_session().query(Log)
            if message:
                query = query.filter(Log.message.like(f"%{message}%"))
            if date:
                query = query.filter(Log.datetime.date() == date)
            if log_level:
                query = query.filter(Log.level_number == log_level)
            return query

    def get_logs_page(
        self, logs_query: Query, page: int, per_page: int
    ) -> typing.List[Log]:
        with self.lock:
            return logs_query.offset((page - 1) * per_page).limit(per_page).all()

    def get_logs_page_count(self, logs_query: Query, per_page: int) -> int:
        with self.lock:
            division = logs_query.count() / per_page
            if division.is_integer():
                return int(division)
            else:
                return int(division) + 1

    def __del__(self):
        """Garante que a sessão e o engine sejam fechados quando o objeto for destruído"""
        self.end_session()
