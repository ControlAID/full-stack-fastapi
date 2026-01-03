import importlib
import pkgutil
import inspect
import sys
import os
from typing import List, Type
from app.modules.base import ClientModule

class ModuleLoader:
    def __init__(self, plugin_package="app.modules"):
        self.plugin_package = plugin_package
        self.modules: List[ClientModule] = []

    def load_modules(self, context) -> List[ClientModule]:
        """
        Scans the module package and instantiates all classes 
        inheriting from ClientModule (excluding ClientModule itself).
        """
        self.modules = []
        
        # Ensure package path is in sys.path
        # Use importlib to find the package
        try:
            package = importlib.import_module(self.plugin_package)
        except ImportError as e:
            print(f"Error importing modules package: {e}")
            return []

        # Iterate via pkgutil to find submodules
        # Note: This loads all modules found in app/modules/
        # In the future, we will verify against the API license before loading.
        if hasattr(package, "__path__"):
            for _, name, is_pkg in pkgutil.iter_modules(package.__path__):
                full_name = f"{self.plugin_package}.{name}"
                try:
                    module = importlib.import_module(full_name)
                    
                    # correct module loaded, now find the class
                    for attribute_name in dir(module):
                        attribute = getattr(module, attribute_name)
                        
                        if (inspect.isclass(attribute) and 
                            issubclass(attribute, ClientModule) and 
                            attribute is not ClientModule):
                            
                            # Instantiate and initialize
                            try:
                                instance = attribute(context=context)
                                self.modules.append(instance)
                                print(f"Loaded module: {instance.get_name()}")
                            except Exception as e:
                                print(f"Failed to instantiate {attribute_name}: {e}")
                                
                except Exception as e:
                    print(f"Error loading module {full_name}: {e}")

        return self.modules

    def get_loaded_modules(self):
        return self.modules
