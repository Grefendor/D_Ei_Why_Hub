import sqlite3
import os
from datetime import datetime, timedelta
import sys
# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.task_board.database import add_task, complete_task, get_due_tasks, DB_PATH

# Reset DB for test
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
from apps.task_board.database import init_db
init_db()

print("--- Test Start ---")

# 1. Add a Daily task
print("1. Adding 'Test Daily Task'")
add_task("Test Daily Task", "Lasse", "Daily")

# Check it's due today
due = get_due_tasks()
print(f"   Due tasks today ({datetime.now().strftime('%Y-%m-%d')}): {[t['name'] for t in due]}")
assert len(due) == 1

# 2. Complete the task
print("\n2. Completing task...")
task_id = due[0]['id']
complete_task(task_id)

# Check it's GONE today
due_after_complete = get_due_tasks()
print(f"   Due tasks immediately after completion: {[t['name'] for t in due_after_complete]}")
assert len(due_after_complete) == 0

# 3. Simulate Tomorrow
print("\n3. Simulating Tomorrow...")
# We can't easily mock datetime.now() inside the imported module without patching.
# Instead, let's just check the DB value directly to see what 'next_due' is set to.

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()
c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
task = c.fetchone()
conn.close()

next_due = task['next_due']
tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

print(f"   Task 'next_due' in DB: {next_due}")
print(f"   Tomorrow's date:       {tomorrow_date}")

if next_due == tomorrow_date:
    print("\nSUCCESS: Task is scheduled for exactly tomorrow.")
    print("It will appear in the list as soon as the date matches.")
else:
    print("\nFAILURE: Dates do not match.")
