"""
Verification script for Screensaver functionality.
"""
import sys
import os
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, Qt, QEvent, QPoint
from PySide6.QtGui import QMouseEvent

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.settings_manager import SettingsManager
from src.core.screensaver_manager import ScreensaverManager
from apps.hub.screensaver_ui import ScreensaverWindow

def verify_screensaver():
    app = QApplication(sys.argv)
    
    # Setup Settings
    settings_manager = SettingsManager("config")
    original_settings = settings_manager.get_screensaver_settings()
    
    # Test Settings
    test_settings = {
        "enabled": True,
        "timeout": 0.1, # 6 seconds (0.1 min)
        "slide_duration": 1,
        "image_path": "data/screensaver_images"
    }
    settings_manager.set_screensaver_settings(test_settings)
    
    print("Settings updated for test.")
    
    # Initialize Manager and Window
    manager = ScreensaverManager(settings_manager)
    window = ScreensaverWindow(settings_manager)
    
    manager.activate_screensaver.connect(window.start)
    manager.deactivate_screensaver.connect(window.stop)
    
    print("Waiting for screensaver activation (approx 6 seconds)...")
    
    def check_activation():
        if window.isVisible():
            print("SUCCESS: Screensaver activated!")
            
            # Simulate activity to deactivate
            print("Simulating activity...")
            # We need to simulate an event that the event filter catches
            # Since we can't easily inject into the global event loop for the filter 
            # without a real window interaction, we'll manually trigger the filter logic
            # or just rely on the fact that we are running a test script.
            
            # Let's try to post an event to the app
            event = QMouseEvent(QEvent.Type.MouseMove, QPoint(100, 100), Qt.MouseButton.NoButton, Qt.MouseButton.NoButton, Qt.KeyboardModifier.NoModifier)
            QApplication.sendEvent(window, event)
            
            QTimer.singleShot(1000, check_deactivation)
        else:
            print("Waiting...")
            QTimer.singleShot(1000, check_activation)

    def check_deactivation():
        if not window.isVisible():
            print("SUCCESS: Screensaver deactivated!")
            cleanup()
        else:
            print("FAILURE: Screensaver did not deactivate.")
            cleanup()

    def cleanup():
        # Restore settings
        settings_manager.set_screensaver_settings(original_settings)
        print("Settings restored.")
        app.quit()

    # Start checking after timeout period
    QTimer.singleShot(7000, check_activation)
    
    app.exec()

if __name__ == "__main__":
    verify_screensaver()
