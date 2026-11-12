from enum import Enum
from typing import List
from fastapi import HTTPException, status

class UserRole(str, Enum):
    ADMIN = "admin"
    SECURITY_ENGINEER = "security_engineer"
    AUDITOR = "auditor"
    AGENCY_ADMIN = "agency_admin"

ROLE_PERMISSIONS = {
    UserRole.ADMIN: [
        "scans:create", "scans:read", "scans:delete", "scans:stop",
        "targets:create", "targets:read", "targets:update", "targets:delete",
        "apis:read", "apis:discover", "apis:classify",
        "vulns:read", "vulns:verify", "vulns:retest", "vulns:update",
        "reports:read", "reports:generate",
        "audit:read",
        "users:manage"
    ],
    UserRole.SECURITY_ENGINEER: [
        "scans:create", "scans:read", "scans:stop",
        "targets:read",
        "apis:read", "apis:discover", "apis:classify",
        "vulns:read", "vulns:verify", "vulns:retest", "vulns:update",
        "reports:read", "reports:generate",
        "audit:read"
    ],
    UserRole.AUDITOR: [
        "scans:read",
        "targets:read",
        "apis:read",
        "vulns:read",
        "reports:read",
        "audit:read"
    ],
    UserRole.AGENCY_ADMIN: [
        "agency:bookings:read", "agency:bookings:write"
    ]
}

def check_permission(user_role: str, required_permission: str) -> bool:
    perms = ROLE_PERMISSIONS.get(user_role, [])
    return required_permission in perms
