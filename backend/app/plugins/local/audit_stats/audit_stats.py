import uuid
from typing import Dict, Any
from app.modules.base import BaseModule, ModuleMetadata
from app.api.deps import SessionDep
from app.models import AuditLog
from sqlmodel import select, func
from fastapi import Depends
from app.api.deps import get_current_active_superuser

class AuditStatsModule(BaseModule):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="audit_stats",
            version="1.0.0",
            description="Módulo interno para estadísticas de auditoría",
            author="ControlAI",
            license_required=True,
            is_external=False
        )
    
    async def initialize(self) -> bool:
        print("Audit Stats Module initialized")
        return True
    
    async def shutdown(self) -> bool:
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        return {"status": "ok"}
    
    def register_routes(self):
        @self.router.get("/summary", dependencies=[Depends(get_current_active_superuser)])
        async def get_summary(session: SessionDep):
            """
            Retorna un resumen de logs por nivel.
            """
            stats = {}
            for level in ["info", "warning", "error", "success"]:
                statement = select(func.count()).select_from(AuditLog).where(AuditLog.level == level)
                count = session.exec(statement).one()
                stats[level] = count
            
            return {
                "total": sum(stats.values()),
                "breakdown": stats
            }
