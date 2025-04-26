from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    pin_or_del = Column(String, nullable=True)
    kick_or_ban = Column(String, nullable=True)
    where_reply = Column(String, nullable=True)
    where_reaction = Column(String, nullable=True)
    delay = Column(Integer, default=0)

    # Relacionamentos one-to-many
    replies = relationship(
        "MessageReply", back_populates="message", cascade="all, delete-orphan"
    )
    reactions = relationship(
        "MessageReaction", back_populates="message", cascade="all, delete-orphan"
    )
    conditions = relationship(
        "MessageCondition", back_populates="message", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Message(name='{self.name}')>"
