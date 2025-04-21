from sqlalchemy import Column, Text, Integer

from models.base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    welcome_message = Column(Text, nullable=True)
    welcome_message_channel = Column(Integer, nullable=True)
    goodbye_message = Column(Text, nullable=True)
    goodbye_message_channel = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<Group(id='{self.id}')>"
