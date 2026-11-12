from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ApiParameterResponse(BaseModel):
    id: int
    name: str
    in_location: str
    data_type: str
    is_required: bool
    description: Optional[str] = None
    example_value: Optional[str] = None

    class Config:
        from_attributes = True

class ApiInventoryHistoryResponse(BaseModel):
    id: int
    change_type: str
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    diff_summary: Optional[str] = None
    detected_at: datetime

    class Config:
        from_attributes = True

class ApiEndpointResponse(BaseModel):
    id: int
    target_id: int
    path: str
    method: str
    summary: Optional[str] = None
    description: Optional[str] = None
    auth_required: bool
    required_roles: Optional[str] = None
    classification: str # active, zombie, shadow
    risk_score: float
    first_seen: datetime
    last_seen: datetime
    is_deprecated: bool
    recommendation: Optional[str] = None
    parameters: List[ApiParameterResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EndpointClassificationUpdate(BaseModel):
    classification: str # active, zombie, shadow
    recommendation: Optional[str] = None

class DeploymentEventCreate(BaseModel):
    target_id: int
    service_name: str
    commit_sha: str
    branch: str = "main"
    triggered_by: str = "ci/cd-webhook"
    event_type: str = "api_deploy"
    payload_json: Optional[Dict[str, Any]] = None

class DeploymentEventResponse(BaseModel):
    id: int
    target_id: int
    service_name: str
    commit_sha: str
    branch: str
    triggered_by: str
    event_type: str
    payload_json: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
