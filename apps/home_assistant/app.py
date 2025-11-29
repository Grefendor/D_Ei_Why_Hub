import sys
import os
import json
"""
Home Assistant Application Module.

Provides a dashboard interface for controlling Home Assistant entities 
(lights, switches, etc.) via the REST API.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QDialog, QFormLayout, QMessageBox, QScrollArea,
    QGridLayout, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QColor, QPalette

from .api import HomeAssistantAPI

# --- Theme Constants ---
HA_BLUE = "#03a9f4"
HA_BG = "#1c1c1c"
CARD_BG = "#2c2c2c"
TEXT_COLOR = "#ffffff"

class SettingsDialog(QDialog):
    def __init__(self, parent=None, url="", token="", demo_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Home Assistant Settings")
        self.setMinimumWidth(400)
        self.setStyleSheet(f"""
            QDialog {{ background-color: {HA_BG}; color: {TEXT_COLOR}; }}
            QLabel {{ color: {TEXT_COLOR}; }}
            QLineEdit {{ 
                padding: 8px; 
                border-radius: 4px; 
                border: 1px solid #444;
                background-color: #333;
                color: {TEXT_COLOR};
            }}
            QCheckBox {{ color: {TEXT_COLOR}; }}
            QPushButton {{
                padding: 8px 16px;
                background-color: {HA_BLUE};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #0288d1; }}
        """)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.demo_checkbox = QCheckBox("Enable Demo Mode")
        self.demo_checkbox.setChecked(demo_mode)
        self.demo_checkbox.toggled.connect(self.toggle_inputs)
        
        self.url_input = QLineEdit(url)
        self.url_input.setPlaceholderText("http://homeassistant.local:8123")
        self.token_input = QLineEdit(token)
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        form.addRow("", self.demo_checkbox)
        form.addRow("HA URL:", self.url_input)
        form.addRow("Access Token:", self.token_input)
        
        layout.addLayout(form)
        
        self.toggle_inputs(demo_mode)
        
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def toggle_inputs(self, checked):
        self.url_input.setEnabled(not checked)
        self.token_input.setEnabled(not checked)

    def get_data(self):
        return self.url_input.text(), self.token_input.text(), self.demo_checkbox.isChecked()

class EntityTile(QFrame):
    def __init__(self, entity, api):
        super().__init__()
        self.entity = entity
        self.api = api
        self.entity_id = entity["entity_id"]
        self.state = entity["state"]
        self.attributes = entity.get("attributes", {})
        
        self.setFixedSize(160, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setup_ui()
        self.update_style()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Icon (Placeholder for now, could use MDI icons if available)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 24px;")
        
        # Name
        name = self.attributes.get("friendly_name", self.entity_id)
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        # State
        self.state_label = QLabel(self.state)
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.state_label)

    def update_style(self):
        domain = self.entity_id.split(".")[0]
        is_on = self.state == "on"
        
        bg_color = CARD_BG
        if is_on and domain in ["light", "switch"]:
            bg_color = "#fdd835" if domain == "light" else HA_BLUE
            text_col = "#000000"
        else:
            text_col = TEXT_COLOR

        self.setStyleSheet(f"""
            EntityTile {{
                background-color: {bg_color};
                border-radius: 10px;
            }}
            QLabel {{ color: {text_col}; }}
        """)
        
        # Set Icon based on domain
        icon_map = {
            "light": "💡",
            "switch": "🔌",
            "sensor": "🌡️",
            "binary_sensor": "👁️",
            "person": "👤",
            "sun": "☀️"
        }
        self.icon_label.setText(icon_map.get(domain, "❓"))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_entity()

    def toggle_entity(self):
        domain = self.entity_id.split(".")[0]
        if domain in ["light", "switch", "input_boolean"]:
            service = "turn_off" if self.state == "on" else "turn_on"
            self.api.call_service(domain, service, {"entity_id": self.entity_id})
            # Optimistic update
            self.state = "off" if self.state == "on" else "on"
            self.state_label.setText(self.state)
            self.update_style()

class HomeAssistantApp(QMainWindow):
    def __init__(self, language_manager=None):
        super().__init__()
        self.language_manager = language_manager
        self.setWindowTitle("Home Assistant")
        if self.language_manager:
            self.setWindowTitle(self.language_manager.translate("home_assistant", "Home Assistant"))
            
        self.setStyleSheet(f"background-color: {HA_BG}; color: {TEXT_COLOR};")
        
        self.settings_file = os.path.join(os.path.dirname(__file__), "settings.json")
        self.api = None
        self.entities = []
        
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QHBoxLayout()
        title_text = "Home Assistant"
        if self.language_manager:
            title_text = self.language_manager.translate("home_assistant", "Home Assistant")
        title = QLabel(title_text)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(40, 40)
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {CARD_BG};
                border-radius: 20px;
                font-size: 20px;
            }}
            QPushButton:hover {{ background-color: #444; }}
        """)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet(settings_btn.styleSheet())
        
        header.addWidget(title)
        header.addStretch()
        header.addWidget(refresh_btn)
        header.addWidget(settings_btn)
        layout.addLayout(header)
        
        # Content Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background-color: transparent;")
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(15)
        
        self.scroll_area.setWidget(self.content_widget)
        layout.addWidget(self.scroll_area)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    config = json.load(f)
                    url = config.get("url", "")
                    token = config.get("token", "")
                    demo_mode = config.get("demo_mode", False)
                    
                    if (url and token) or demo_mode:
                        self.api = HomeAssistantAPI(url, token, demo_mode)
                        self.refresh_data()
                    else:
                        self.open_settings()
            except Exception as e:
                print(f"Error loading settings: {e}")
                self.open_settings()
        else:
            self.open_settings()

    def save_settings(self, url, token, demo_mode):
        config = {"url": url, "token": token, "demo_mode": demo_mode}
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(config, f)
            
            self.api = HomeAssistantAPI(url, token, demo_mode)
            self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save settings: {e}")

    def open_settings(self):
        url = ""
        token = ""
        demo_mode = False
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    config = json.load(f)
                    url = config.get("url", "")
                    token = config.get("token", "")
                    demo_mode = config.get("demo_mode", False)
            except:
                pass
                
        dialog = SettingsDialog(self, url, token, demo_mode)
        if dialog.exec():
            new_url, new_token, new_demo_mode = dialog.get_data()
            self.save_settings(new_url, new_token, new_demo_mode)

    def refresh_data(self):
        if not self.api:
            return
            
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Fetch states
        states = self.api.get_states()
        if not states:
            # Check connection if states are empty (could be auth error)
            if not self.api.check_connection():
                QMessageBox.warning(self, "Connection Error", "Could not connect to Home Assistant. Check URL and Token.")
                return

        # Filter and Sort
        # For now, let's just show lights, switches, and sensors to avoid clutter
        allowed_domains = ["light", "switch", "sensor", "binary_sensor", "person", "sun"]
        filtered_states = [
            s for s in states 
            if s["entity_id"].split(".")[0] in allowed_domains
        ]
        
        # Sort by domain then name
        filtered_states.sort(key=lambda x: (x["entity_id"].split(".")[0], x["entity_id"]))
        
        row = 0
        col = 0
        max_cols = 4 # Adjust based on window size?
        
        for entity in filtered_states:
            tile = EntityTile(entity, self.api)
            self.grid_layout.addWidget(tile, row, col)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
