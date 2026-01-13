from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserMe(BaseModel):
    id: int
    user_name: Optional[str]
    user_email: EmailStr
    org_name: Optional[str] = None
    org_type: Optional[str] = None
    user_roles: List[str] = []

    class Config:
        from_attributes = True
