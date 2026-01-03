try:
    import psutil
except ImportError:
    psutil = None
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends
from sqlmodel import select, func

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import Organization, User, License, AuditLog, SystemMetrics, SystemCounts, LogsPublic, ModulesPublic, ModulePublic

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


def get_growth(session: SessionDep, model: Any) -> float:
    """Calculate percentage growth between last 30 days and previous 30 days."""
    try:
        now = datetime.utcnow()
        last_30_days_start = now - timedelta(days=30)
        prev_30_days_start = now - timedelta(days=60)
        
        # Count for last 30 days
        last_30_statement = select(func.count()).select_from(model).where(model.created_at >= last_30_days_start)
        last_30_count = session.exec(last_30_statement).one()
        
        # Count for previous 30 days (the "base" for growth)
        prev_30_statement = select(func.count()).select_from(model).where(
            model.created_at >= prev_30_days_start,
            model.created_at < last_30_days_start
        )
        prev_30_count = session.exec(prev_30_statement).one()
        
        if prev_30_count == 0:
            return 100.0 if last_30_count > 0 else 0.0
            
        return (last_30_count / prev_30_count) * 100.0
    except Exception as e:
        print(f"Error calculating growth for {model}: {e}")
        return 0.0


@router.get("/metrics", dependencies=[Depends(get_current_active_superuser)])
def get_metrics(session: SessionDep) -> SystemMetrics:
    """
    Get real-time system metrics and summary statistics.
    """
    # System metrics
    if psutil:
        cpu_usage = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
    else:
        cpu_usage = 0.0
        memory_usage = 0.0
    
    # DB metrics & Summary stats
    try:
        org_count = session.exec(select(func.count()).select_from(Organization)).one()
        user_count = session.exec(select(func.count()).select_from(User)).one()
        license_count = session.exec(select(func.count()).select_from(License)).one()
        
        org_growth = get_growth(session, Organization)
        user_growth = get_growth(session, User)
        license_growth = get_growth(session, License)
        
        db_status = "stable"
    except Exception:
        db_status = "error"
        org_count = 0
        user_count = 0
        license_count = 0
        org_growth = 0.0
        user_growth = 0.0
        license_growth = 0.0

    return {
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "db_status": db_status,
        "counts": {
            "organizations": org_count,
            "organizations_growth": org_growth,
            "users": user_count,
            "users_growth": user_growth,
            "licenses": license_count,
            "licenses_growth": license_growth,
        },
        "timestamp": datetime.utcnow()
    }


@router.get("/logs", dependencies=[Depends(get_current_active_superuser)])
def get_logs(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
    level: Optional[str] = None,
    target: Optional[str] = None
) -> LogsPublic:
    """
    Get paginated audit logs for superusers.
    """
    statement = select(AuditLog)
    if level:
        statement = statement.where(AuditLog.level == level)
    if target:
        statement = statement.where(AuditLog.target.ilike(f"%{target}%"))
        
    count_statement = select(func.count()).select_from(statement.subquery())
    
    statement = statement.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit)
    logs = session.exec(statement).all()
    count = session.exec(count_statement).one()
    return LogsPublic(data=logs, count=count)


@router.get("/modules", dependencies=[Depends(get_current_active_superuser)])
def get_modules() -> ModulesPublic:
    """
    Get all registered modules.
    """
    from app.modules.registry import ModuleRegistry
    modules = ModuleRegistry.list_modules()
    return ModulesPublic(data=modules)
