import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                             QWidget, QPushButton, QTabWidget, QDialog, 
                             QHBoxLayout, QFrame, QStackedWidget, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from app.services.auth import AuthService
from app.ui.login import LoginWindow
from app.core.loader import ModuleLoader
from app.services.license import LicenseService
from app.ui.binding import BindingDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ControlAI - Monitoring Station")
        self.setMinimumSize(1200, 800)
        self.auth_service = AuthService()
        self.module_loader = ModuleLoader()
        
        # Central widget container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Main Layout (Horizontal: Drawer | Content)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 1. Drawer (Sidebar)
        self.create_drawer()
        
        # 2. Main Content Area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header (Top Bar)
        self.create_header()
        
        # Stacked Widget for Modules
        self.stacked_widget = QStackedWidget()
        self.content_layout.addWidget(self.stacked_widget)
        
        self.main_layout.addWidget(self.content_area)
        
        # Load Modules
        self.load_modules()

    def create_drawer(self):
        self.drawer = QFrame()
        self.drawer.setObjectName("drawer")
        self.drawer.setFixedWidth(250)
        self.drawer.setStyleSheet("""
            QFrame#drawer {
                background-color: #263238; /* Dark Blue-Grey / Material Dark */
                border-right: 1px solid #37474f;
            }
            QPushButton {
                text-align: left;
                padding: 15px;
                border: none;
                background-color: transparent;
                color: #eceff1;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #37474f;
            }
            QPushButton:checked {
                background-color: #00acc1; /* Teal accent */
                color: white;
                border-left: 4px solid white;
            }
            QLabel {
                color: white;
            }
        """)
        
        self.drawer_layout = QVBoxLayout(self.drawer)
        self.drawer_layout.setContentsMargins(0, 0, 0, 0)
        self.drawer_layout.setSpacing(5)
        
        # App Title / Logo Area
        title_box = QFrame()
        title_box.setFixedHeight(60)
        title_box.setStyleSheet("background-color: transparent; margin-top: 10px; margin-bottom: 10px;")
        
        tb_layout = QVBoxLayout(title_box)
        title_label = QLabel("ControlAI")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #eceff1;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tb_layout.addWidget(title_label)
        
        self.drawer_layout.addWidget(title_box)
        
        # Navigation Buttons Container
        self.nav_container = QVBoxLayout()
        self.nav_container.setSpacing(2)
        self.drawer_layout.addLayout(self.nav_container)
        
        self.drawer_layout.addStretch()
        
        # User Profile / Logout at bottom
        user_box = QFrame()
        user_box.setStyleSheet("border-top: 1px solid #37474f; padding: 10px;")
        ub_layout = QVBoxLayout(user_box)
        
        user_label = QLabel(f"{self.get_user_email()}")
        user_label.setStyleSheet("font-size: 12px; color: #b0bec5;")
        user_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ub_layout.addWidget(user_label)
        
        logout_btn = QPushButton(" Cerrar Sesión")
        # logout_btn.setIcon(QIcon("path/to/icon.png")) # TODO: Icons
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("""
            QPushButton { color: #ffab91; }
            QPushButton:hover { background-color: #3e2723; }
        """)
        ub_layout.addWidget(logout_btn)
        
        self.drawer_layout.addWidget(user_box)
        
        self.main_layout.addWidget(self.drawer)
        
        # Keep track of nav buttons to manage 'checked' state
        self.nav_buttons = []

    def create_header(self):
        # Optional: Top header bar for global search or notifications
        # For now, minimal.
        pass

    def get_user_email(self):
        return "Admin" 

    def load_modules(self):
        # Clear existing
        # (For simple reloading, we would need to remove widgets from stack and buttons from layout)
        
        modules = self.module_loader.load_modules(context=self)
        
        if not modules:
            return

        for i, module in enumerate(modules):
            try:
                # 1. Create Nav Button
                btn = QPushButton(f"  {module.get_display_name()}")
                btn.setCheckable(True)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                # Ensure closure captures current index 'i'
                btn.clicked.connect(lambda checked, idx=i: self.switch_module(idx))
                
                self.nav_container.addWidget(btn)
                self.nav_buttons.append(btn)
                
                # 2. Add Page to Stack
                widget = module.init_ui()
                self.stacked_widget.addWidget(widget)
                
                # Load logic
                module.on_load()
                
            except Exception as e:
                print(f"Error initializing module {module.get_name()}: {e}")
        
        # Select first module by default
        if self.nav_buttons:
            self.switch_module(0)

    def switch_module(self, index):
        # Update Stack
        self.stacked_widget.setCurrentIndex(index)
        
        # Update Buttons Styling
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)

    def logout(self):
        self.auth_service.logout()
        self.close()
        # Restart app flow to show login
        global login_window
        login_window = LoginWindow()
        
        # Apply Theme to Login too
        from qt_material import apply_stylesheet
        global app_instance # We need access to app
        if app_instance:
             apply_stylesheet(app_instance, theme='dark_teal.xml')

        login_window.login_successful.connect(start_main_app)
        login_window.show()

def start_main_app():
    global main_window, login_window
    
    # 1. Initialize License Service
    auth_service = AuthService() 
    license_service = LicenseService(auth_service)
    
    # 2. Check Binding
    binding_status = license_service.check_binding()
    
    if not binding_status["bound"]:
        dialog = BindingDialog(license_service)
        from qt_material import apply_stylesheet
        # Dialog needs theme too if created independently, but it might inherit if parent is app
        
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
    
    # NEW: 3. Check/Install Modules (Remote)
    # Only show if there are updates? For now always run to check.
    from app.ui.loader_dialog import LoaderDialog
    loader = LoaderDialog(auth_service)
    
    # Apply Theme to Loader
    if app_instance:
        from qt_material import apply_stylesheet
        apply_stylesheet(app_instance, theme='dark_teal.xml') # Ensure theme is active
        
    if loader.exec() == QDialog.DialogCode.Accepted:
        pass
    else:
        # User closed loader?
        pass

    # 4. Launch Main Window
    main_window = MainWindow()
    
    # Apply Theme
    from qt_material import apply_stylesheet
    if app_instance:
        apply_stylesheet(app_instance, theme='dark_teal.xml')
    
    main_window.show()
    if login_window:
        login_window.close()

# Global variables
login_window = None
main_window = None
app_instance = None

def main():
    global app_instance, login_window
    app_instance = QApplication(sys.argv)
    
    auth_service = AuthService()
    
    if auth_service.token:
        # Validate token / License first?
        start_main_app()
    else:
        login_window = LoginWindow()
        
        # Apply Theme to Login too
        from qt_material import apply_stylesheet
        apply_stylesheet(app_instance, theme='dark_teal.xml')
        
        login_window.login_successful.connect(start_main_app)
        login_window.show()
        
    sys.exit(app_instance.exec())

if __name__ == "__main__":
    main()
