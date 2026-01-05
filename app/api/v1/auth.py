from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.schemas.auth import UserRegister, UserLogin, Token
from app.models.user import User
from app.models.organization import Organization
from app.models.role import Role
from app.models.user_role import UserRole
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings

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

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    # 1. Authenticate User
    user = db.query(User).filter(User.email == user_in.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered!",
        )

    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 2. Get Organization Type for Dashboard Routing
    # We join with Organization to get the type
    org = db.query(Organization).filter(Organization.id == user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # 3. Create Access Token with Tenant Context
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "org_id": str(user.organization_id),
            "org_type": org.org_type
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "org_type": org.org_type # Frontend uses this to redirect
    }
