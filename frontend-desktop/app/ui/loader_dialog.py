from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from app.core.module_manager import ModuleManager

class InstallWorker(QThread):
    progress = pyqtSignal(str) # Status message
    finished = pyqtSignal(bool) # Success
    
    def __init__(self, manager: ModuleManager, modules_to_install: list):
        super().__init__()
        self.manager = manager
        self.modules_to_install = modules_to_install
        
    def run(self):
        self.progress.emit("Checking modules...")
        
        # In a real app, we would fetch the list of licensed modules from the API first
        # For this demo, we force install specific modules if not present
        
        current_plugins = [p.name for p in self.manager.plugins_dir.iterdir() if p.is_dir()]
        
        for mod in self.modules_to_install:
            if mod not in current_plugins:
                self.progress.emit(f"Downloading {mod}...")
                success = self.manager.install_module(mod)
                if not success:
                    self.progress.emit(f"Failed to install {mod}")
                else:
                    self.progress.emit(f"Installed {mod}")
            else:
                 self.progress.emit(f"{mod} is up to date.")
                 
        self.progress.emit("Loading application...")
        self.finished.emit(True)

class LoaderDialog(QDialog):
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.setWindowTitle("ControlAI - Updating")
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.WindowType.SplashScreen) # No border, splash style
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel("Checking for updates...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        self.pbar = QProgressBar()
        self.pbar.setRange(0, 0) # Indeterminate
        layout.addWidget(self.pbar)
        
        # Start Worker
        from app.core.module_manager import ModuleManager
        self.manager = ModuleManager(auth_service)
        
        # DEMO: Force install pandas_analytics
        modules_to_demo = ["pandas_analytics"]
        
        self.worker = InstallWorker(self.manager, modules_to_demo)
        self.worker.progress.connect(self.update_status)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()
        
    def update_status(self, text):
        self.status_label.setText(text)
        
    def on_finished(self, success):
        self.accept()
