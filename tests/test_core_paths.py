import os
import sys
from src.core.paths import ROOT_DIR, DATA_DIR, CONFIG_DIR, APPS_DIR, WIDGETS_DIR, get_db_path, get_config_path

def test_root_dir_exists():
    assert os.path.exists(ROOT_DIR)
    assert os.path.isdir(ROOT_DIR)

def test_data_dir_structure():
    assert os.path.exists(DATA_DIR)
    assert DATA_DIR.startswith(ROOT_DIR)
    assert DATA_DIR.endswith("data")

def test_config_dir_structure():
    assert os.path.exists(CONFIG_DIR)
    assert CONFIG_DIR.startswith(ROOT_DIR)
    assert CONFIG_DIR.endswith("config")

def test_apps_dir_structure():
    assert os.path.exists(APPS_DIR)
    assert APPS_DIR.startswith(ROOT_DIR)
    assert APPS_DIR.endswith("apps")

def test_widgets_dir_structure():
    assert os.path.exists(WIDGETS_DIR)
    assert WIDGETS_DIR.startswith(ROOT_DIR)
    assert WIDGETS_DIR.endswith("widgets")

def test_get_db_path():
    path = get_db_path("test.db")
    assert path == os.path.join(DATA_DIR, "test.db")

def test_get_config_path():
    path = get_config_path("test.json")
    assert path == os.path.join(CONFIG_DIR, "test.json")
