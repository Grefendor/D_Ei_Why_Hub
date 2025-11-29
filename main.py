import sys
import os
from PySide6.QtWidgets import QApplication

# Ensure the project root is in the Python path for module resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.hub.ui import HubWindow

def main():
    """
    Starts up the whole application, sets up the main window, and gets the 
    event loop running.
    """
    app = QApplication(sys.argv)
    
    # Create and display the main hub window
    window = HubWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
