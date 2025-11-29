# D_Ei-Why_Hub
(No Pun intended)
Welcome to **The DEW-Hub**! 

This is your personal, customizable dashboard for managing your daily digital life. Think of it as a home base for your applications and widgets, built with Python and PySide6. It's designed to be sleek, modular, and easy to make your own.

## What Can It Do?

*   **Dashboard**: A grid of your installed applications. Click to launch!
*   **Top Bar**: A customizable strip of widgets like Clock, Weather, and Calendar.
*   **Dynamic Management**: You don't need to touch the code to add new apps or widgets. Just drop them in the right folder, and The Hub finds them.
*   **Drag & Drop Layout**: Want your "Pantry Manager" in the top-left corner? Just drag it there in the Settings. Want the Clock on the far right? Drag it there too!

## Getting Started

1.  **Prerequisites**:
    *   Python 3.x installed.
    *   Install the required dependencies:
        ```bash
        pip install -r requirements.txt
        ```

2.  **Run the App**:
    ```bash
    python main.py
    ```
2.  **Explore**: You'll see the dashboard with default apps.
3.  **Customize**: Click the **Settings** button in the top bar.
    *   **Apps Layout**: Drag apps from the list to the grid to place them exactly where you want.
    *   **Widgets Layout**: Drag widgets to the top bar strip. They stay exactly where you put them.
    *   **General**: Switch between **English** and **German** language.

## Included Applications & Widgets

I have a growing collection of apps and widgets. Check out their detailed documentation:

*   [**Applications Documentation**](apps/README.md): Learn about the Pantry Manager, Task Board, and more.
*   [**Widgets Documentation**](widgets/README.md): Details on the Clock, Weather, and Calendar widgets.

## How to Add Your Own Stuff

### Adding an App 

1.  Create a new folder in `apps/` (e.g., `apps/my_new_app`).
2.  Add your Python code (e.g., `main.py`).
3.  Create a `manifest.json` file in that folder:
    ```json
    {
      "name": "My New App",
      "id": "my_new_app",
      "entry_point": "main.py:MyNewAppClass"
    }
    ```
    *   `entry_point`: The file name and the class name of your app's main widget, separated by a colon.
4.  Restart The Hub. Your app will appear in the Settings list, ready to be placed on the dashboard!

### Internationalization (i18n) for Apps

To make your app translatable:

1.  **Accept `language_manager`**: Ensure your app's `__init__` method accepts a `language_manager` argument.
    ```python
    def __init__(self, language_manager=None):
        super().__init__()
        self.language_manager = language_manager
        # ...
    ```
2.  **Use `translate()`**: Wrap user-facing strings with `self.language_manager.translate("key", "Default Text")`.
3.  **Implement `update_texts()`**: Create a method to refresh UI strings and connect it to the `language_changed` signal.
    ```python
    if self.language_manager:
        self.language_manager.language_changed.connect(self.update_texts)

    def update_texts(self, lang_code=None):
        # Update labels, buttons, window titles here
        pass
    ```
4.  **Add Keys**: Add your translation keys to `languages/en.json` and `languages/de.json`.

### Adding a Widget 

1.  Create a new Python file in `widgets/` (e.g., `widgets/cpu_monitor.py`).
2.  Define a class that inherits from `QWidget` and ends with `Widget` (e.g., `CpuMonitorWidget`).
    ```python
    from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

## Project Structure

*   `main.py`: The entry point.
*   `apps/`: Where applications live.
*   `widgets/`: Where widgets live.
*   `src/`: Core logic (registries, settings, UI components).
*   `tests/`: Verification scripts to ensure everything keeps working.

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for details.

### Third Party Licenses

This project uses the following third-party libraries:

*   **PySide6**: Licensed under the **LGPLv3**.
*   **Requests**: Licensed under the **Apache License 2.0**.
