from typing import Generator, Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.core.security import decode_access_token
from app.core.rbac import check_permission
from app.models.user import User
from app.models.audit import AuditLog

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(auth.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject missing"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

def require_permission(permission: str):
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Missing '{permission}' permission"
            )
        return current_user
    return permission_checker

def record_audit(
    db: Session,
    user_id: Optional[int],
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: str = "127.0.0.1"
):
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details_json=details or {},
            ip_address=ip_address
        )
        db.add(log_entry)
        db.commit()
    except Exception:
        db.rollback()

