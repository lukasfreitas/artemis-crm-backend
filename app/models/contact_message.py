from datetime import datetime, timezone
from enum import Enum
import uuid

from sqlalchemy import Column, DateTime, String, Text

from app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class ContactMessageStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    CONTACTED = "contacted"
    CONVERTED = "converted"
    DISCARDED = "discarded"


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    whatsapp = Column(String, nullable=False)
    company = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String, nullable=False, default=ContactMessageStatus.NEW.value, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
