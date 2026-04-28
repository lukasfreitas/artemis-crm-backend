import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    cell_number = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")
