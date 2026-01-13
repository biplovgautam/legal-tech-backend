from sqlalchemy import Column, Integer, ForeignKey
from app.models.base import Base

class MemberRole(Base):
    __tablename__ = "member_roles"

    member_id = Column(Integer, ForeignKey("organization_members.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
