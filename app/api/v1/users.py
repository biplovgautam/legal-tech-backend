from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.schemas.user import UserMe
from app.models.organization import Organization
from app.models.role import Role
from app.models.user_role import UserRole
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
    # Fetch Organization
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Fetch Roles
    # Join UserRole and Role to get role names for the user
    roles = db.query(Role).join(UserRole).filter(UserRole.user_id == current_user.id).all()
    role_names = [role.name for role in roles]

    return {
        "id": current_user.id,
        "user_name": current_user.name,
        "user_email": current_user.email,
        "org_name": org.name,
        "org_type": org.org_type,
        "user_roles": role_names
    }
