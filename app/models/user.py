from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    # organization_id removed (moved to organization_members)

    name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True, index=True)
    phone_number = Column(String, unique=True, nullable=True, index=True, comment="E.164 standard format recommended")
    hashed_password = Column(String, nullable=False)
    
    # Global app behavior
    # LAWYER | CLERK | ADMIN_STAFF
    primary_profession = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)

    # Timestamps for user tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())