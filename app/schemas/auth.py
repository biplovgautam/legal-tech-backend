from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime

class UserRegister(BaseModel):
    law_firm: bool = False
    lawyer: bool = False
    tarik: bool = False
    
    # Conditional fields based on type
    law_firm_name: Optional[str] = None
    lawyer_name: Optional[str] = None
    tarik_name: Optional[str] = None
    
    # Common fields
    admin_name: Optional[str] = None # For Law Firm admin name
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("Passwords do not match")
        return v
    
    @validator("law_firm_name")
    def validate_names(cls, v, values):
        if values.get("law_firm") and not v:
            raise ValueError("Law Firm Name is required")
        return v

    @validator("lawyer_name")
    def validate_lawyer_name(cls, v, values):
        if values.get("lawyer") and not v:
            raise ValueError("Lawyer Name is required")
        return v

    @validator("tarik_name")
    def validate_tarik_name(cls, v, values):
        if values.get("tarik") and not v:
             raise ValueError("Name is required for clerk")
        return v

    @validator("admin_name")
    def validate_admin_name(cls, v, values):
        if values.get("law_firm") and not v:
            raise ValueError("Admin Name is required for Law Firm")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    org_type: str
    primary_profession: str # Added this field
    expires_at: datetime

