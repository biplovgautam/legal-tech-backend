from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.auth import UserRegister
from app.models.user import User
from app.models.organization import Organization
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import get_password_hash

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    # 1. Check if user with email already exists
    user = db.query(User).filter(User.email == user_in.admin_email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # 2. Determine Organization Name
    org_name = user_in.org_name
    if user_in.org_type == "solo":
        org_name = user_in.admin_name  # Use admin name for solo practice
    
    # 3. Create Organization
    new_org = Organization(
        name=org_name,
        org_type=user_in.org_type.upper(), # Store as SOLO or FIRM
        is_active=True
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    # 4. Create User
    hashed_password = get_password_hash(user_in.admin_password)
    new_user = User(
        email=user_in.admin_email,
        hashed_password=hashed_password,
        name=user_in.admin_name,
        organization_id=new_org.id,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 5. Create "Super Admin" Role for this Organization
    # Note: In a real app, you might have a set of default roles to create
    admin_role = Role(
        name="Super Admin",
        organization_id=new_org.id
    )
    db.add(admin_role)
    db.commit()
    db.refresh(admin_role)

    # 6. Assign Role to User
    user_role = UserRole(
        user_id=new_user.id,
        role_id=admin_role.id
    )
    db.add(user_role)
    db.commit()

    return {
        "message": "Registration successful",
        "organization": {
            "id": new_org.id,
            "name": new_org.name,
            "type": new_org.org_type
        },
        "user": {
            "id": new_user.id,
            "email": new_user.email,
            "name": new_user.name
        }
    }
