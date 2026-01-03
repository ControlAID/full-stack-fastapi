from app.modules.base import ClientModule
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QAction

class DummyModule(ClientModule):
    def get_name(self) -> str:
        return "dummy_module"

    def get_display_name(self) -> str:
        return "Panel de Prueba"

    def get_icon(self) -> str:
        return "help"

    def init_ui(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("¡Hola! Soy un módulo cargado dinámicamente.")
        label.setStyleSheet("font-size: 18px; color: green;")
        layout.addWidget(label)
        
        info = QLabel("Este contenido viene de 'app.modules.dummy.dummy_module'")
        layout.addWidget(info)
        
        self.widget = widget
        return widget
    
    def get_menu_action(self):
        # We can return an action to be added to the View menu or similar
        return None
