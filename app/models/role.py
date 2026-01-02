# Role Model (Organization-scoped)
# app/models/role.py

from sqlalchemy import Column, Integer, String, ForeignKey
from app.models.base import Base

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    name = Column(String, nullable=False)
