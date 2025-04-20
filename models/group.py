from sqlalchemy import Column, String, Text, Integer

from models.base import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)  # ID do Discord como string
    welcome_message = Column(Text, nullable=True)
    welcome_message_channel = Column(Integer, nullable=True)  # ID do canal como string

    def __repr__(self):
        return f"<Group(id='{self.id}')>"
