from typing import Dict, List, Optional
from .base import BaseModule

class ModuleRegistry:
    """
    Registro central de módulos del sistema.
    Gestiona el ciclo de vida y acceso a los módulos cargados.
    """
    _instance = None
    _modules: Dict[str, BaseModule] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleRegistry, cls).__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, module: BaseModule):
        """Registrar una instancia de un módulo"""
        if module.metadata.name in cls._modules:
            raise ValueError(f"Module {module.metadata.name} is already registered")
        cls._modules[module.metadata.name] = module
        print(f"Module registered: {module.metadata.name} v{module.metadata.version}")

    @classmethod
    def get_module(cls, name: str) -> Optional[BaseModule]:
        """Obtener un módulo por su nombre"""
        return cls._modules.get(name)

    @classmethod
    def list_modules(cls) -> List[Dict]:
        """Listar todos los módulos registrados y sus metadatos"""
        return [
            module.metadata.model_dump() 
            for module in cls._modules.values()
        ]

    @classmethod
    def get_all_modules(cls) -> List[BaseModule]:
        """Obtener todas las instancias de módulos"""
        return list(cls._modules.values())
