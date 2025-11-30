import pytest
from unittest.mock import patch
from apps.task_board.database import add_task, get_due_tasks, init_db

@pytest.fixture
def integration_db(temp_db):
    with patch('apps.task_board.database.DB_PATH', temp_db):
        init_db()
        yield temp_db

def test_full_task_flow(integration_db, qapp):
    """
    Simulates a user adding a task and checking it appears.
    """
    # 1. User starts app (simulated by DB init)
    from apps.task_board.database import add_person
    add_person("User")
    
    # 2. User adds a task via UI (simulated by direct DB call for now, 
    #    as full UI automation is complex without accessibility IDs)
    add_task("Integration Task", "all", None, "Daily")
    
    # 3. User checks dashboard (simulated by querying DB)
    tasks = get_due_tasks()
    
    # 4. Verify
    assert len(tasks) == 1
    assert tasks[0]['name'] == "Integration Task"
    
    # In a real integration test with Selenium/Appium or careful PySide testing,
    # we would click buttons. For this scope, verifying the logic flow is sufficient.
