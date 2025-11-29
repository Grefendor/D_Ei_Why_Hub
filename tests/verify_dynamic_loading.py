import sys
import os
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.app_registry import AppRegistry
from src.core.widget_registry import WidgetRegistry
from src.core.settings_manager import SettingsManager

def test_registries():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    apps_dir = os.path.join(root_dir, "apps")
    widgets_dir = os.path.join(root_dir, "widgets")
    
    print(f"Testing AppRegistry with {apps_dir}...")
    app_registry = AppRegistry(apps_dir)
    apps = app_registry.get_app_list()
    print(f"Found {len(apps)} apps:")
    for app in apps:
        print(f" - {app['name']} ({app['id']})")
        
    if len(apps) < 3:
        print("FAIL: Expected at least 3 apps (Pantry, Task Board, Calendar)")
    else:
        print("PASS: App discovery")

    print(f"\nTesting WidgetRegistry with {widgets_dir}...")
    widget_registry = WidgetRegistry(widgets_dir)
    widgets = widget_registry.get_widget_list()
    print(f"Found {len(widgets)} widgets:")
    for widget in widgets:
        print(f" - {widget['name']} ({widget['id']})")
        
    if len(widgets) < 3:
        print("FAIL: Expected at least 3 widgets (Clock, Weather, Calendar)")
    else:
        print("PASS: Widget discovery")

    print("\nTesting SettingsManager...")
    config_dir = os.path.join(root_dir, "config")
    settings_manager = SettingsManager(config_dir)
    
    # Test default
    if not settings_manager.get_enabled_apps():
        print("Settings empty, simulating first run...")
        settings_manager.set_enabled_apps([app['id'] for app in apps])
        settings_manager.set_app_order([app['id'] for app in apps])
        
    enabled_apps = settings_manager.get_enabled_apps()
    print(f"Enabled apps: {enabled_apps}")
    
    if len(enabled_apps) == len(apps):
        print("PASS: Settings save/load")
    else:
        print("FAIL: Settings save/load mismatch")

    # Test App Positions
    print("\nTesting App Positions...")
    positions = {"pantry_manager": {"row": 0, "col": 1}}
    settings_manager.set_app_positions(positions)
    loaded_positions = settings_manager.get_app_positions()
    if loaded_positions == positions:
        print("PASS: App positions save/load")
    else:
        print(f"FAIL: App positions mismatch. Got {loaded_positions}")

    # Test Widget Positions
    print("\nTesting Widget Positions...")
    w_positions = {0: "clock", 2: "weather"}
    settings_manager.set_widget_positions(w_positions)
    loaded_w_positions = settings_manager.get_widget_positions()
    if loaded_w_positions == w_positions:
        print("PASS: Widget positions save/load")
    else:
        print(f"FAIL: Widget positions mismatch. Got {loaded_w_positions}")

if __name__ == "__main__":
    test_registries()
