import sys
import os
import unittest
from PySide6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.app_registry import AppRegistry
from src.core.language_manager import LanguageManager

class TestAppRegistryI18n(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.app_registry = AppRegistry(os.path.join(self.root_dir, "apps"))
        self.language_manager = LanguageManager(self.root_dir)
        self.language_manager.load_language("en")

    def test_localized_app_names(self):
        """Test that get_app_list returns localized names."""
        # Test English
        self.language_manager.load_language("en")
        apps_en = self.app_registry.get_app_list(self.language_manager)
        
        # Check Home Assistant
        ha_en = next((a for a in apps_en if a["id"] == "home_assistant"), None)
        self.assertIsNotNone(ha_en)
        self.assertEqual(ha_en["name"], "Home Assistant")

        # Test German
        self.language_manager.load_language("de")
        apps_de = self.app_registry.get_app_list(self.language_manager)
        
        # Check Home Assistant
        ha_de = next((a for a in apps_de if a["id"] == "home_assistant"), None)
        self.assertIsNotNone(ha_de)
        self.assertEqual(ha_de["name"], "Home Assistant") # It's the same in DE for HA, let's check Calendar

        # Check Calendar
        cal_de = next((a for a in apps_de if a["id"] == "calendar"), None)
        self.assertIsNotNone(cal_de)
        self.assertEqual(cal_de["name"], "Kalender")

    def test_app_instantiation_with_language_manager(self):
        """Test that apps are instantiated with language_manager."""
        app_instance = self.app_registry.get_app_instance("home_assistant", self.language_manager)
        self.assertIsNotNone(app_instance)
        self.assertTrue(hasattr(app_instance, "language_manager"))
        self.assertEqual(app_instance.language_manager, self.language_manager)

if __name__ == "__main__":
    unittest.main()
