from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from app.services.license import LicenseService

class BindingDialog(QDialog):
    def __init__(self, license_service: LicenseService, parent=None):
        super().__init__(parent)
        self.license_service = license_service
        self.setWindowTitle("Vincular Dispositivo")
        self.setFixedSize(400, 300)
        self.setModal(True)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("Dispositivo No Registrado")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #d9534f;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        info = QLabel(f"MAC: {self.license_service.mac_address}\n\nEste equipo no está vinculado a su organización.\nPor favor ingrese un nombre para registrarlo.")
        info.setWordWrap(True)
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del Punto de Acceso (ej. Recepción)")
        layout.addWidget(self.name_input)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Ubicación (ej. Torre A)")
        layout.addWidget(self.location_input)
        
        self.bind_btn = QPushButton("Vincular y Continuar")
        self.bind_btn.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        self.bind_btn.clicked.connect(self.handle_bind)
        layout.addWidget(self.bind_btn)

    def handle_bind(self):
        name = self.name_input.text()
        location = self.location_input.text()
        
        if not name or not location:
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
            
        success = self.license_service.register_device(name, location)
        
        if success:
            QMessageBox.information(self, "Éxito", "Dispositivo vinculado correctamente.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo vincular el dispositivo.\nVerifique permisos o límite de licencias.")
