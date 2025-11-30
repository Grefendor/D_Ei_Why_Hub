import json
import os
from PySide6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QDialog, QSpinBox, QFrame)
from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtGui import QAction

from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme

"""
Timer Widget Module.

This widget provides three independent countdown timers, allowing users to track multiple
durations simultaneously. It is designed for quick interactions, such as cooking timers
or productivity sprints, directly from the Hub's top bar.
"""

class TimeSetDialog(QDialog):
    """
    A modal dialog for configuring the duration of a timer.
    
    Allows the user to specify hours, minutes, and seconds using spin boxes.
    """
    def __init__(self, language_manager, parent=None):
        """
        Initialize the time setting dialog.

        Args:
            language_manager: The manager instance for handling translations.
            parent: The parent widget.
        """
        super().__init__(parent)
        self.language_manager = language_manager
        self.setWindowTitle(self.language_manager.translate("set_timer"))
        self.setModal(True)
        self.res_manager = ResolutionManager()
        
        layout = QVBoxLayout(self)
        
        # Time Inputs
        time_layout = QHBoxLayout()
        
        self.hours = QSpinBox()
        self.hours.setRange(0, 99)
        self.hours.setSuffix(f" {self.language_manager.translate('hours')}")
        
        self.minutes = QSpinBox()
        self.minutes.setRange(0, 59)
        self.minutes.setSuffix(f" {self.language_manager.translate('minutes')}")
        
        self.seconds = QSpinBox()
        self.seconds.setRange(0, 59)
        self.seconds.setSuffix(f" {self.language_manager.translate('seconds')}")
        
        # Apply scaling and styling to inputs
        for spin in [self.hours, self.minutes, self.seconds]:
            spin.setFixedSize(self.res_manager.scale(80), self.res_manager.scale(40))
            spin.setStyleSheet(f"font-size: {self.res_manager.scale(16)}px;")
            time_layout.addWidget(spin)
            
        layout.addLayout(time_layout)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton(self.language_manager.translate("start"))
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton(self.language_manager.translate("cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def get_seconds(self):
        """
        Calculate the total duration in seconds from the input fields.

        Returns:
            int: Total seconds.
        """
        return (self.hours.value() * 3600) + (self.minutes.value() * 60) + self.seconds.value()

class SingleTimer(QFrame):
    """
    Represents a single, independent timer unit.
    
    Handles the countdown logic, display updates, and user interaction states 
    (running, paused, finished).
    """
    def __init__(self, index, res_manager, language_manager):
        """
        Initialize a single timer instance.

        Args:
            index: The identifier for this timer slot.
            res_manager: Resolution manager for UI scaling.
            language_manager: Language manager for translations.
        """
        super().__init__()
        self.index = index
        self.res_manager = res_manager
        self.language_manager = language_manager
        self.remaining_seconds = 0
        self.is_running = False
        self.is_alarm = False
        self.alarm_state = False # Toggle state for flashing effect
        
        # Timer for the countdown tick
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.setInterval(1000)

        # Timer for the alarm flashing effect
        self.alarm_timer = QTimer(self)
        self.alarm_timer.timeout.connect(self.flash_alarm)
        self.alarm_timer.setInterval(500) # Flash every 500ms
        
        self.setup_ui()
        
    def setup_ui(self):
        """Constructs the UI elements for the timer."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # Time Display
        self.time_label = QLabel("00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"font-size: {self.res_manager.scale(20)}px; font-weight: bold; color: {Theme.TEXT_PRIMARY};")
        layout.addWidget(self.time_label)
        
        # Control Buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(5)
        
        # Primary Action Button (Set/Start/Stop)
        self.action_btn = QPushButton(self.language_manager.translate("set_timer").split(" ")[0]) # Use short text like "Set"
        self.action_btn.setFixedSize(self.res_manager.scale(50), self.res_manager.scale(25))
        self.action_btn.setStyleSheet(Theme.get_button_style(font_size=self.res_manager.scale(12)))
        self.action_btn.clicked.connect(self.on_action_click)
        controls_layout.addWidget(self.action_btn)
        
        # Reset Button
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setFixedSize(self.res_manager.scale(25), self.res_manager.scale(25))
        self.reset_btn.setStyleSheet(Theme.get_button_style(font_size=self.res_manager.scale(12)))
        self.reset_btn.clicked.connect(self.reset_timer)
        controls_layout.addWidget(self.reset_btn)
        
        layout.addLayout(controls_layout)
        
        # Default styling
        self.setStyleSheet(f"""
            SingleTimer {{
                background-color: {Theme.GLASS_COLOR};
                border-radius: {self.res_manager.scale(8)}px;
                border: {Theme.GLASS_BORDER};
            }}
        """)
        
        # Update button text to match language
        self.reset_timer()

    def on_action_click(self):
        """Handles clicks on the primary action button based on current state."""
        if self.is_alarm:
            # State: Alarm -> Stop Alarm (Reset)
            self.reset_timer()
        elif self.remaining_seconds == 0:
            # State: Idle -> Open Set Dialog
            dialog = TimeSetDialog(self.language_manager, self)
            if dialog.exec():
                seconds = dialog.get_seconds()
                if seconds > 0:
                    self.remaining_seconds = seconds
                    self.update_display()
                    self.start_timer()
        elif self.is_running:
            # State: Running -> Pause
            self.pause_timer()
        else:
            # State: Paused -> Resume
            self.start_timer()

    def start_timer(self):
        """Starts or resumes the countdown."""
        self.is_running = True
        self.timer.start()
        self.action_btn.setText(self.language_manager.translate("stop"))
        self.setStyleSheet(f"""
            SingleTimer {{
                background-color: {Theme.GLASS_COLOR};
                border-radius: {self.res_manager.scale(8)}px;
                border: 1px solid {Theme.ACCENT_COLOR};
            }}
        """)

    def pause_timer(self):
        """Pauses the countdown."""
        self.is_running = False
        self.timer.stop()
        self.action_btn.setText(self.language_manager.translate("start"))
        self.setStyleSheet(f"""
            SingleTimer {{
                background-color: {Theme.GLASS_COLOR};
                border-radius: {self.res_manager.scale(8)}px;
                border: 1px solid #f39c12;
            }}
        """)

    def reset_timer(self):
        """Resets the timer to zero and idle state."""
        self.is_running = False
        self.is_alarm = False
        self.timer.stop()
        self.alarm_timer.stop() # Stop flashing
        self.remaining_seconds = 0
        self.update_display()
        # "Set" might be too long in some languages, maybe use icon or short word?
        # For now using the first word of "Set Timer" or fallback
        set_text = self.language_manager.translate("set_timer").split(" ")[0]
        self.action_btn.setText(set_text)
        
        self.setStyleSheet(f"""
            SingleTimer {{
                background-color: {Theme.GLASS_COLOR};
                border-radius: {self.res_manager.scale(8)}px;
                border: {Theme.GLASS_BORDER};
            }}
        """)

    def tick(self):
        """Called every second to decrement the timer."""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_display()
            if self.remaining_seconds == 0:
                self.trigger_alarm()

    def update_display(self):
        """Updates the time label with formatted HH:MM:SS."""
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        
        if hours > 0:
            self.time_label.setText(f"{hours}:{minutes:02}:{seconds:02}")
        else:
            self.time_label.setText(f"{minutes:02}:{seconds:02}")

    def trigger_alarm(self):
        """Handles the timer completion event (visual alarm)."""
        self.is_running = False
        self.is_alarm = True
        self.timer.stop()
        self.action_btn.setText(self.language_manager.translate("ok"))
        self.alarm_timer.start() # Start flashing

    def flash_alarm(self):
        """Toggles the background color for the alarm effect."""
        self.alarm_state = not self.alarm_state
        if self.alarm_state:
            self.setStyleSheet(f"""
                SingleTimer {{
                    background-color: #e74c3c;
                    border-radius: {self.res_manager.scale(8)}px;
                    border: 2px solid #FFFFFF;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                SingleTimer {{
                    background-color: {Theme.GLASS_COLOR};
                    border-radius: {self.res_manager.scale(8)}px;
                    border: 2px solid #e74c3c;
                }}
            """)

class TimerWidget(QWidget):
    """
    The main container widget holding three independent timer slots.
    """
    def __init__(self, language_manager=None, res_manager=None, parent=None):
        """
        Initialize the Timer Widget.

        Args:
            language_manager: Manager for translations.
            res_manager: Manager for UI scaling.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.language_manager = language_manager
        self.res_manager = res_manager if res_manager else ResolutionManager()
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.res_manager.scale(10))
        
        # Instantiate 3 independent timer slots
        for i in range(3):
            timer = SingleTimer(i, self.res_manager, self.language_manager)
            self.layout.addWidget(timer)
