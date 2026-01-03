import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTabWidget, QDialog
from app.services.auth import AuthService
from app.ui.login import LoginWindow
from app.core.loader import ModuleLoader
from app.services.license import LicenseService
from app.ui.binding import BindingDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ControlAI - Monitoring Station")
        self.setMinimumSize(1024, 768)
        self.auth_service = AuthService()
        self.module_loader = ModuleLoader()
        
        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Header / Toolbar
        self.header_layout = QVBoxLayout()
        self.user_label = QLabel(f"Usuario: {self.get_user_email()}")
        self.logout_btn = QPushButton("Cerrar Sesión")
        self.logout_btn.setFixedSize(120, 30)
        self.logout_btn.clicked.connect(self.logout)
        
        self.layout.addWidget(self.user_label)
        self.layout.addWidget(self.logout_btn)
        
        # Module Tabs
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        # Load Modules
        self.load_modules()

    def get_user_email(self):
        # In a real app, decode JWT or get from user profile
        return "Admin" 

    def load_modules(self):
        # Clear existing tabs
        self.tabs.clear()
        
        # Load modules
        modules = self.module_loader.load_modules(context=self)
        
        if not modules:
            self.tabs.addTab(QLabel("No modules loaded"), "Info")
            return

        for module in modules:
            try:
                widget = module.init_ui()
                self.tabs.addTab(widget, module.get_display_name())
                module.on_load()
            except Exception as e:
                print(f"Error initializing module {module.get_name()}: {e}")

    def logout(self):
        self.auth_service.logout()
        self.close()
        # Restart app flow to show login
        global login_window
        login_window = LoginWindow()
        login_window.login_successful.connect(start_main_app)
        login_window.show()

def start_main_app():
    global main_window, login_window
    
    # 1. Initialize License Service
    auth_service = AuthService() # Re-instantiate to ensure token is loaded
    license_service = LicenseService(auth_service)
    
    # 2. Check Binding
    binding_status = license_service.check_binding()
    
    if not binding_status["bound"]:
        print(f"Binding check failed: {binding_status['message']}")
        
        # If authenticated but not bound, show Binding Dialog
        # (Assuming we have a valid token logic here, otherwise Auth would fail earlier)
        
        # We need a parent widget or run independent dialog??
        # Since we are outside main loop's window show(), we can run dialog exec
        
        dialog = BindingDialog(license_service)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Re-check or assume success
            pass
        else:
            # User cancelled binding
            print("User cancelled binding")
            # Maybe show login again or exit?
            # For now, let's close login if open and return
            if login_window: login_window.close()
            return

    # 3. Launch Main Window
    main_window = MainWindow()
    main_window.show()
    if login_window:
        login_window.close()

def main():
    app = QApplication(sys.argv)
    
    auth_service = AuthService()
    
    global login_window
    
    if auth_service.token:
        # Validate token / License first?
        start_main_app()
    else:
        login_window = LoginWindow()
        login_window.login_successful.connect(start_main_app)
        login_window.show()
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
