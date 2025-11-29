import os
import shutil

def reset_application_data():
    """
    Deletes all application data databases and configuration files to reset the app to a clean state.
    """
    files_to_delete = [
        os.path.join("data", "tasks.db"),
        os.path.join("data", "lebensmittel.db"),
        os.path.join("data", "events.db"),
        os.path.join("config", "weather_config.json")
    ]
    
    deleted_files = []
    errors = []
    
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
            except Exception as e:
                errors.append(f"Failed to delete {file_path}: {e}")
                
    return deleted_files, errors
