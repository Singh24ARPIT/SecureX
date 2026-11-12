from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class TargetBase(BaseModel):
    name: str
    target_url: str
    environment: str = "staging"
    is_approved: bool = True
    approval_notes: Optional[str] = None
    rate_limit_rps: float = 5.0

class TargetCreate(TargetBase):
    pass

class TargetUpdate(BaseModel):
    name: Optional[str] = None
    target_url: Optional[str] = None
    environment: Optional[str] = None
    is_approved: Optional[bool] = None
    approval_notes: Optional[str] = None
    rate_limit_rps: Optional[float] = None

class TargetResponse(TargetBase):
    id: int
    approved_by: str
    health_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

