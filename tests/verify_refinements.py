
import sys
import os
import sqlite3
import time
from datetime import datetime

# Add project root to path
sys.path.append("c:/Git_Projects/D_Ei_Why_Hub")

from apps.task_board.database import add_task, get_due_tasks, complete_task, get_task, add_person, get_people, DB_PATH
from src.core.data_manager import reset_application_data

def verify_auto_complete():
    print("Verifying Auto-Complete...")
    
    # Setup: Add a person
    add_person("TestUser")
    people = get_people()
    user_id = people[0]['id']
    
    # 1. Add Single Assignee Task
    add_task("Single Task", "specific", str(user_id), "Daily")
    tasks = get_due_tasks()
    single_task = next(t for t in tasks if t['name'] == "Single Task")
    
    # Simulate Auto-Complete Logic (mocking UI logic)
    # In UI: if specific and len(ids) == 1 -> call complete_task(id, user_id)
    
    task_details = get_task(single_task['id'])
    ids = str(task_details['assignment_value']).split(',')
    
    if task_details['assignment_type'] == 'specific' and len(ids) == 1:
        print("  - Detected single assignee task.")
        complete_task(single_task['id'], int(ids[0]))
    else:
        print("  - FAILED: Did not detect single assignee.")
        return False
        
    # Verify it is completed
    updated_task = get_task(single_task['id'])
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # If required was 1, it should have reset current_completions to 0 and set last_completed to today
    if updated_task['last_completed'] == today_str:
        print("  - Task completed successfully (last_completed updated).")
    elif updated_task['current_completions'] == 1:
         print("  - Task completed successfully (count incremented).")
    else:
        print(f"  - FAILED: Task not completed. State: {dict(updated_task)}")
        return False
        
    return True

def verify_data_deletion():
    print("\nVerifying Data Deletion...")
    
    # Create dummy whiteboard file
    wb_path = os.path.join("data", "whiteboard.png")
    os.makedirs("data", exist_ok=True)
    with open(wb_path, "w") as f:
        f.write("dummy data")
        
    if not os.path.exists(wb_path):
        print("  - FAILED: Could not create dummy whiteboard file.")
        return False
        
    # Run Reset
    deleted, errors = reset_application_data()
    
    if wb_path in deleted or not os.path.exists(wb_path):
        print("  - Whiteboard file deleted successfully.")
    else:
        print(f"  - FAILED: Whiteboard file not deleted. Deleted: {deleted}, Errors: {errors}")
        return False
        
    return True

if __name__ == "__main__":
    try:
        if verify_auto_complete() and verify_data_deletion():
            print("\nALL VERIFICATION PASSED!")
        else:
            print("\nVERIFICATION FAILED!")
            sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
