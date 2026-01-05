from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal

class UserRegister(BaseModel):
    org_type: Literal["solo", "firm"]
    org_name: Optional[str] = None
    admin_name: str = Field(..., min_length=2, max_length=100)
    admin_email: EmailStr
    admin_password: str = Field(..., min_length=8)
    confirm_admin_password: str = Field(..., min_length=8)

    @validator("confirm_admin_password")
    def passwords_match(cls, v, values, **kwargs):
        if "admin_password" in values and v != values["admin_password"]:
            raise ValueError("Passwords do not match")
        return v

    @validator("org_name")
    def validate_org_name(cls, v, values, **kwargs):
        org_type = values.get("org_type")
        if org_type == "firm" and not v:
            raise ValueError("Organization name is required for law firms")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    org_type: str
