from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from app.services.auth import AuthService

class LoginWindow(QWidget):
    login_successful = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ControlAI - Login")
        self.setFixedSize(400, 500)
        # Using qt-material theme, removing hardcoded styles
        # self.setStyleSheet(...) 

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Card container
        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)

        # Title
        title = QLabel("ControlAI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setProperty("class", "danger") # Use material classes if supported or just inherit
        card_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Monitoring Station")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # subtitle.setStyleSheet("font-size: 16px; color: #666; margin-bottom: 20px;")
        card_layout.addWidget(subtitle)

        # Inputs
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        card_layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        card_layout.addWidget(self.password_input)

        # Button
        self.login_btn = QPushButton("Iniciar Sesión")
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_btn)

        layout.addWidget(card)

    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("Conectando...")
        
        # Process events to update UI
        # In a real app, this should be in a separate thread
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

        success = self.auth_service.login(email, password)
        
        if success:
            self.login_successful.emit()
            self.close()
        else:
            QMessageBox.critical(self, "Error", "Credenciales inválidas o error de conexión")
            self.login_btn.setEnabled(True)
            self.login_btn.setText("Iniciar Sesión")
