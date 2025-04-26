from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models.base import Base


class MessageCondition(Base):
    __tablename__ = "message_conditions"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False)
    field = Column(String, nullable=False)
    operator = Column(String, nullable=False)
    value = Column(String, nullable=False)
    case_insensitive = Column(Boolean, nullable=True, default=False)

    # Relacionamento many-to-one
    message = relationship("Message", back_populates="conditions")

    def __repr__(self):
        return f"<MessageCondition(field='{self.field}', operator='{self.operator}', value='{self.value}')>"
