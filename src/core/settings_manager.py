"""
Settings Manager Module.

This module handles the persistence and retrieval of application settings.
It manages user preferences such as enabled apps, widget layouts, and other
configuration options, saving them to a JSON file.
"""

import json
import os
from typing import List, Dict, Any

class SettingsManager:
    """
    Manages application configuration and persistence.

    Attributes:
        SETTINGS_FILE (str): The filename for the settings JSON file.
        DEFAULT_SETTINGS (Dict): A dictionary containing default configuration values.
        settings_path (str): The full path to the settings file.
        settings (Dict): The current loaded settings.
    """
    SETTINGS_FILE = "settings.json"
    
    DEFAULT_SETTINGS = {
        "language": "en",
        "enabled_apps": [], # Empty list means all enabled by default (or we can auto-populate)
        "app_order": [],
        "app_positions": {}, # {"app_id": {"row": 0, "col": 0}}
        "enabled_widgets": [],
        "widget_order": [],
        "widget_positions": {} # {index: "widget_id"}
    }

    def __init__(self, settings_dir: str = "."):
        """
        Initializes the SettingsManager.

        Args:
            settings_dir (str): The directory where the settings file should be stored. Defaults to current directory.
        """
        self.settings_path = os.path.join(settings_dir, self.SETTINGS_FILE)
        self.settings = self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        """
        Loads settings from the JSON file.

        Returns:
            Dict[str, Any]: The loaded settings dictionary, or default settings if the file doesn't exist or is invalid.
        """
        if not os.path.exists(self.settings_path):
            return self.DEFAULT_SETTINGS.copy()
        
        try:
            with open(self.settings_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return self.DEFAULT_SETTINGS.copy()

    def save_settings(self):
        """
        Saves the current settings to the JSON file.
        """
        try:
            with open(self.settings_path, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def get_enabled_apps(self) -> List[str]:
        """Returns a list of IDs for enabled applications."""
        return self.settings.get("enabled_apps", [])

    def set_enabled_apps(self, apps: List[str]):
        """Updates the list of enabled applications and saves settings."""
        self.settings["enabled_apps"] = apps
        self.save_settings()
        
    def is_app_enabled(self, app_id: str) -> bool:
        """
        Checks if a specific application is enabled.

        Args:
            app_id (str): The ID of the application to check.

        Returns:
            bool: True if the app is enabled, False otherwise.
        """
        # If list is empty, treat all as enabled? Or should we populate it initially?
        # Let's say if it's in the list, it's enabled. If the list is empty, maybe we treat all as enabled?
        # Better approach: The list contains ONLY enabled apps.
        # But for first run, we might want to enable all found apps.
        # We'll handle "first run" logic in the registry or main UI.
        return app_id in self.settings.get("enabled_apps", [])

    def get_app_order(self) -> List[str]:
        """Returns the preferred order of application IDs."""
        return self.settings.get("app_order", [])

    def set_app_order(self, order: List[str]):
        """Updates the application order and saves settings."""
        self.settings["app_order"] = order
        self.save_settings()

    def get_app_positions(self) -> Dict[str, Dict[str, int]]:
        """Returns the grid positions for applications."""
        return self.settings.get("app_positions", {})

    def set_app_positions(self, positions: Dict[str, Dict[str, int]]):
        """Updates the application positions and saves settings."""
        self.settings["app_positions"] = positions
        self.save_settings()

    def get_enabled_widgets(self) -> List[str]:
        """Returns a list of IDs for enabled widgets."""
        return self.settings.get("enabled_widgets", [])

    def set_enabled_widgets(self, widgets: List[str]):
        """Updates the list of enabled widgets and saves settings."""
        self.settings["enabled_widgets"] = widgets
        self.save_settings()

    def is_widget_enabled(self, widget_id: str) -> bool:
        """Checks if a specific widget is enabled."""
        return widget_id in self.settings.get("enabled_widgets", [])

    def get_widget_order(self) -> List[str]:
        """Returns the preferred order of widget IDs."""
        return self.settings.get("widget_order", [])

    def set_widget_order(self, order: List[str]):
        """Updates the widget order and saves settings."""
        self.settings["widget_order"] = order
        self.save_settings()

    def get_widget_positions(self) -> Dict[int, str]:
        """
        Returns the positions of widgets.
        
        Returns:
            Dict[int, str]: A mapping of position index to widget ID.
        """
        # JSON keys are always strings, so we need to convert keys to int
        raw = self.settings.get("widget_positions", {})
        return {int(k): v for k, v in raw.items()}

    def set_widget_positions(self, positions: Dict[int, str]):
        """Updates the widget positions and saves settings."""
        self.settings["widget_positions"] = positions
        self.save_settings()

    def get_language(self) -> str:
        """Returns the current language code."""
        return self.settings.get("language", "en")

    def set_language(self, language: str):
        """Updates the language and saves settings."""
        self.settings["language"] = language
        self.save_settings()
