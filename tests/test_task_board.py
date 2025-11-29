import sys
import os
import unittest

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.task_board import database

"""
Task Board Database Tests.

This module contains unit tests for the Task Board's database operations,
verifying task creation, retrieval, completion, and deletion.
"""

class TestTaskBoardDB(unittest.TestCase):
    """
    Tests for the Task Board database functions.
    """
    def setUp(self):
        """
        Sets up the test environment.
        """
        database.init_db()

    def test_add_and_get_task(self):
        """
        Tests adding and retrieving a task.
        """
        database.add_task("Test Task 1", "Lasse", "Daily")
        tasks = database.get_due_tasks()
        
        found = False
        for task in tasks:
            if task['name'] == "Test Task 1":
                found = True
                self.assertEqual(task['assignee'], "Lasse")
                self.assertEqual(task['frequency'], "Daily")
                # Clean up
                database.delete_task(task['id'])
                break
        
        self.assertTrue(found)

    def test_complete_task(self):
        database.add_task("Test Task 2", "Sophie", "Daily")
        tasks = database.get_due_tasks()
        
        task_id = None
        for task in tasks:
            if task['name'] == "Test Task 2":
                task_id = task['id']
                break
        
        self.assertIsNotNone(task_id)
        
        database.complete_task(task_id)
        
        # Should not be due anymore
        tasks_after = database.get_due_tasks()
        found_after = False
        for task in tasks_after:
            if task['id'] == task_id:
                found_after = True
                break
        
        self.assertFalse(found_after)
        
        # Clean up
        database.delete_task(task_id)

if __name__ == '__main__':
    unittest.main()
