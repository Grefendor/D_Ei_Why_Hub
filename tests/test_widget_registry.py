import unittest
import os
import sys
import shutil
import tempfile

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.widget_registry import WidgetRegistry

class TestWidgetRegistry(unittest.TestCase):
    """
    Tests for the WidgetRegistry class.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.registry = WidgetRegistry(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_dummy_widget(self, name):
        with open(os.path.join(self.test_dir, f"{name}.py"), "w") as f:
            f.write(f"""
from PySide6.QtWidgets import QWidget
class {name.capitalize()}Widget(QWidget):
    pass
""")

    def test_discover_widgets(self):
        self.create_dummy_widget("clock")
        self.create_dummy_widget("weather")
        
        # Re-scan
        self.registry.scan_widgets()
        
        widgets = self.registry.get_widget_list()
        self.assertEqual(len(widgets), 2)
        
        widget_ids = [w["id"] for w in widgets]
        self.assertIn("clock", widget_ids)
        self.assertIn("weather", widget_ids)

if __name__ == "__main__":
    unittest.main()
