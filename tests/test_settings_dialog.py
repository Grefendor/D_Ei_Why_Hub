import sys
import os
import unittest
from PySide6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apps.hub.settings_dialog import SettingsDialog
from src.core.settings_manager import SettingsManager
from src.core.app_registry import AppRegistry
from src.core.widget_registry import WidgetRegistry
from src.core.language_manager import LanguageManager

class TestSettingsDialog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance if it doesn't exist
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.settings_manager = SettingsManager(self.root_dir)
        self.app_registry = AppRegistry(os.path.join(self.root_dir, "apps"))
        self.widget_registry = WidgetRegistry(os.path.join(self.root_dir, "widgets"))
        self.language_manager = LanguageManager(self.root_dir)
        self.language_manager.load_language("en")

    def test_dialog_initialization(self):
        """Test that SettingsDialog initializes without error."""
        try:
            dialog = SettingsDialog(
                self.settings_manager, 
                self.app_registry, 
                self.widget_registry, 
                self.language_manager
            )
            self.assertIsNotNone(dialog)
        except AttributeError as e:
            self.fail(f"SettingsDialog initialization failed with AttributeError: {e}")
        except Exception as e:
            self.fail(f"SettingsDialog initialization failed with Exception: {e}")

if __name__ == "__main__":
    unittest.main()
