from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import Base
from sqlalchemy.sql import func

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    org_type = Column(String, nullable=False)  # LAW_FIRM | SOLO
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

