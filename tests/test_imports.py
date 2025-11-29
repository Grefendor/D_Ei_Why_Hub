"""
Import Test Script.

This script verifies that all major application modules can be imported successfully.
It helps detect circular import issues or missing dependencies early.
"""

import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Testing imports...")
    from apps.hub.ui import HubWindow
    print("Successfully imported apps.hub.ui.HubWindow")
    
    from apps.pantry_manager.ui_qt import LebensmittelManagerApp
    print("Successfully imported apps.pantry_manager.ui_qt.LebensmittelManagerApp")
    
    from apps.task_board.app import TaskBoardApp
    print("Successfully imported apps.task_board.app.TaskBoardApp")
    
    from apps.task_board.database import get_completed_tasks
    print("Successfully imported apps.task_board.database.get_completed_tasks")

    from widgets.clock import ClockWidget
    print("Successfully imported widgets.clock.ClockWidget")
    
    print("All imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
