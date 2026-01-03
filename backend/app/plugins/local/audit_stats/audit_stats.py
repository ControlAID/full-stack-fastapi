import logging
from datetime import datetime, timedelta
from typing import Dict, Any

from fastapi import Depends
from sqlmodel import select, func

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import AuditLog
from app.modules.base import BaseModule, ModuleMetadata

logger = logging.getLogger(__name__)

class AuditStatsModule(BaseModule):
    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            name="audit_stats",
            version="1.1.0",
            description="Módulo interno optimizado para análisis de logs de auditoría",
            author="ControlAI",
            license_required=True,
            is_external=False
        )
    
    async def initialize(self) -> bool:
        logger.info("Audit Stats Module v1.1.0 initialized")
        return True
    
    async def shutdown(self) -> bool:
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "ok",
            "database_connected": True,
            "monitored_model": "AuditLog"
        }
    
    def register_routes(self):
        @self.router.get("/summary", dependencies=[Depends(get_current_active_superuser)])
        async def get_summary(session: SessionDep):
            """
            Retorna estadísticas avanzadas de logs agrupadas por nivel y tiempo.
            """
            # 1. Resumen Total usando GROUP BY
            statement = select(AuditLog.level, func.count(AuditLog.id)).group_by(AuditLog.level)
            results = session.exec(statement).all()
            
            breakdown = {level: count for level, count in results}
            # Asegurar que todos los niveles existan en el dict
            for level in ["info", "warning", "error", "success"]:
                breakdown.setdefault(level, 0)

            # 2. Estadísticas de las últimas 24 horas
            last_24h = datetime.utcnow() - timedelta(hours=24)
            recent_statement = select(AuditLog.level, func.count(AuditLog.id))\
                .where(AuditLog.timestamp >= last_24h)\
                .group_by(AuditLog.level)
            recent_results = session.exec(recent_statement).all()
            
            breakdown_24h = {level: count for level, count in recent_results}
            for level in ["info", "warning", "error", "success"]:
                breakdown_24h.setdefault(level, 0)
            
            return {
                "total_stats": {
                    "total": sum(breakdown.values()),
                    "breakdown": breakdown
                },
                "recent_stats_24h": {
                    "total": sum(breakdown_24h.values()),
                    "breakdown": breakdown_24h
                },
                "generated_at": datetime.utcnow()
            }
