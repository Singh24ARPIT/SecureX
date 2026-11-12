from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.scan import AgentExecutionLog
from app.models.user import User
from app.schemas.scan import AgentLogResponse
from app.api.deps import get_current_user, require_permission

router = APIRouter(prefix="/agents", tags=["Agent Activity Center"])

AGENTS_METADATA = [
    {
        "id": "agent-1",
        "name": "Change Detection Agent",
        "type": "Perception & CI/CD",
        "assigned_task": "Monitor deployments, compare OpenAPI definitions, detect endpoint diffs",
        "supported_protocols": ["Webhooks", "Git Commits", "Schema Hash Diffs"],
        "status": "active"
    },
    {
        "id": "agent-2",
        "name": "Recon Discovery Agent",
        "type": "Discovery & Knowledge Graph",
        "assigned_task": "Enumerate endpoints (GET, POST, PUT, DELETE), analyze parameter trees & auth headers",
        "supported_protocols": ["OpenAPI", "Crawler", "Route Introspection"],
        "status": "active"
    },
    {
        "id": "agent-3",
        "name": "API Inventory Agent",
        "type": "Governance & Asset Tagging",
        "assigned_task": "Classify endpoints into Active, Zombie, and Shadow APIs; issue decommissioning guidance",
        "supported_protocols": ["Inventory Analysis", "Heuristic Drift"],
        "status": "active"
    },
    {
        "id": "agent-4",
        "name": "Attack Planning Agent",
        "type": "Reasoning & Test Synthesis",
        "assigned_task": "Generate targeted test matrix based on endpoint semantics and business context",
        "supported_protocols": ["Heuristic Planner", "Contextual Rules"],
        "status": "active"
    },
    {
        "id": "agent-5",
        "name": "Security Testing Agents (5-Pack)",
        "type": "Active Execution Suite",
        "assigned_task": "Execute Access Control (IDOR), Business Logic (Fare/Refund), Auth, and API Security checks",
        "supported_protocols": ["HTTPX", "Contract Asserts", "Tenant Headers"],
        "status": "active"
    },
    {
        "id": "agent-6",
        "name": "Safety & Policy Agent",
        "type": "Deterministic Security Gatekeeper",
        "assigned_task": "Scope boundary enforcement, rate limiting (RPS throttle), health tripwires, non-destructive bounds",
        "supported_protocols": ["Token Bucket", "Allowlist Checker", "Health Ping"],
        "status": "active"
    },
    {
        "id": "agent-7",
        "name": "Vulnerability Verification Agent",
        "type": "Proof & False-Positive Filter",
        "assigned_task": "Recheck detected flaws with deterministic response assertions to eliminate hallucinations",
        "supported_protocols": ["Minimal Proof Engine", "Diff Assertion"],
        "status": "active"
    },
    {
        "id": "agent-8",
        "name": "Risk & Severity Assessment Agent",
        "type": "Business Risk & CVSS Scorer",
        "assigned_task": "Evaluate business impact, cross-agency risks, financial loss, and CVSS severity scoring",
        "supported_protocols": ["CVSS v3.1 Logic", "Financial Risk Heuristics"],
        "status": "active"
    },
    {
        "id": "agent-9",
        "name": "Reporting Agent",
        "type": "Actionable Synthesis",
        "assigned_task": "Generate executive audit reports, remediation steps, CSV/PDF/JSON exports",
        "supported_protocols": ["CSV Engine", "JSON Exporter", "Markdown Builder"],
        "status": "active"
    },
    {
        "id": "agent-10",
        "name": "Retesting Agent",
        "type": "Post-Fix Continuous Verification",
        "assigned_task": "Rerun original targeted attack vectors after developer patches to confirm resolution",
        "supported_protocols": ["Baseline Diff Engine", "Regression Tester"],
        "status": "active"
    }
]

@router.get("/status")
def get_agents_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:read"))
):
    recent_logs = db.query(AgentExecutionLog).order_by(
        AgentExecutionLog.created_at.desc()
    ).limit(10).all()

    # Match each agent with its latest activity
    agents_state = []
    for agent_meta in AGENTS_METADATA:
        latest = db.query(AgentExecutionLog).filter(
            AgentExecutionLog.agent_name.ilike(f"%{agent_meta['name'].split()[0]}%")
        ).order_by(AgentExecutionLog.created_at.desc()).first()

        agents_state.append({
            **agent_meta,
            "last_active": latest.created_at if latest else None,
            "last_step": latest.step_name if latest else "Standby - Waiting for next scan or deployment event",
            "last_status": latest.status if latest else "idle"
        })

    return {
        "total_agents": len(AGENTS_METADATA),
        "active_agents": len(AGENTS_METADATA),
        "agents": agents_state,
        "recent_activity": recent_logs
    }

@router.get("/logs", response_model=List[AgentLogResponse])
def get_all_agent_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("scans:read"))
):
    return db.query(AgentExecutionLog).order_by(
        AgentExecutionLog.created_at.desc()
    ).limit(limit).all()

