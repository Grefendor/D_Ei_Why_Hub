"""
Clock Widget Module.

This widget shows the time and date. It's big, bold, and updates every second.
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import QTimer, Qt, QTime, QDate
from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme

class ClockWidget(QWidget):
    """
    A simple clock widget for your dashboard.
    """
    def __init__(self, parent=None):
        """Sets up the clock and starts the timer."""
        super().__init__(parent)
        self.res_manager = ResolutionManager()
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_font_size = self.res_manager.scale(48)
        self.time_label.setStyleSheet(f"font-size: {time_font_size}px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_font_size = self.res_manager.scale(18)
        self.date_label.setStyleSheet(f"font-size: {date_font_size}px; color: {Theme.TEXT_SECONDARY};")

        self.layout.addWidget(self.time_label)
        self.layout.addWidget(self.date_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.update_time()

    def update_time(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        
        self.time_label.setText(current_time.toString("HH:mm"))
        self.date_label.setText(current_date.toString("dddd, d. MMMM yyyy"))

