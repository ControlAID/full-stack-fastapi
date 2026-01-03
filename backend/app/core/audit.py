import uuid
from typing import Optional
from fastapi import Request
from sqlmodel import Session

from app.models import AuditLog, User

def log_action(
    session: Session,
    action: str,
    target: str,
    details: Optional[str] = None,
    level: str = "info",
    user: Optional[User] = None,
    organization_id: Optional[uuid.UUID] = None,
    request: Optional[Request] = None
) -> None:
    """
    Record an action in the audit log.
    """
    ip_address = None
    if request:
        # Try to get real IP from headers if behind proxy
        ip_address = request.headers.get("X-Forwarded-For") or request.client.host if request.client else None
        
    audit_entry = AuditLog(
        user_id=user.id if user else None,
        action=action,
        target=target,
        details=details,
        level=level,
        ip_address=ip_address,
        organization_id=organization_id or (user.organization_id if user else None)
    )
    session.add(audit_entry)
    session.commit()
