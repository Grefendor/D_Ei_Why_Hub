
import sys
import os

# Add project root to path
sys.path.append("c:/Git_Projects/D_Ei_Why_Hub")

try:
    from PySide6.QtWidgets import QApplication
    from apps.task_board.app import TaskBoardApp, AddTaskDialog, ManagePeopleDialog
    
    # Create App
    app = QApplication(sys.argv)
    
    # Instantiate TaskBoardApp
    print("Instantiating TaskBoardApp...")
    board = TaskBoardApp()
    print("TaskBoardApp instantiated successfully.")
    
    # Check if AddTaskDialog can be instantiated (checks for NameErrors in __init__)
    print("Instantiating AddTaskDialog...")
    dialog = AddTaskDialog(board)
    print("AddTaskDialog instantiated successfully.")
    
    print("Verification passed!")
    
except Exception as e:
    print(f"Verification FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
