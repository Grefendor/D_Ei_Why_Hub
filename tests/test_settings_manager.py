import unittest
import os
import sys
import shutil
import tempfile

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.settings_manager import SettingsManager

class TestSettingsManager(unittest.TestCase):
    """
    Tests for the SettingsManager class.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.manager = SettingsManager(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_defaults(self):
        self.assertEqual(self.manager.get_enabled_apps(), [])
        self.assertEqual(self.manager.get_app_positions(), {})

    def test_save_load_app_positions(self):
        positions = {"app1": {"row": 1, "col": 1}}
        self.manager.set_app_positions(positions)
        
        # Reload
        new_manager = SettingsManager(self.test_dir)
        self.assertEqual(new_manager.get_app_positions(), positions)

    def test_save_load_widget_positions(self):
        positions = {0: "clock", 2: "weather"}
        self.manager.set_widget_positions(positions)
        
        # Reload
        new_manager = SettingsManager(self.test_dir)
        # JSON keys become strings when saved, but our getter converts them back to int
        self.assertEqual(new_manager.get_widget_positions(), positions)

if __name__ == "__main__":
    unittest.main()
