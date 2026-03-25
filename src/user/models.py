from sqlalchemy import Column, String, Integer, DateTime, Boolean
from src.utils.db import Base
from datetime import datetime, timezone

class UserModel(Base):
    __tablename__ = "user_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String, unique=True, nullable=False, index=True)
    hash_password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

