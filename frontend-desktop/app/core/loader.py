import importlib
import importlib.util
import pkgutil
import os
import sys
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
    def load_modules(self, context=None) -> list[ClientModule]:
        self.modules = [] # Initialize self.modules
        
        # 1. Load built-in modules
        built_in_pkg = "app.modules"
        self.modules.extend(self._scan_package(built_in_pkg, context))
        
        # 2. Load downloaded plugins
        # Plugins are in app/plugins/{module_name}/module.py
        # This structure is different from flat app.modules
        plugins_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins")
        if os.path.exists(plugins_dir):
            self.modules.extend(self._scan_plugins_dir(plugins_dir, context))
            
        return self.modules

    def _scan_package(self, package_name: str, context) -> list[ClientModule]:
        modules = []
        try:
            package = importlib.import_module(package_name)
            package_path = package.__path__
            
            for _, name, _ in pkgutil.iter_modules(package_path):
                # Import module
                full_name = f"{package_name}.{name}"
                try:
                    module = importlib.import_module(full_name)
                    
                    # Scan for ClientModule subclasses
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, ClientModule) and 
                            attr is not ClientModule):
                            
                            # Instantiate
                            instance = attr(context)
                            modules.append(instance)
                            print(f"Loaded module: {instance.get_name()}")
                except Exception as e:
                    print(f"Error loading module {full_name}: {e}")
                    
        except ImportError as e:
            print(f"Error importing package {package_name}: {e}")
            
        return modules

    def _scan_plugins_dir(self, plugins_dir: str, context) -> list[ClientModule]:
        modules = []
        # plugins_dir contains subdirectories (one per module)
        # We need to add plugins_dir to sys.path possibly, or import dynamically by path
        
        # Strategy: Iterate directories, look for module.py
        for item in os.listdir(plugins_dir):
            item_path = os.path.join(plugins_dir, item)
            model_file = os.path.join(item_path, "module.py")
            
            if os.path.isdir(item_path) and os.path.exists(model_file):
                try:
                    # Dynamic import from file path
                    spec = importlib.util.spec_from_file_location(f"plugins.{item}", model_file)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # Register package in sys.modules so relative imports might work? 
                        # Ideally plugins shouldn't rely on complex relative imports for now.
                        sys.modules[f"app.plugins.{item}"] = module
                        spec.loader.exec_module(module)
                        
                        # Scan classes
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if (isinstance(attr, type) and 
                                issubclass(attr, ClientModule) and 
                                attr is not ClientModule):
                                
                                instance = attr(context)
                                modules.append(instance)
                                print(f"Loaded plugin: {instance.get_name()}")
                except Exception as e:
                    print(f"Error loading plugin {item}: {e}")
                    
        return modules

    def get_loaded_modules(self):
        return self.modules
