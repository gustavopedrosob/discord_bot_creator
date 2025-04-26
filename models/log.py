from sqlalchemy import Column, Integer, String, DateTime

from models.base import Base
import logging


class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    message = Column(String)
    level_number = Column(Integer)

    @property
    def date(self):
        return self.datetime.date()

    @property
    def level(self):
        return logging.getLevelName(self.level_number)
