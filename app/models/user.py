from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from app.core.database import Base
import uuid


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)
    permission_group_id = Column(String, ForeignKey("permission_groups.id"), nullable=True, index=True)
    permission_group = relationship("PermissionGroup", back_populates="users")
    auth_sessions = relationship("AuthSession", backref="user", cascade="all, delete-orphan")
    profile = relationship(
        "UserProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    @property
    def is_admin(self):
        return bool(self.permission_group and self.permission_group.is_admin)

    @property
    def is_influencer(self):
        return bool(self.permission_group and self.permission_group.is_influencer)
