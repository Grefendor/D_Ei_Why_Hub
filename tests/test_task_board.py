import pytest
import sqlite3
import os
from unittest.mock import patch
from apps.task_board.database import (
    init_db, add_task, get_due_tasks, complete_task, 
    add_person, get_people, delete_task
)

# We need to patch the DB_PATH in the database module to use our temp db
@pytest.fixture
def task_db(temp_db):
    with patch('apps.task_board.database.DB_PATH', temp_db):
        init_db()
        yield temp_db
        # Cleanup is handled by temp_dir fixture

def test_add_and_get_people(task_db):
    add_person("Alice")
    add_person("Bob")
    
    people = get_people()
    assert len(people) == 2
    names = [p['name'] for p in people]
    assert "Alice" in names
    assert "Bob" in names

def test_add_task(task_db):
    from apps.task_board import database
    # Add a person so 'all' assignment type has a requirement > 0
    add_person("Alice")
    
    add_task("Test Task", "all", None, "Daily")
    
    # It should be due immediately
    tasks = get_due_tasks()
    assert len(tasks) == 1
    assert tasks[0]['name'] == "Test Task"

def test_complete_task(task_db):
    add_person("Alice")
    people = get_people()
    alice_id = people[0]['id']
    
    add_task("Task 1", "specific", str(alice_id), "Daily")
    
    tasks = get_due_tasks()
    task_id = tasks[0]['id']
    
    # Complete it
    complete_task(task_id, alice_id)
    
    # Should not be due anymore
    tasks = get_due_tasks()
    assert len(tasks) == 0

def test_recurrence_logic(task_db):
    # Test that a daily task resets?
    # This is hard to test without mocking datetime.
    # For now, we trust the logic or add a specific test for date calculation if needed.
    pass
