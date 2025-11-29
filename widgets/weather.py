import json
import os
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QDialog, QLineEdit, QPushButton, QMessageBox, QFrame)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QCursor

from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme
from src.services.weather_service import WeatherService

"""
Weather Widget Module.

This widget shows the weather and forecast. It fetches data in the background 
so the app stays smooth.
"""

CONFIG_FILE = os.path.join("config", "weather_config.json")

class WeatherWorker(QThread):
    """
    A background worker to get weather data without freezing the app.
    """
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, service, lat, lon):
        """Sets up the worker."""
        super().__init__()
        self.service = service
        self.lat = lat
        self.lon = lon

    def run(self):
        """
        Goes and gets the weather data.
        """
        data = self.service.get_weather(self.lat, self.lon)
        if data:
            self.finished.emit(data)
        else:
            self.error.emit("Failed to fetch weather data")

class LocationDialog(QDialog):
    """
    A popup to type in your city.
    """
    def __init__(self, parent=None):
        """Sets up the dialog."""
        super().__init__(parent)
        self.setWindowTitle("Set Location")
        self.setModal(True)
        self.res_manager = ResolutionManager()
        
        layout = QVBoxLayout(self)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter city name (e.g. Berlin)")
        layout.addWidget(self.city_input)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.resize(300, 150)

    def get_city(self):
        """Gets what you typed."""
        return self.city_input.text().strip()

class WeatherWidget(QWidget):
    """
    Shows the current weather and a 3-day forecast.

    You can click it to change your location. It updates automatically.
    """
    def __init__(self, parent=None):
        """Sets up the widget and loads your saved location."""
        super().__init__(parent)
        self.res_manager = ResolutionManager()
        self.service = WeatherService()
        self.config = self.load_config()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.res_manager.scale(5))
        
        # Main Weather Display (Clickable)
        self.main_container = QWidget()
        self.main_container.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.main_container.mousePressEvent = self.open_location_dialog
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.temp_label = QLabel("--°C")
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_font_size = self.res_manager.scale(32)
        self.temp_label.setStyleSheet(f"font-size: {temp_font_size}px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        
        self.desc_label = QLabel("Set Location")
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_font_size = self.res_manager.scale(16)
        self.desc_label.setStyleSheet(f"font-size: {desc_font_size}px; color: {Theme.TEXT_SECONDARY};")
        
        self.main_layout.addWidget(self.temp_label)
        self.main_layout.addWidget(self.desc_label)
        
        self.layout.addWidget(self.main_container)
        
        # Forecast Display
        self.forecast_container = QWidget()
        self.forecast_layout = QHBoxLayout(self.forecast_container)
        self.forecast_layout.setContentsMargins(0, self.res_manager.scale(10), 0, 0)
        self.forecast_layout.setSpacing(self.res_manager.scale(15))
        
        self.layout.addWidget(self.forecast_container)
        
        # Timer for auto-refresh (every hour)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_weather)
        self.timer.start(3600 * 1000) 
        
        # Initial Load
        if self.config.get("lat") and self.config.get("lon"):
            self.refresh_weather()

    def load_config(self):
        """Reads your settings from a file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        """Saves your settings to a file."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def open_location_dialog(self, event):
        """
        Lets you change the city when you click the widget.
        """
        dialog = LocationDialog(self)
        if dialog.exec():
            city = dialog.get_city()
            if city:
                self.update_location(city)

    def update_location(self, city):
        """
        Finds the coordinates for your city and saves them.
        """
        self.desc_label.setText("Finding...")
        # Run in thread to avoid freeze
        # Note: For simplicity in this step, using a quick synchronous call for geocoding 
        # or we could make another worker. 
        # Given geocoding is fast, I'll do it here but ideally should be threaded too.
        # Let's use a worker for consistency if I can, but I need to define it.
        # For now, I'll just call service directly as it's a one-time action initiated by user.
        
        try:
            result = self.service.get_coordinates(city)
            if result:
                lat, lon, name = result
                self.config = {"lat": lat, "lon": lon, "city": name}
                self.save_config()
                self.refresh_weather()
            else:
                QMessageBox.warning(self, "Error", "City not found.")
                self.desc_label.setText("City not found")
        except Exception as e:
            print(f"Error updating location: {e}")
            self.desc_label.setText("Error")

    def refresh_weather(self):
        """
        Starts the background worker to get fresh data.
        """
        lat = self.config.get("lat")
        lon = self.config.get("lon")
        if not lat or not lon:
            return

        self.worker = WeatherWorker(self.service, lat, lon)
        self.worker.finished.connect(self.update_ui)
        self.worker.error.connect(self.handle_error)
        self.worker.start()

    def update_ui(self, data):
        """
        Updates the labels and icons with the new weather info.

        Args:
            data (dict): The weather data we just got.
        """
        # Current Weather
        current = data["current"]
        self.temp_label.setText(f"{current['temp']}°C {current['icon']}")
        self.desc_label.setText(f"{self.config.get('city', 'Unknown')}: {current['desc']}")
        
        # Forecast
        # Clear previous forecast
        for i in reversed(range(self.forecast_layout.count())): 
            self.forecast_layout.itemAt(i).widget().setParent(None)
            
        daily = data.get("daily", [])
        for day in daily:
            day_widget = QFrame()
            day_layout = QVBoxLayout(day_widget)
            day_layout.setContentsMargins(0, 0, 0, 0)
            day_layout.setSpacing(2)
            day_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            day_label = QLabel(day["day"])
            day_label.setStyleSheet(f"font-size: {self.res_manager.scale(12)}px; color: {Theme.TEXT_SECONDARY}; font-weight: bold;")
            day_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            icon_label = QLabel(day["icon"])
            icon_label.setStyleSheet(f"font-size: {self.res_manager.scale(18)}px;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            temp_label = QLabel(f"{day['max_temp']}°/{day['min_temp']}°")
            temp_label.setStyleSheet(f"font-size: {self.res_manager.scale(10)}px; color: {Theme.TEXT_PRIMARY};")
            temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            day_layout.addWidget(day_label)
            day_layout.addWidget(icon_label)
            day_layout.addWidget(temp_label)
            
            self.forecast_layout.addWidget(day_widget)

    def handle_error(self, error_msg):
        """
        Shows an error message if something goes wrong.
        """
        print(f"Weather Error: {error_msg}")
        self.desc_label.setText("Update Failed")
