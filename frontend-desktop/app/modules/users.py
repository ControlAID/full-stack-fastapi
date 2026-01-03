from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QDialog, QFormLayout, QLineEdit, QComboBox, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from app.modules.base import ClientModule

class UserDialog(QDialog):
    def __init__(self, parent=None, user_data=None, units=None):
        super().__init__(parent)
        self.user_data = user_data
        self.units = units or []
        self.setWindowTitle("Add User" if not user_data else "Edit User")
        self.setFixedWidth(400)
        
        layout = QFormLayout(self)
        
        self.email_input = QLineEdit()
        self.name_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_input = QComboBox()
        self.role_input.addItems(["resident", "staff", "admin", "visitor"])
        
        self.unit_input = QComboBox()
        self.unit_input.addItem("None", None)
        for unit in self.units:
            # item data is unit_id
            self.unit_input.addItem(f"{unit.get('name')} ({unit.get('type')})", unit.get('id'))
        
        layout.addRow("Email:", self.email_input)
        layout.addRow("Full Name:", self.name_input)
        
        if not user_data:
            layout.addRow("Password:", self.password_input)
        else:
            # allow password update optionally
            self.password_input.setPlaceholderText("Leave empty to keep current")
            layout.addRow("New Password:", self.password_input)
            
        layout.addRow("Role:", self.role_input)
        layout.addRow("Unit/Location:", self.unit_input)
        
        self.is_primary_input = QCheckBox("Is Head of Household / Manager")
        layout.addRow("", self.is_primary_input)
        
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        layout.addRow(btn_box)
        
        if user_data:
            self.email_input.setText(user_data.get("email", ""))
            self.name_input.setText(user_data.get("full_name", ""))
            self.role_input.setCurrentText(user_data.get("role", "resident"))
            self.is_primary_input.setChecked(user_data.get("is_primary_unit_user", False))
            self.email_input.setReadOnly(True)

    def get_data(self):
        data = {
            "email": self.email_input.text(),
            "full_name": self.name_input.text(),
            "role": self.role_input.currentText(),
            "is_primary_unit_user": self.is_primary_input.isChecked()
        }
        if self.password_input.text():
            data["password"] = self.password_input.text()
            
        unit_id = self.unit_input.currentData()
        if unit_id:
            data["unit_id"] = unit_id
            
        return data

class UnitsManagerDialog(QDialog):
    def __init__(self, parent=None, auth_service=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.setWindowTitle("Manage Units / Locations")
        self.resize(700, 500)
        layout = QVBoxLayout(self)
        
        # Add Unit Form
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Unit Name (e.g. Apt 101, Parking A1)")
        self.type_input = QComboBox()
        self.type_input.addItems(["apartment", "office", "parking_spot", "common_area"])
        
        # Link to another unit (e.g. Parking -> Apt)
        self.link_input = QComboBox()
        self.link_input.addItem("No Link", None)
        
        add_btn = QPushButton("Add Unit")
        add_btn.clicked.connect(self.add_unit)
        
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.type_input)
        form_layout.addWidget(QLabel("Link to:"))
        form_layout.addWidget(self.link_input)
        form_layout.addWidget(add_btn)
        layout.addLayout(form_layout)
        
        # Units Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Name", "Type", "Linked To"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        self.load_units()

    def get_org_id(self):
        # Try to get org_id from cached user info or fetch me
        import requests
        from app.core.config import settings
        url = f"{settings.API_URL}/users/me"
        resp = requests.get(url, headers=self.auth_service.get_headers())
        if resp.status_code == 200:
            return resp.json().get("organization_id")
        return None

    def load_units(self):
        import requests
        from app.core.config import settings
        try:
            url = f"{settings.API_URL}/units/"
            resp = requests.get(url, headers=self.auth_service.get_headers())
            if resp.status_code == 200:
                units = resp.json()
                self.units_cache = units
                self.table.setRowCount(len(units))
                
                # Refresh link dropdown
                self.link_input.clear()
                self.link_input.addItem("No Link", None)
                
                unit_map = {u['id']: u['name'] for u in units}
                
                for i, u in enumerate(units):
                    self.table.setItem(i, 0, QTableWidgetItem(u.get("name")))
                    self.table.setItem(i, 1, QTableWidgetItem(u.get("type")))
                    
                    linked_id = u.get("related_unit_id")
                    linked_name = unit_map.get(linked_id, "-") if linked_id else "-"
                    self.table.setItem(i, 2, QTableWidgetItem(linked_name))
                    
                    # Populate dropdown (only show Apartments/Offices as link targets, not parking spots)
                    if u.get("type") in ["apartment", "office"]:
                        self.link_input.addItem(u.get("name"), u.get("id"))
                        
        except Exception as e:
            print(f"Error loading units: {e}")

    def add_unit(self):
        import requests
        from app.core.config import settings
        
        name = self.name_input.text()
        if not name: return
        
        org_id = self.get_org_id()
        if not org_id:
            QMessageBox.warning(self, "Error", "Could not determine Organization ID")
            return

        data = {
            "name": name,
            "type": self.type_input.currentText(),
            "organization_id": org_id
        }
        
        linked_id = self.link_input.currentData()
        if linked_id:
            data["related_unit_id"] = linked_id
        
        try:
            url = f"{settings.API_URL}/units/"
            resp = requests.post(url, json=data, headers=self.auth_service.get_headers())
            if resp.status_code == 200:
                self.name_input.clear()
                self.load_units()
            else:
                QMessageBox.warning(self, "Error", f"Failed: {resp.text}")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

