import unittest
import os
import sys
import json
import shutil
import tempfile

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.app_registry import AppRegistry

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

if __name__ == "__main__":
    unittest.main()
