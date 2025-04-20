from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from models.base import Base


class MessageReaction(Base):
    __tablename__ = "message_reactions"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    reaction = Column(String, nullable=False)  # Emoji ou ID do emoji personalizado

    # Relacionamento many-to-one
    message = relationship("Message", back_populates="reactions")

    def __repr__(self):
        return f"<MessageReaction(reaction='{self.reaction}')>"
