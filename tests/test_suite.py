import unittest
import os
import sys
import json
import shutil
import tempfile
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.app_registry import AppRegistry
from src.core.widget_registry import WidgetRegistry
from src.core.settings_manager import SettingsManager

"""
Core Test Suite.

This module contains unit tests for the core components of the application,
including the AppRegistry, WidgetRegistry, and SettingsManager.
"""

class TestAppRegistry(unittest.TestCase):
    """
    Tests for the AppRegistry class.
    """
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.registry = AppRegistry(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def create_dummy_app(self, app_id, name, entry_point_content="class App: pass"):
        app_dir = os.path.join(self.test_dir, app_id)
        os.makedirs(app_dir)
        
        manifest = {
            "name": name,
            "id": app_id,
            "entry_point": "app.py:App"
        }
        
        with open(os.path.join(app_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f)
            
        with open(os.path.join(app_dir, "app.py"), "w") as f:
            f.write(entry_point_content)
            
    def test_discover_apps(self):
        self.create_dummy_app("app1", "App One")
        self.create_dummy_app("app2", "App Two")
        
        # Re-scan
        self.registry.scan_apps()
        
        apps = self.registry.get_app_list()
        print(f"Discovered apps: {apps}")
        self.assertEqual(len(apps), 2)
        
        app_ids = [app["id"] for app in apps]
        self.assertIn("app1", app_ids)
        self.assertIn("app2", app_ids)

    def test_invalid_manifest(self):
        app_dir = os.path.join(self.test_dir, "bad_app")
        os.makedirs(app_dir)
        with open(os.path.join(app_dir, "manifest.json"), "w") as f:
            f.write("{invalid_json")
            
        self.registry.scan_apps()
        apps = self.registry.get_app_list()
        self.assertEqual(len(apps), 0)

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
        print(f"Discovered widgets: {widgets}")
        self.assertEqual(len(widgets), 2)
        
        widget_ids = [w["id"] for w in widgets]
        self.assertIn("clock", widget_ids)
        self.assertIn("weather", widget_ids)

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
