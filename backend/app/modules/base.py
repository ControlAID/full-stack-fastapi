from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter

class ModuleMetadata(BaseModel):
    name: str
    version: str
    description: str
    author: str
    license_required: bool = True
    is_external: bool = False
    dependencies: List[str] = []
    
class BaseModule(ABC):
    """
    Clase base abstracta para todos los módulos del sistema.
    Define el contrato que deben cumplir tanto módulos locales como conectores externos.
    """
    
    def __init__(self):
        self._router = APIRouter()
        self.register_routes()

    @property
    @abstractmethod
    def metadata(self) -> ModuleMetadata:
        """Metadatos del módulo"""
        pass
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Inicializar el módulo.
        Retorna True si la inicialización fue exitosa.
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Tareas de limpieza al apagar el módulo.
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar el estado de salud del módulo.
        Retorna un diccionario con detalles del estado.
        """
        pass
    
    @abstractmethod
    def register_routes(self):
        """
        Registrar las rutas del módulo en self._router
        """
        pass

    @property
    def router(self) -> APIRouter:
        return self._router
