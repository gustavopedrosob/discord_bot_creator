from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from models.base import Base


class MessageReply(Base):
    __tablename__ = "message_replies"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    text = Column(Text, nullable=False)

    # Relacionamento many-to-one
    message = relationship("Message", back_populates="replies")

    def __repr__(self):
        return f"<MessageReply(text='{self.text}')>"
