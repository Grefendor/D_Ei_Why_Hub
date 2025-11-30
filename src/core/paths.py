import os
import sys

# Determine the project root directory
# We assume this file is in src/core/paths.py, so root is two levels up
# However, if running from main.py, sys.path[0] might be the root.
# Let's rely on the file location.

# src/core/paths.py -> src/core -> src -> root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(ROOT_DIR, "data")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
APPS_DIR = os.path.join(ROOT_DIR, "apps")
WIDGETS_DIR = os.path.join(ROOT_DIR, "widgets")
LANGUAGES_DIR = os.path.join(ROOT_DIR, "languages")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

def get_db_path(db_name):
    """Returns the absolute path for a database file in the data directory."""
    return os.path.join(DATA_DIR, db_name)

def get_config_path(config_name):
    """Returns the absolute path for a config file in the config directory."""
    return os.path.join(CONFIG_DIR, config_name)
