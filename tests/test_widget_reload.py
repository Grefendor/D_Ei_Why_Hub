import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.widget_registry import WidgetRegistry
from PySide6.QtWidgets import QApplication

"""
Widget Reload Test Script.

This script verifies that the WidgetRegistry correctly instantiates new widget
objects on subsequent requests, ensuring that widgets are not reused improperly.
"""

def test_widget_reinstantiation():
    """
    Tests that requesting a widget instance twice returns two different objects.
    """
    # Need app for widgets
    app = QApplication(sys.argv)
    
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    widgets_dir = os.path.join(root_dir, "widgets")
    
    registry = WidgetRegistry(widgets_dir)
    
    print("Getting first instance of clock...")
    w1 = registry.get_widget_instance("clock")
    print(f"w1: {w1}")
    
    print("Getting second instance of clock...")
    w2 = registry.get_widget_instance("clock")
    print(f"w2: {w2}")
    
    if w1 is w2:
        print("FAIL: Registry returned the same instance. This will cause crashes if the first instance was deleted.")
        sys.exit(1)
    else:
        print("PASS: Registry returned a new instance.")
        sys.exit(0)

if __name__ == "__main__":
    test_widget_reinstantiation()
