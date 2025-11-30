# D_Ei_Why_Hub

The D_Ei_Why_Hub is a customizable, modular dashboard application designed for managing daily digital tasks. Built with Python and PySide6, it serves as a central interface for various applications and widgets, offering a streamlined user experience.

## Capabilities

*   **Dashboard**: A grid-based launcher for installed applications.
*   **Top Bar**: A customizable area for persistent widgets such as Clock, Weather, and Calendar.
*   **Dynamic Management**: The system automatically detects and integrates new applications and widgets placed in the respective directories.
*   **Customizable Layout**: Users can rearrange applications and widgets via the Settings interface to suit their workflow.

## Getting Started

### Prerequisites

*   Python 3.x installed.
*   Required dependencies installed via pip:
    ```bash
    pip install -r requirements.txt
    ```

### Execution

1.  **Launch the Application**:
    ```bash
    python main.py
    ```
2.  **Navigation**: The dashboard displays available applications.
3.  **Configuration**: Access the **Settings** menu to:
    *   **Manage Layouts**: Drag and drop applications and widgets to reorder them.
    *   **General Settings**: Toggle between available languages (English, German).

## Included Applications & Widgets

The platform includes a suite of default applications and widgets. Detailed documentation for these components can be found in their respective directories:

*   [**Applications Documentation**](apps/README.md): Detailed information on the Pantry Manager, Task Board, and other integrated tools.
*   [**Widgets Documentation**](widgets/README.md): Specifications for the Clock, Weather, and Calendar widgets.

## Extending the Application

The architecture is designed for extensibility, allowing developers to easily add custom applications and widgets.

### Adding a New Application

To integrate a new application:

1.  **Create Directory**: Create a new folder within the `apps/` directory (e.g., `apps/my_new_app`).
2.  **Implementation**: Add the application logic (e.g., `main.py`).
3.  **Manifest Configuration**: Create a `manifest.json` file in the application folder with the following structure:
    ```json
    {
      "name": "My New App",
      "id": "my_new_app",
      "entry_point": "main.py:MyNewAppClass"
    }
    ```
    *   `entry_point`: Specifies the filename and the class name of the main widget, separated by a colon.
4.  **Deployment**: Restart the application. The new app will be detected and listed in the Settings menu for placement on the dashboard.

#### Internationalization (i18n) for Apps

To ensure translatability for a custom application:

1.  **Initialize Language Manager**: Ensure the application's `__init__` method accepts a `language_manager` argument.
    ```python
    def __init__(self, language_manager=None):
        super().__init__()
        self.language_manager = language_manager
        # ...
    ```
2.  **Implement Translation**: Use the `translate` method for user-facing strings: `self.language_manager.translate("key", "Default Text")`.
3.  **Dynamic Updates**: Implement a method to refresh UI text and connect it to the `language_changed` signal.
    ```python
    if self.language_manager:
        self.language_manager.language_changed.connect(self.update_texts)

    def update_texts(self, lang_code=None):
        # Update labels, buttons, and window titles here
        pass
    ```
4.  **Translation Files**: Add the corresponding translation keys to `languages/en.json` and `languages/de.json`.

### Adding a New Widget

To add a custom widget:

1.  **Create File**: Create a new Python file in the `widgets/` directory (e.g., `widgets/cpu_monitor.py`).
2.  **Implementation**: Define a class that inherits from `QWidget`. The class name **must** end with `Widget` (e.g., `CpuMonitorWidget`).
    ```python
    from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

    class CpuMonitorWidget(QWidget):
        def __init__(self):
            super().__init__()
            layout = QVBoxLayout()
            self.label = QLabel("CPU: 0%")
            layout.addWidget(self.label)
            self.setLayout(layout)
    ```
3.  **Deployment**: Restart the application. The widget will be automatically detected and available in the Settings menu.

## Project Structure

*   `main.py`: Application entry point.
*   `apps/`: Directory for application modules.
*   `widgets/`: Directory for widget modules.
*   `src/`: Core system logic, including registries, settings management, and UI components.
*   `tests/`: Automated tests and verification scripts.

## License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for details.

### Third Party Licenses

This project utilizes the following third-party libraries:

*   **PySide6**: Licensed under the **LGPLv3**.
*   **Requests**: Licensed under the **Apache License 2.0**.
*   **pycaw**: Licensed under the **MIT License**.
*   **comtypes**: Licensed under the **MIT License**.
