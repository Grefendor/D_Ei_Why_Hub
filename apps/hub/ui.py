from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QStackedWidget, QGridLayout, QPushButton, QFrame)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPalette, QColor

from widgets.app_tile import AppTile
from .settings_dialog import SettingsDialog

from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme
from src.core.app_registry import AppRegistry
from src.core.widget_registry import WidgetRegistry
from src.core.settings_manager import SettingsManager
from src.core.language_manager import LanguageManager

import os

"""
Hub UI Module.

This is the main UI for the Hub. It handles the dashboard, launching apps, 
and managing the top bar widget strip.
"""

from src.core.screensaver_manager import ScreensaverManager
from .screensaver_ui import ScreensaverWindow
from .components.top_bar import TopBar
from .components.dashboard import Dashboard

class HubWindow(QMainWindow):
    """
    The main window for the Hub.

    It manages the central dashboard, lets you switch between apps, and handles 
    global stuff like the top bar and settings.
    """
    def __init__(self):
        """Sets up the window, loads settings, and gets everything ready."""
        super().__init__()
        self.setWindowTitle("The Hub")
        
        self.res_manager = ResolutionManager()
        

        
        # Initialize Core Systems
        from src.core.paths import CONFIG_DIR, ROOT_DIR, APPS_DIR, WIDGETS_DIR
        
        self.settings_manager = SettingsManager(CONFIG_DIR)
        self.language_manager = LanguageManager(ROOT_DIR)
        self.language_manager.load_language(self.settings_manager.get_language())
        
        # Apply Resolution Setting
        resolution_setting = self.settings_manager.get_resolution()
        self.res_manager.update_screen_info(resolution_setting)
        
        self.app_registry = AppRegistry(APPS_DIR)
        self.widget_registry = WidgetRegistry(WIDGETS_DIR)
        
        # Screensaver
        self.screensaver_manager = ScreensaverManager(self.settings_manager)
        self.screensaver_window = ScreensaverWindow(self.settings_manager)
        
        self.screensaver_manager.activate_screensaver.connect(self.screensaver_window.start)
        self.screensaver_manager.deactivate_screensaver.connect(self.screensaver_window.stop)
        self.screensaver_window.activity_detected.connect(self.screensaver_manager.deactivate)
        
        # Apply Theme
        self.setStyleSheet(f"QMainWindow {{ background: {Theme.BACKGROUND_GRADIENT}; }}")
        
        # Fullscreen by default
        self.showFullScreen()

        self.active_app = None

        self.setup_ui()
        self.update_texts()
        self.language_manager.language_changed.connect(self.update_texts)

    def update_texts(self, lang_code=None):
        """Updates UI texts based on current language."""
        self.setWindowTitle(self.language_manager.translate("app_title"))
        if hasattr(self, 'top_bar'):
            self.top_bar.update_texts()

    def setup_ui(self):
        """
        Sets up the layout, including the top bar and the main content area 
        where apps and the dashboard live.
        """
        # Create central widget if it doesn't exist (re-creation support)
        if not self.centralWidget():
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
        else:
            central_widget = self.centralWidget()
            # Clear existing layout
            if central_widget.layout():
                QWidget().setLayout(central_widget.layout()) # Trick to delete layout
        
        # Main Layout
        main_layout = QVBoxLayout(central_widget)
        margin = self.res_manager.scale(30)
        main_layout.setContentsMargins(margin, margin, margin, margin)
        main_layout.setSpacing(self.res_manager.scale(20))
        
        # Top Bar
        self.top_bar = TopBar(self.settings_manager, self.widget_registry, self.language_manager, self.res_manager)
        self.top_bar.home_clicked.connect(self.show_dashboard)
        self.top_bar.settings_clicked.connect(self.open_settings)
        main_layout.addWidget(self.top_bar)
        
        # Content Area (Stacked Widget)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # 1. Dashboard View
        self.dashboard = Dashboard(self.settings_manager, self.app_registry, self.language_manager, self.res_manager)
        self.dashboard.app_launched.connect(self.launch_app)
        self.stack.addWidget(self.dashboard)
        
        # 2. App View Container
        self.app_container = QWidget()
        self.app_layout = QVBoxLayout(self.app_container)
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self.app_container)



    def launch_app(self, app_id):
        """
        Launches or switches to an app.

        Args:
            app_id (str): The ID of the app you want to open.
        """
        print(f"Launching {app_id}...")
        app_instance = self.app_registry.get_app_instance(app_id, self.language_manager)
        
        if app_instance:
            # Clear previous app if any
            if self.active_app:
                self.app_layout.removeWidget(self.active_app)
                self.active_app.setParent(None) 
                self.active_app.hide()
                self.active_app = None

            self.active_app = app_instance
            self.active_app.setWindowFlags(Qt.WindowType.Widget)
            
            self.app_layout.addWidget(self.active_app)
            self.active_app.show() 
            
            self.stack.setCurrentWidget(self.app_container)

            self.top_bar.set_home_visible(True)

    def show_dashboard(self):
        """
        Switches the view back to the main dashboard.
        """
        self.dashboard.refresh_previews()
        self.stack.setCurrentWidget(self.dashboard)
        self.top_bar.set_home_visible(False)



    def open_settings(self):
        """
        Opens the settings dialog.
        """
        dialog = SettingsDialog(self.settings_manager, self.app_registry, self.widget_registry, self.language_manager, self)
        dialog.data_reset.connect(self.on_data_reset)
        if dialog.exec():

            # Refresh UI
            self.top_bar.populate()
            self.dashboard.populate()

    def on_data_reset(self):
        """
        Called when data is reset from settings.
        Refreshes all running apps and widgets.
        """
        print("Data reset! Refreshing apps...")
        
        # 1. Refresh Apps
        # We need to iterate over all instantiated apps
        for app_id, app_data in self.app_registry.apps.items():
            instance = app_data.get("instance")
            if instance:
                # Try common refresh methods
                if hasattr(instance, "refresh_data"):
                    instance.refresh_data()
                elif hasattr(instance, "refresh_table"):
                    instance.refresh_table()
                elif hasattr(instance, "refresh_tasks"):
                    instance.refresh_tasks()
                elif hasattr(instance, "refresh"):
                    instance.refresh()
                    
        # 2. Refresh Widgets (if they have data)
        # TODO: Implement widget refresh if needed. 
        # Most widgets update on timer, so they might catch up eventually.
        # But we can force update if they have an update method.
        
        # 3. Reload Weather Config (if it was deleted)
        # The weather widget might need to be re-initialized or told to reload.
        # Since widgets are in the top bar, we can iterate them.
        # This is now handled inside TopBar or we can just repopulate
        self.top_bar.populate()

