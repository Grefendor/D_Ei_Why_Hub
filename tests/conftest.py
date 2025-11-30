import pytest
import os
import sys
import shutil
import tempfile
from PySide6.QtWidgets import QApplication

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.settings_manager import SettingsManager
from src.core.paths import get_db_path

@pytest.fixture(scope="session")
def qapp():
    """
    Fixture to manage the QApplication instance.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

@pytest.fixture
def temp_dir():
    """
    Creates a temporary directory for testing.
    """
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_settings(temp_dir):
    """
    Creates a SettingsManager with a temporary config directory.
    """
    config_dir = os.path.join(temp_dir, "config")
    os.makedirs(config_dir)
    return SettingsManager(config_dir)

@pytest.fixture
def temp_db(temp_dir):
    """
    Sets up a temporary database path and ensures it's clean.
    """
    # We need to patch the DB path in the module we are testing
    # For now, we just return a path that tests can use
    db_path = os.path.join(temp_dir, "test_tasks.db")
    return db_path
