from app.modules.base import ClientModule
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QProgressBar, QFrame, QGridLayout)
from PyQt6.QtCore import QTimer, Qt
import psutil

class DashboardModule(ClientModule):
    def get_name(self) -> str:
        return "system_dashboard"

    def get_display_name(self) -> str:
        return "Dashboard"

    def get_icon(self) -> str:
        return "speed"  # Placeholder for icon name

    def init_ui(self) -> QWidget:
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        
        # Title
        title = QLabel("Monitor de Sistema")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        # Grid for Stats Cards
        grid = QGridLayout()
        layout.addLayout(grid)

        # CPU Card
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk { background-color: #007bff; border-radius: 5px; }
        """)
        grid.addWidget(self.create_card("Procesador", self.cpu_label, self.cpu_bar), 0, 0)

        # RAM Card
        self.ram_label = QLabel("RAM: 0/0 GB")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk { background-color: #28a745; border-radius: 5px; }
        """)
        grid.addWidget(self.create_card("Memoria RAM", self.ram_label, self.ram_bar), 0, 1)

        # Disk Card
        self.disk_label = QLabel("Disco: 0/0 GB")
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        self.disk_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk { background-color: #ffc107; border-radius: 5px; }
        """)
        grid.addWidget(self.create_card("Almacenamiento", self.disk_label, self.disk_bar), 1, 0, 1, 2)
        
        layout.addStretch()

        # Timer for updates
        self.timer = QTimer(self.widget)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000) # Update every 2 seconds
        
        # Initial update
        self.update_stats()

        return self.widget

    def create_card(self, title_text, label, progress_bar):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame { 
                background-color: white; 
                border-radius: 10px; 
                border: 1px solid #e0e0e0;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #555; border: none;")
        layout.addWidget(title)
        
        label.setStyleSheet("font-size: 14px; color: #666; margin-bottom: 5px; border: none;")
        layout.addWidget(label)
        layout.addWidget(progress_bar)
        
        return frame

    def on_unload(self):
        if hasattr(self, 'timer'):
            self.timer.stop()

    def update_stats(self):
        try:
            # CPU
            cpu = psutil.cpu_percent()
            self.cpu_label.setText(f"Uso: {cpu}%")
            self.cpu_bar.setValue(int(cpu))

            # RAM
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024**3)
            used_gb = mem.used / (1024**3)
            self.ram_label.setText(f"Uso: {used_gb:.1f} GB de {total_gb:.1f} GB ({mem.percent}%)")
            self.ram_bar.setValue(int(mem.percent))

            # Disk
            disk = psutil.disk_usage('/')
            total_disk_gb = disk.total / (1024**3)
            used_disk_gb = disk.used / (1024**3)
            self.disk_label.setText(f"Uso: {used_disk_gb:.1f} GB de {total_disk_gb:.1f} GB ({disk.percent}%)")
            self.disk_bar.setValue(int(disk.percent))
        except Exception as e:
            print(f"Error updating stats: {e}")
