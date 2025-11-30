"""
Screensaver Manager Module.

Handles inactivity detection and screensaver state management.
"""

from PySide6.QtCore import QObject, QTimer, Signal, QEvent
from PySide6.QtWidgets import QApplication

class ScreensaverManager(QObject):
    """
    Manages the screensaver state based on user inactivity.
    """
    activate_screensaver = Signal()
    deactivate_screensaver = Signal()

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.on_timeout)
        
        # Install event filter on the application to detect activity
        QApplication.instance().installEventFilter(self)
        
        self.is_active = False
        self.load_settings()

    def load_settings(self):
        """Loads settings and starts/stops the timer."""
        settings = self.settings_manager.get_screensaver_settings()
        enabled = settings.get("enabled", False)
        timeout_minutes = settings.get("timeout", 5)
        
        if enabled:
            # Convert minutes to milliseconds
            timeout_ms = timeout_minutes * 60 * 1000
            self.timer.start(timeout_ms)
        else:
            self.timer.stop()

    def eventFilter(self, obj, event):
        """
        Monitors global application events to detect user activity.
        We care about mouse moves, clicks, key presses, and touch events.
        """
        if event.type() in [QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress, 
                            QEvent.Type.KeyPress, QEvent.Type.TouchBegin]:
            self.reset_timer()
            
            # If the screensaver is currently running, any activity should kill it immediately.
            if self.is_active:
                self.deactivate()
                
        return super().eventFilter(obj, event)

    def reset_timer(self):
        """Resets the inactivity timer, effectively postponing the screensaver."""
        if self.timer.isActive():
            self.timer.start() # Restarts with the same interval

    def on_timeout(self):
        """Timer finished, which means the user has been idle for too long."""
        if not self.is_active:
            self.activate()

    def activate(self):
        """Triggers the screensaver activation signal."""
        self.is_active = True
        self.activate_screensaver.emit()

    def deactivate(self):
        """Stops the screensaver and resets the tracking timer."""
        self.is_active = False
        self.deactivate_screensaver.emit()
        self.reset_timer()
