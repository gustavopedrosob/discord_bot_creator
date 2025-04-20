from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from models.base import Base


class MessageCondition(Base):
    __tablename__ = "message_conditions"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    condition = Column(String, nullable=False)

    # Relacionamento many-to-one
    message = relationship("Message", back_populates="conditions")

    def __repr__(self):
        return f"<MessageCondition(condition='{self.condition}')>"
