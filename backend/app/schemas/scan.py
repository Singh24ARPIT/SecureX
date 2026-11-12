from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class AgentLogResponse(BaseModel):
    id: int
    agent_name: str
    step_name: str
    status: str
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    execution_duration_ms: float
    created_at: datetime

    class Config:
        from_attributes = True

class ScanCreate(BaseModel):
    target_id: int
    scan_name: Optional[str] = None
    scan_type: str = "full" # full, incremental, targeted_api, retest
    selected_categories: Optional[List[str]] = [
        "access_control",
        "business_logic",
        "authentication",
        "injection",
        "api_security"
    ]
    rate_limit_rps: Optional[float] = 5.0
    auto_verify: bool = True

class ScanResponse(BaseModel):
    id: int
    target_id: int
    scan_name: str
    scan_type: str
    status: str
    triggered_by: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_endpoints: int
    tested_endpoints: int
    vulnerabilities_count: int
    stop_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ScanDetailResponse(ScanResponse):
    agent_logs: List[AgentLogResponse] = []
    config_json: Optional[Dict[str, Any]] = None

