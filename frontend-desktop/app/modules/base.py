from abc import ABC, abstractmethod
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QAction
from typing import Optional

class ClientModule(ABC):
    """
    Base class for all Desktop UI Modules.
    Similar to backend's BaseModule but focused on UI.
    """
    
    def __init__(self, context=None):
        self.context = context  # Access to main window, services, etc.
        self.widget: Optional[QWidget] = None

    @abstractmethod
    def get_name(self) -> str:
        """Unique identifier for the module"""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """User-friendly name for menus/tabs"""
        pass

    @abstractmethod
    def get_icon(self) -> str:
        """Icon name (e.g., 'home', 'camera')"""
        pass

    @abstractmethod
    def init_ui(self) -> QWidget:
        """
        Initialize and return the main widget for this module.
        This is called when the module is activated.
        """
        pass

    def on_load(self):
        """Called when the module is loaded by the application"""
        pass

    def on_unload(self):
        """Called when the module is unloaded"""
        pass
        
    def get_menu_action(self) -> Optional[QAction]:
        """
        Optional: Return a QAction to add to the main menu/sidebar.
        Default is None (no menu item).
        """
        return None