class UsersModule(ClientModule):
    def get_name(self) -> str:
        return "users"
        
    def get_display_name(self) -> str:
        return "Users & Personnel"
    
    def get_icon(self):
        return "people" # Material icon
    
    def init_ui(self) -> QWidget:
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("User Management")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        units_btn = QPushButton("Manage Locations")
        units_btn.clicked.connect(self.open_units_manager)
        header_layout.addWidget(units_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        add_btn = QPushButton("Add User")
        add_btn.clicked.connect(self.add_user)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Email", "Role", "Unit", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.edit_user)
        layout.addWidget(self.table)
        
        return self.widget

    def on_load(self):
        self.load_data()
        
    def load_data(self):
        import requests
        from app.core.config import settings
        
        # Load Units first
        self.units_cache = []
        try:
            url_units = f"{settings.API_URL}/units/"
            headers = self.context.auth_service.get_headers()
            resp_units = requests.get(url_units, headers=headers)
            if resp_units.status_code == 200:
                self.units_cache = resp_units.json()
        except:
            pass # Fail silently or log
            
        # Load Users
        try:
            url = f"{settings.API_URL}/users/"
            headers = self.context.auth_service.get_headers()
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("data", [])
                
                self.table.setRowCount(len(users))
                self.users_cache_data = users
                
                for i, user in enumerate(users):
                    self.table.setItem(i, 0, QTableWidgetItem(user.get("full_name") or ""))
                    self.table.setItem(i, 1, QTableWidgetItem(user.get("email")))
                    self.table.setItem(i, 2, QTableWidgetItem(user.get("role", "N/A")))
                    self.table.setItem(i, 3, QTableWidgetItem(user.get("unit_name") or "-"))
                    status = "Active" if user.get("is_active") else "Inactive"
                    self.table.setItem(i, 4, QTableWidgetItem(status))
            else:
                print(f"Failed to load users: {response.status_code}")
                
        except Exception as e:
            print(f"Error loading users: {e}")

    def add_user(self):
        dialog = UserDialog(self.widget, units=self.units_cache)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self._create_user_api(data)
            
    def open_units_manager(self):
        dialog = UnitsManagerDialog(self.widget, auth_service=self.context.auth_service)
        dialog.exec()
        # Reload after closing to update cache
        self.load_data()

    def edit_user(self, index):
        pass

    def _create_user_api(self, data):
        import requests
        from app.core.config import settings
        
        try:
            url = f"{settings.API_URL}/users/"
            headers = self.context.auth_service.get_headers()
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                self.load_data()
            else:
                 QMessageBox.critical(self.widget, "Error", f"Failed to create user: {response.text}")
        except Exception as e:
            QMessageBox.critical(self.widget, "Error", f"Connection error: {e}")
