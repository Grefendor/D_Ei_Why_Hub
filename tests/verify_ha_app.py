import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.home_assistant.api import HomeAssistantAPI
from apps.home_assistant.app import HomeAssistantApp
from PySide6.QtWidgets import QApplication

class TestHomeAssistantApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create QApplication instance for UI tests
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def test_api_init(self):
        api = HomeAssistantAPI("http://localhost:8123", "token")
        self.assertEqual(api.url, "http://localhost:8123")
        self.assertEqual(api.headers["Authorization"], "Bearer token")

    @patch('requests.get')
    def test_api_check_connection_success(self, mock_get):
        mock_get.return_value.status_code = 200
        api = HomeAssistantAPI("http://localhost:8123", "token")
        self.assertTrue(api.check_connection())

    @patch('requests.get')
    def test_api_check_connection_failure(self, mock_get):
        mock_get.return_value.status_code = 401
        api = HomeAssistantAPI("http://localhost:8123", "token")
        self.assertFalse(api.check_connection())

    def test_app_instantiation(self):
        # Test that the app class can be instantiated without crashing
        try:
            app = HomeAssistantApp()
            self.assertIsNotNone(app)
        except Exception as e:
            self.fail(f"HomeAssistantApp instantiation failed: {e}")

    def test_demo_mode(self):
        api = HomeAssistantAPI("http://localhost:8123", "token", demo_mode=True)
        self.assertTrue(api.check_connection())
        states = api.get_states()
        self.assertTrue(len(states) > 0)
        self.assertEqual(states[0]["entity_id"], "light.living_room")
        self.assertTrue(api.call_service("light", "turn_on"))

if __name__ == '__main__':
    unittest.main()
