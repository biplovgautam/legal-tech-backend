from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserMe
from app.models.organization import Organization
from app.models.role import Role
from app.models.organization_member import OrganizationMember
from app.models.member_role import MemberRole
from app.models.user import User

router = APIRouter()

@router.get("/me", response_model=UserMe)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
):
    """
    Get current user details including organization and roles.
    """
    # 1. Find User's Active Membership
    # For MVP, we just grab the first ACTIVE one.
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == current_user.id,
        OrganizationMember.status == "ACTIVE"
    ).first()

    org_id = None
    org_name = None
    org_type = None
    role_names = []

    if membership:
        # Fetch Organization
        org = db.query(Organization).filter(Organization.id == membership.organization_id).first()
        if org:
            org_id = org.id
            org_name = org.name
            org_type = org.org_type

        # Fetch Roles via MemberRole
        # Join MemberRole -> Role
        roles = db.query(Role).join(MemberRole).filter(MemberRole.member_id == membership.id).all()
        role_names = [role.name for role in roles]

    return {
        "id": current_user.id,
        "user_name": current_user.name,
        "user_email": current_user.email,
        "org_id": org_id,
        "org_name": org_name,
        "org_type": org_type,
        "primary_profession": current_user.primary_profession,
        "user_roles": role_names
    }
