from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from app.models.base import Base

class OrganizationMember(Base):
    __tablename__ = "organization_members"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # ENFORCEMENT RULES:
    # If true: System BLOCKS user from joining other Orgs (For Firm Lawyers/Assistants).
    # If false: User can join multiple Orgs (For Clerks).
    is_exclusive = Column(Boolean, default=False)
    
    # ACTIVE | INVITED | LEFT | REMOVED
    status = Column(String, nullable=False, default='ACTIVE')
    
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('organization_id', 'user_id', name='uq_organization_member'),
    )
