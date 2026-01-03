import importlib
import pkgutil
import inspect
import os
from types import ModuleType
from typing import List
from .base import BaseModule
from .registry import ModuleRegistry

class ModuleLoader:
    """
    Se encarga de escanear y cargar módulos dinámicamente desde los directorios configurados.
    """
    
    @staticmethod
    def load_modules(package_path: str):
        """
        Cargar todos los módulos encontrados en un paquete/directorio dado.
        
        Args:
            package_path: Ruta del paquete (ej: 'app.plugins.local')
        """
        try:
            # Importar el paquete base
            package = importlib.import_module(package_path)
            
            # Si es un directorio, iterar sobre sus contenidos
            if hasattr(package, "__path__"):
                for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                    full_name = f"{package_path}.{name}"
                    
                    if is_pkg:
                        # Si es un subpaquete, intentar cargarlo recursivamente o buscar módulo principal
                        try:
                            module = importlib.import_module(full_name)
                            ModuleLoader._find_and_register_module(module)
                        except Exception as e:
                            print(f"Error loading module package {full_name}: {e}")
                    else:
                        # Si es un archivo, cargarlo
                        try:
                            module = importlib.import_module(full_name)
                            ModuleLoader._find_and_register_module(module)
                        except Exception as e:
                            print(f"Error loading module file {full_name}: {e}")
                            
        except ImportError as e:
            print(f"Error importing package {package_path}: {e}")

    @staticmethod
    def _find_and_register_module(module: ModuleType):
        """
        Buscar subclases de BaseModule en un módulo python y registrarlas.
        """
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BaseModule) and 
                obj is not BaseModule):
                
                try:
                    # Instanciar y registrar el módulo
                    instance = obj()
                    ModuleRegistry.register(instance)
                except Exception as e:
                    print(f"Error registering module class {name}: {e}")
