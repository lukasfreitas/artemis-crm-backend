import uuid

from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class PermissionGroup(Base):
    __tablename__ = "permission_groups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)
    is_influencer = Column(Boolean, default=False, nullable=False)

    users = relationship("User", back_populates="permission_group")
