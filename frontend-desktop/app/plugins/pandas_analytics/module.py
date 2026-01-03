from app.modules.base import ClientModule
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt

class PandasAnalyticsUI(ClientModule):
    def get_name(self) -> str:
        return "pandas_analytics"
        
    def get_display_name(self) -> str:
        return "Data Analytics"

    def get_icon(self):
        # Return none or a standard icon name
        return "analytics" # Material icon name or path
    
    def init_ui(self) -> QWidget:
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        
        label = QLabel("Generated Data Frame using Pandas")
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(label)
        
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        return self.widget

    def on_load(self):
        try:
            import pandas as pd
            
            # Create a simple DataFrame
            data = {
                'Name': ['Alice', 'Bob', 'Charlie', 'David'],
                'Age': [25, 30, 35, 40],
                'City': ['New York', 'Los Angeles', 'Chicago', 'Houston'],
                'Score': [85, 90, 88, 92]
            }
            df = pd.DataFrame(data)
            
            # Display in Table
            self.table.setRowCount(df.shape[0])
            self.table.setColumnCount(df.shape[1])
            self.table.setHorizontalHeaderLabels(df.columns)
            
            for i in range(df.shape[0]):
                for j in range(df.shape[1]):
                    self.table.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
                    
            self.table.horizontalHeader().setStretchLastSection(True)
            
        except ImportError:
            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setItem(0,0, QTableWidgetItem("Error: Pandas not installed!"))
