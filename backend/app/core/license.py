from datetime import datetime
from typing import Optional
from sqlmodel import Session, select
from app.models import License, Organization, LicenseTier

class LicenseService:
    """
    Servicio para validar y gestionar licencias de organizaciones.
    """

    @staticmethod
    def get_active_license(session: Session, organization_id: str) -> Optional[License]:
        """
        Obtener la licencia activa de una organización.
        """
        statement = select(License).where(
            License.organization_id == organization_id,
            License.is_active == True,
            License.valid_until > datetime.utcnow()
        )
        return session.exec(statement).first()

    @staticmethod
    def is_module_enabled(session: Session, organization_id: str, module_name: str) -> bool:
        """
        Verificar si un módulo está habilitado para una organización.
        """
        license = LicenseService.get_active_license(session, organization_id)
        
        if not license:
            return False
            
        # Definir módulos base por tier (esto podría estar en configuración o BD)
        base_modules = {
            LicenseTier.STARTER: ["qr", "access_control", "audit"],
            LicenseTier.BUSINESS: ["qr", "access_control", "audit", "face_recognition"],
            LicenseTier.ENTERPRISE: ["qr", "access_control", "audit", "face_recognition", "voice_id", "analytics"]
        }
        
        allowed_modules = base_modules.get(license.tier, []) + license.addon_modules
        
        return module_name in allowed_modules

    @staticmethod
    def check_limits(session: Session, organization_id: str, resource_type: str, current_count: int) -> bool:
        """
        Verificar si se han excedido los límites de la licencia.
        resource_type: 'users', 'devices', 'locations'
        """
        license = LicenseService.get_active_license(session, organization_id)
        if not license:
            return False
            
        if resource_type == "users":
            return current_count < license.max_users
        elif resource_type == "devices":
            return current_count < license.max_devices
        elif resource_type == "locations":
            return current_count < license.max_locations
            
        return False
