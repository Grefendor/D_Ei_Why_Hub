import sys
import os
from PySide6.QtWidgets import QApplication

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from apps.hub.ui import HubWindow
    from apps.calendar.app import CalendarApp
    from apps.task_board.app import TaskBoardApp
    from widgets.app_tile import AppTile
    from widgets.clock import ClockWidget
    from widgets.weather import WeatherWidget
    from widgets.calendar import CalendarWidget
    from src.ui.resolution_manager import ResolutionManager
    from src.ui.theme import Theme
    print("Imports successful.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def verify_initialization():
    print("Verifying initialization...")
    app = QApplication(sys.argv)
    
    try:
        # Initialize ResolutionManager
        res_manager = ResolutionManager()
        print(f"ResolutionManager initialized. Scale factor: {res_manager.scale_factor}")
        
        # Initialize Widgets (headless)
        clock = ClockWidget()
        weather = WeatherWidget()
        calendar = CalendarWidget()
        tile = AppTile("test_app", "Test App")
        
        # Initialize Apps
        cal_app = CalendarApp()
        task_app = TaskBoardApp()
        
        # Initialize Main Window
        window = HubWindow()
        
        print("Initialization successful.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_initialization()
