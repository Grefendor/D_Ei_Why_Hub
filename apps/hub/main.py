"""
Hub Application Entry Point.

This module serves as the entry point for the Hub application when run as a standalone
package. It sets up the Python path to ensure imports work correctly and launches
the main Hub window.
"""

import sys
import os

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PySide6.QtWidgets import QApplication
from hub.ui import HubWindow

def main():
    """
    Initializes and runs the Hub application.
    """
    app = QApplication(sys.argv)
    
    # Optional: Set global stylesheet or font here
    
    window = HubWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
