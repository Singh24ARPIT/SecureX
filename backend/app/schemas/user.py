from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    role: str = "security_engineer"
    agency_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
