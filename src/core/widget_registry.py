"""
Widget Registry Module.

This module provides the `WidgetRegistry` class, which is responsible for discovering
and managing dashboard widgets. It scans a specified directory for Python files
defining widgets and handles their dynamic loading and instantiation.
"""

import os
import importlib.util
import sys
import inspect
from typing import List, Dict, Any, Optional

class WidgetRegistry:
    """
    Manages the discovery and lifecycle of dashboard widgets.

    Attributes:
        widgets_dir (str): The directory path where widgets are located.
        widgets (Dict[str, Dict[str, Any]]): A dictionary storing metadata about available widgets.
    """

    def __init__(self, widgets_dir: str):
        """
        Initializes the WidgetRegistry.

        Args:
            widgets_dir (str): The absolute path to the directory containing widget files.
        """
        self.widgets_dir = widgets_dir
        self.widgets: Dict[str, Dict[str, Any]] = {}
        self.scan_widgets()

    def scan_widgets(self):
        """
        Scans the widgets directory for valid widget implementations.

        It looks for Python files containing classes that end with 'Widget'.
        Valid widgets are registered in the `self.widgets` dictionary.
        """
        self.widgets = {}
        if not os.path.exists(self.widgets_dir):
            return

        for entry in os.scandir(self.widgets_dir):
            if entry.is_file() and entry.name.endswith(".py") and not entry.name.startswith("__"):
                try:
                    module_name = entry.name[:-3] # remove .py
                    spec = importlib.util.spec_from_file_location(f"widgets.{module_name}", entry.path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        sys.modules[f"widgets.{module_name}"] = module
                        spec.loader.exec_module(module)
                        
                        # Find classes ending with 'Widget'
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if name.endswith("Widget") and obj.__module__ == module.__name__:
                                # Use filename as ID (or maybe class name?)
                                # Let's use filename as ID for simplicity, or generate one
                                widget_id = module_name
                                
                                self.widgets[widget_id] = {
                                    "name": name.replace("Widget", ""), # Simple name extraction
                                    "class": obj
                                }
                except Exception as e:
                    print(f"Error loading widget {entry.name}: {e}")

    def get_widget_list(self) -> List[Dict[str, Any]]:
        """
        Retrieves a list of all registered widgets.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing 'id' and 'name' for each widget.
        """
        return [{"id": k, "name": v["name"]} for k, v in self.widgets.items()]

    def get_widget_instance(self, widget_id: str, language_manager=None) -> Optional[Any]:
        """
        Creates a new instance of the specified widget.

        Args:
            widget_id (str): The unique identifier of the widget.
            language_manager (LanguageManager, optional): Passed to widget constructor if accepted.

        Returns:
            Optional[Any]: A new instance of the widget class, or None if instantiation fails.
        """
        if widget_id not in self.widgets:
            return None
            
        widget_data = self.widgets[widget_id]
        # Always create a new instance because the UI might have deleted the previous one
        try:
            if language_manager:
                try:
                    return widget_data["class"](language_manager=language_manager)
                except TypeError:
                    return widget_data["class"]()
            else:
                return widget_data["class"]()
        except Exception as e:
            print(f"Error instantiating widget {widget_id}: {e}")
            return None
