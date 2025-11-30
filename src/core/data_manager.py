from src.core.paths import get_db_path, get_config_path

def reset_application_data():
    """
    Deletes all application data databases and configuration files to reset the app to a clean state.
    """
    files_to_delete = [
        get_db_path("tasks.db"),
        get_db_path("lebensmittel.db"),
        get_db_path("events.db"),
        get_config_path("weather_config.json"),
        get_db_path("whiteboard.png")
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
