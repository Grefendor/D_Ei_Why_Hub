"""
Application Registry Module.

This module handles finding and loading apps. It scans the 'apps' folder 
and makes sure everything is loaded correctly.
"""

import os
import json
import importlib
import sys
from typing import List, Dict, Any, Optional

class AppRegistry:
    """
    Finds all the apps in the 'apps' folder and loads them up.

    Attributes:
        apps_dir (str): Where we look for apps.
        apps (Dict): Keeps track of all the apps we found.
    """

    def __init__(self, apps_dir: str):
        """
        Sets up the registry and scans for apps.

        Args:
            apps_dir (str): The folder where apps live.
        """
        self.apps_dir = apps_dir
        self.apps: Dict[str, Dict[str, Any]] = {}
        self.scan_apps()

    def scan_apps(self):
        """
        Looks through the 'apps' folder to find valid apps with a manifest.
        """
        self.apps = {}
        if not os.path.exists(self.apps_dir):
            return

        for entry in os.scandir(self.apps_dir):
            if entry.is_dir():
                manifest_path = os.path.join(entry.path, "manifest.json")
                if os.path.exists(manifest_path):
                    try:
                        with open(manifest_path, 'r') as f:
                            manifest = json.load(f)
                            
                        app_id = manifest.get("id")
                        if not app_id:
                            continue
                            
                        self.apps[app_id] = {
                            "name": manifest.get("name", "Unknown App"),
                            "entry_point": manifest.get("entry_point"),
                            "path": entry.path,
                            "instance": None,
                            "class": None
                        }
                    except Exception as e:
                        print(f"Error loading manifest for {entry.name}: {e}")

    def get_app_list(self, language_manager=None) -> List[Dict[str, Any]]:
        """
        Gives you a list of all the apps we found.

        Args:
            language_manager (LanguageManager, optional): If you want translated names.

        Returns:
            List: A list of apps with their IDs and names.
        """
        apps_list = []
        for k, v in self.apps.items():
            name = v["name"]
            if isinstance(name, dict) and language_manager:
                lang = language_manager.current_language
                name = name.get(lang, name.get("en", "Unknown App"))
            elif isinstance(name, dict):
                name = name.get("en", "Unknown App")
                
            apps_list.append({"id": k, "name": name})
        return apps_list

    def get_app_instance(self, app_id: str, language_manager=None) -> Optional[Any]:
        """
        Gets the running instance of an app, or starts it if it's not running.

        Args:
            app_id (str): The ID of the app.
            language_manager (LanguageManager, optional): Passed to the app so it can translate stuff.

        Returns:
            The app instance, or None if something went wrong.
        """
        if app_id not in self.apps:
            return None
            
        app_data = self.apps[app_id]
        if app_data["instance"]:
            return app_data["instance"]
            
        # Load class if not loaded
        if not app_data["class"]:
            entry_point = app_data["entry_point"]
            if not entry_point:
                return None
                
            try:
                module_name, class_name = entry_point.split(":")
                # Use standard import mechanism
                # Assumes apps are in 'apps' package which is in python path
                full_module_name = f"apps.{app_id}.{module_name}"
                module = importlib.import_module(full_module_name)
                app_data["class"] = getattr(module, class_name)
            except Exception as e:
                print(f"Error loading app {app_id}: {e}")
                return None

        # Instantiate
        if app_data["class"]:
            try:
                # Try passing language_manager if available
                if language_manager:
                    try:
                        app_data["instance"] = app_data["class"](language_manager=language_manager)
                    except TypeError:
                        # Fallback to no args
                        app_data["instance"] = app_data["class"]()
                else:
                    app_data["instance"] = app_data["class"]()
                    
                return app_data["instance"]
            except Exception as e:
                print(f"Error instantiating app {app_id}: {e}")
                
        return None
