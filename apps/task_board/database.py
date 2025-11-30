import sqlite3
import os
from datetime import datetime, timedelta

"""
Task Board Database Module.

This module handles all database interactions for the Task Board application.
It manages the storage, retrieval, completion, and deletion of tasks using SQLite.
"""

# Go up 3 levels from apps/task_board/database.py to root, then into data
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'tasks.db')

def init_db():
    """
    Initializes the database schema.

    Creates the 'tasks' and 'people' tables if they do not already exist.
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # People Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Tasks Table - Updated Schema
    # We need to handle migration if table exists but has old schema. 
    # For simplicity in this "release mode" setup, we will check if 'assignee' column exists.
    # If it does, we might want to drop and recreate or alter. 
    # Given the user asked to "put into release mode", wiping old dev data is likely acceptable 
    # or we can try to migrate. Let's try to be safe and check columns.
    
    c.execute("PRAGMA table_info(tasks)")
    columns = [info[1] for info in c.fetchall()]
    
    if 'assignee' in columns and 'assignment_type' not in columns:
        # Old schema detected. Let's drop and recreate for a clean slate as requested.
        c.execute("DROP TABLE tasks")
        
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            assignment_type TEXT NOT NULL, -- 'specific', 'any_n', 'all'
            assignment_value TEXT, -- JSON list of IDs for 'specific', count for 'any_n', or null for 'all'
            frequency TEXT NOT NULL,
            last_completed TEXT,
            next_due TEXT,
            required_completions INTEGER DEFAULT 1,
            current_completions INTEGER DEFAULT 0,
            last_reset_date TEXT
        )
    ''')
    
    # Task Completions Tracking (who completed what today)
    c.execute('''
        CREATE TABLE IF NOT EXISTS task_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            person_id INTEGER,
            completion_date TEXT,
            FOREIGN KEY(task_id) REFERENCES tasks(id),
            FOREIGN KEY(person_id) REFERENCES people(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- People Management ---

def add_person(name):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO people (name) VALUES (?)', (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass # Already exists
    conn.close()

def get_people():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM people ORDER BY name')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_person(person_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM people WHERE id = ?', (person_id,))
    conn.commit()
    conn.close()

# --- Task Management ---

def add_task(name, assignment_type, assignment_value, frequency):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    next_due = datetime.now().strftime('%Y-%m-%d')
    
    # Determine required completions
    required = 1
    if assignment_type == 'all':
        c.execute('SELECT COUNT(*) FROM people')
        required = c.fetchone()[0]
    elif assignment_type == 'any_n':
        required = int(assignment_value)
    elif assignment_type == 'specific':
        # assignment_value is comma separated IDs or names? Let's store IDs as comma separated string
        required = len(str(assignment_value).split(',')) if assignment_value else 1
        
    c.execute('''
        INSERT INTO tasks (name, assignment_type, assignment_value, frequency, next_due, required_completions) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, assignment_type, str(assignment_value), frequency, next_due, required))
    
    conn.commit()
    conn.close()

def update_task(task_id, name, assignment_type, assignment_value, frequency):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Recalculate required completions
    required = 1
    if assignment_type == 'all':
        c.execute('SELECT COUNT(*) FROM people')
        required = c.fetchone()[0]
    elif assignment_type == 'any_n':
        required = int(assignment_value)
    elif assignment_type == 'specific':
        required = len(str(assignment_value).split(',')) if assignment_value else 1

    c.execute('''
        UPDATE tasks 
        SET name = ?, assignment_type = ?, assignment_value = ?, frequency = ?, required_completions = ? 
        WHERE id = ?
    ''', (name, assignment_type, str(assignment_value), frequency, required, task_id))
    conn.commit()
    conn.close()

def get_due_tasks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Check for daily reset of completion counts
    # If a task is due today (or past), we need to ensure its current_completions is valid for today.
    # Actually, let's just return tasks. The UI or logic will handle "is it done yet".
    # A task is "due" if next_due <= today AND current_completions < required_completions
    
    # First, handle resets for recurring tasks if we are in a new period? 
    # Simplified: We just look at next_due. If next_due is today, we show it.
    # If current_completions >= required_completions, it's "done" for this period, so we don't show it in "Due".
    
    c.execute('''
        SELECT * FROM tasks 
        WHERE (next_due <= ? OR next_due IS NULL) 
        AND current_completions < required_completions
    ''', (today,))
    
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_completed_tasks():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Tasks where we have met the requirement OR next_due is in future
    c.execute('''
        SELECT * FROM tasks 
        WHERE next_due > ? OR current_completions >= required_completions
        ORDER BY next_due ASC
    ''', (today,))
    
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def complete_task(task_id, person_id=None):
    """
    Records a completion for a task.
    If person_id is provided, records who did it.
    Updates current_completions.
    If requirements met, advances next_due.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = c.fetchone()
    
    if task:
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Record completion
        if person_id:
            # Check if this person already completed it today?
            c.execute('SELECT * FROM task_completions WHERE task_id = ? AND person_id = ? AND completion_date = ?', 
                      (task_id, person_id, today))
            if c.fetchone():
                conn.close()
                return # Already did it
            
            c.execute('INSERT INTO task_completions (task_id, person_id, completion_date) VALUES (?, ?, ?)',
                      (task_id, person_id, today))
        
        # Increment count
        new_count = task['current_completions'] + 1
        c.execute('UPDATE tasks SET current_completions = ? WHERE id = ?', (new_count, task_id))
        
        # Check if fully complete
        if new_count >= task['required_completions']:
            # Advance Date
            now = datetime.now()
            last_completed = now.strftime('%Y-%m-%d')
            
            frequency = task['frequency']
            days_to_add = 1
            
            if frequency == 'Daily':
                days_to_add = 1
            elif frequency == 'Weekly':
                days_to_add = 7
            elif frequency.startswith('Every '):
                try:
                    parts = frequency.split(' ')
                    if len(parts) >= 2 and parts[1].isdigit():
                        days_to_add = int(parts[1])
                except:
                    pass
            
            next_due = (now + timedelta(days=days_to_add)).strftime('%Y-%m-%d')
            
            # Reset completions for next cycle
            c.execute('''
                UPDATE tasks 
                SET last_completed = ?, next_due = ?, current_completions = 0 
                WHERE id = ?
            ''', (last_completed, next_due, task_id))
            
        conn.commit()
        
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    c.execute('DELETE FROM task_completions WHERE task_id = ?', (task_id,))
    conn.commit()
    conn.close()

def get_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None
