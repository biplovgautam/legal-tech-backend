from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from app.schemas.auth import UserRegister, UserLogin, Token
from app.models.user import User
from app.models.organization import Organization
from app.models.role import Role
from app.models.organization_member import OrganizationMember
from app.models.member_role import MemberRole
from app.core.security import get_password_hash, verify_password, create_access_token
from datetime import timedelta, datetime
from app.core.config import settings
from app.api import deps

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(deps.get_db)):
    # 1. Check if user with email already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Determine registration type and set variables
    # Types: "law_firm" | "solo_lawyer" | "clerk"
    reg_type = None
    if user_in.law_firm:
        reg_type = "law_firm"
    elif user_in.lawyer:
        reg_type = "solo_lawyer"
    elif user_in.tarik:
        reg_type = "clerk"
    else:
        raise HTTPException(status_code=400, detail="Invalid registration type")

    # Common Logic: Create User
    # Determine the name based on type
    full_name = ""
    primary_prof = ""
    
    if reg_type == "law_firm":
        full_name = user_in.admin_name
        primary_prof = "LAWYER" # Admin of a firm is typically a lawyer or senior partner
    elif reg_type == "solo_lawyer":
        full_name = user_in.lawyer_name
        primary_prof = "LAWYER"
    elif reg_type == "clerk":
        full_name = user_in.tarik_name
        primary_prof = "CLERK"
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_password,
        name=full_name,
        primary_profession=primary_prof,
        is_active=True,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Organization Logic
    org_response_data = None
    
    # CASE 1: Law Firm -> Create Firm Org, Join as Admin
    # inputs: law_firm=True, law_firm_name, admin_name, email...
    if reg_type == "law_firm":
        new_org = Organization(
            name=user_in.law_firm_name,
            org_type="FIRM",
            is_active=True
        )
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        
        # Membership for Admin
        membership = OrganizationMember(
            organization_id=new_org.id,
            user_id=new_user.id,
            is_exclusive=True, 
            status="ACTIVE"
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        
        # Create Admin Role & Assign
        admin_role = Role(name="FIRM_ADMIN", organization_id=new_org.id)
        db.add(admin_role)
        db.commit()
        
        member_role = MemberRole(member_id=membership.id, role_id=admin_role.id)
        db.add(member_role)
        db.commit()
        
        org_response_data = {
            "id": new_org.id,
            "name": new_org.name,
            "type": new_org.org_type
        }

    # CASE 2: Solo Lawyer -> Create Solo Org, Join as Admin/Lawyer
    # inputs: lawyer=True, lawyer_name, email...
    # Solo lawyers create a practice where assistants can join later.
    elif reg_type == "solo_lawyer":
        new_org = Organization(
            name=f"{full_name}'s Practice",
            org_type="SOLO", # Allows hiring assistants later
            is_active=True
        )
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
        
        # Membership for Solo Lawyer
        membership = OrganizationMember(
            organization_id=new_org.id,
            user_id=new_user.id,
            is_exclusive=True, # Solo lawyers own their practice
            status="ACTIVE"
        )
        db.add(membership)
        db.commit()
        db.refresh(membership)
        
        # Create Lawyer Role & Assign
        # Solo lawyers act as both Admin and Principle Lawyer
        role = Role(name="SOLO_PRACTITIONER", organization_id=new_org.id)
        db.add(role)
        db.commit()
        
        member_role = MemberRole(member_id=membership.id, role_id=role.id)
        db.add(member_role)
        db.commit()
        
        org_response_data = {
            "id": new_org.id,
            "name": new_org.name,
            "type": new_org.org_type
        }

    # CASE 3: Tarik (Clerk) -> Only User Created
    # inputs: tarik=True, tarik_name, email...
    # Created as a free agent. Can be invited to firms or solo practices later.
    # No organization logic needed here.

    return {
        "message": "Registration successful",
        "user": {
            "id": new_user.id, 
            "email": new_user.email, 
            "name": new_user.name,
            "primary_profession": new_user.primary_profession
        },
        "organization": org_response_data
    }


@router.post("/login", response_model=Token)
def login(response: Response, user_in: UserLogin, db: Session = Depends(deps.get_db)):
    # 1. Authenticate User
    user = db.query(User).filter(User.email == user_in.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not registered. Please sign up first.",
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
    # We check OrganizationMember to get the type
    # For now, we take the first active membership.
    # Future improvement: Allow user to select org if multiple.
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.user_id == user.id,
        OrganizationMember.status == "ACTIVE"
    ).first()
    
    org_id = None
    org_type_str = "NONE" # Default for those with no org (like new clerks)
    
    if membership:
        org = db.query(Organization).filter(Organization.id == membership.organization_id).first()
        if org:
            org_id = org.id
            org_type_str = org.org_type

    # 3. Create Access Token with Tenant Context
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.utcnow() + access_token_expires
    expires_at_http = expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")

    token_payload = {
        "sub": str(user.id),
        # org_id might be None if user is just a clerk with no assignment yet
        "org_id": str(org_id) if org_id else None,
        "org_type": org_type_str,
        "primary_profession": user.primary_profession
    }

    access_token = create_access_token(
        data=token_payload,
        expires_delta=access_token_expires,
    )

    # 4. Set HttpOnly Cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=settings.ENVIRONMENT
        == "production",  # Only secure in production (HTTPS)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "org_type": org_type_str,  # Frontend uses this to redirect
        "primary_profession": user.primary_profession, # Also needed for redirection decision
        "expires_at": expires_at,
        "expires_at_http": expires_at_http,
    }


@router.post("/logout")
def logout(response: Response, current_user: User = Depends(deps.get_current_user)):
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
    )
    return {"message": "Logged out successfully"}
