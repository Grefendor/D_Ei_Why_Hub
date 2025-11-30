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
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_dir = os.path.join(root_dir, "config")
        self.settings_manager = SettingsManager(config_dir)
        self.language_manager = LanguageManager(root_dir)
        self.language_manager.load_language(self.settings_manager.get_language())
        
        # Apply Resolution Setting
        resolution_setting = self.settings_manager.get_resolution()
        self.res_manager.update_screen_info(resolution_setting)
        
        self.app_registry = AppRegistry(os.path.join(root_dir, "apps"))
        self.widget_registry = WidgetRegistry(os.path.join(root_dir, "widgets"))
        
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
        if hasattr(self, 'home_btn'):
            self.home_btn.setText(f"🏠 {self.language_manager.translate('home')}")
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setText(f"⚙️ {self.language_manager.translate('settings')}")

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
        
        # Top Bar (Dynamic Widgets)
        self.top_bar = QHBoxLayout()
        self.populate_top_bar()
        
        main_layout.addLayout(self.top_bar)
        
        # Content Area (Stacked Widget)
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # 1. Dashboard View
        self.dashboard_view = QWidget()
        self.dashboard_layout = QGridLayout(self.dashboard_view)
        self.dashboard_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dashboard_layout.setSpacing(self.res_manager.scale(40))
        
        self.populate_dashboard()
        
        self.stack.addWidget(self.dashboard_view)
        
        # 2. App View Container
        self.app_container = QWidget()
        self.app_layout = QVBoxLayout(self.app_container)
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.stack.addWidget(self.app_container)

    def populate_top_bar(self):
        """
        Fills the top bar with your widgets and buttons.

        It grabs the enabled widgets from the registry and puts them in the 
        strip. Also adds the Home and Settings buttons.
        """
        # Clear existing items
        while self.top_bar.count():
            item = self.top_bar.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                pass # Spacers are deleted when taken
        
        # Home Button (Always present, but hidden in dashboard)
        self.home_btn = QPushButton(f"🏠 {self.language_manager.translate('home')}")
        btn_width = self.res_manager.scale(140)
        btn_height = self.res_manager.scale(60)
        self.home_btn.setFixedSize(btn_width, btn_height)
        self.home_btn.setStyleSheet(Theme.get_button_style(font_size=self.res_manager.scale(18)))
        self.home_btn.clicked.connect(self.show_dashboard)
        self.home_btn.hide()
        
        # Settings Button
        self.settings_btn = QPushButton(f"⚙️ {self.language_manager.translate('settings')}")
        self.settings_btn.setFixedSize(btn_width, btn_height)
        self.settings_btn.setStyleSheet(Theme.get_button_style(font_size=self.res_manager.scale(18)))
        self.settings_btn.clicked.connect(self.open_settings)

        # Load Widgets
        positions = self.settings_manager.get_widget_positions()
        
        # We have 5 slots in the editor. Let's respect that.
        # We will add widgets or spacers for indices 0-4.
        
        for i in range(5):
            if i in positions:
                widget_id = positions[i]
                widget_instance = self.widget_registry.get_widget_instance(widget_id, self.language_manager)
                if widget_instance:
                    self.top_bar.addWidget(widget_instance)
                else:
                    # Widget failed to load, add spacer
                    self.top_bar.addSpacing(self.res_manager.scale(150))
            else:
                # Empty slot
                # Add a transparent widget or spacer to hold the space
                # Using addSpacing might be invisible and collapse if not careful with stretch
                # But QHBoxLayout with spacing should work if we don't add stretch elsewhere indiscriminately
                # Let's add a fixed size spacer widget to be sure
                spacer = QWidget()
                spacer.setFixedSize(self.res_manager.scale(150), self.res_manager.scale(10)) # Height doesn't matter much
                spacer.setStyleSheet("background: transparent;")
                self.top_bar.addWidget(spacer)
            
            # Add spacing between slots
            self.top_bar.addSpacing(self.res_manager.scale(20))
        
        self.top_bar.addStretch()
        
        # Volume Control
        from widgets.volume_control import VolumeControlWidget
        self.volume_control = VolumeControlWidget(self.language_manager, self.res_manager)
        self.top_bar.addWidget(self.volume_control)
        
        self.top_bar.addWidget(self.home_btn)
        self.top_bar.addWidget(self.settings_btn)

    def populate_dashboard(self):
        """
        Fills the dashboard with tiles for your apps.

        It checks where you want your apps to be and creates the tiles for them.
        """
        # Clear existing
        while self.dashboard_layout.count():
            item = self.dashboard_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        positions = self.settings_manager.get_app_positions()
        
        # If no positions, maybe default layout?
        if not positions:
            # Default layout logic (linear fill)
            all_apps = self.app_registry.get_app_list(self.language_manager)
            row = 0
            col = 0
            max_cols = 3
            for app in all_apps:
                positions[app["id"]] = {"row": row, "col": col}
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
            # Save default positions? Maybe not, let user decide.
        
        # We need to get app names again to ensure they are localized
        all_apps_map = {app["id"]: app["name"] for app in self.app_registry.get_app_list(self.language_manager)}

        for app_id, pos in positions.items():
            app_name = all_apps_map.get(app_id)
            if not app_name:
                continue
                
            # Generate Preview
            preview_pixmap = None
            app_instance = self.app_registry.get_app_instance(app_id, self.language_manager)
            if app_instance:
                if not app_instance.isVisible():
                    # Resize for preview generation based on resolution
                    preview_w = self.res_manager.scale(800)
                    preview_h = self.res_manager.scale(600)
                    app_instance.resize(preview_w, preview_h)
                preview_pixmap = app_instance.grab()
            
            tile = AppTile(app_id, app_name, preview_pixmap=preview_pixmap)
            tile.launch_app.connect(self.launch_app)
            
            row = pos.get("row", 0)
            col = pos.get("col", 0)
            self.dashboard_layout.addWidget(tile, row, col)

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
            self.home_btn.show()
            self.settings_btn.hide() # Hide settings in app view

    def show_dashboard(self):
        """
        Switches the view back to the main dashboard.
        """
        self.stack.setCurrentWidget(self.dashboard_view)
        self.home_btn.hide()
        self.settings_btn.show()

    def open_settings(self):
        """
        Opens the settings dialog.
        """
        dialog = SettingsDialog(self.settings_manager, self.app_registry, self.widget_registry, self.language_manager, self)
        dialog.data_reset.connect(self.on_data_reset)
        if dialog.exec():
            # Refresh UI
            self.populate_top_bar()
            self.populate_dashboard()

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
        for i in range(self.top_bar.count()):
            item = self.top_bar.itemAt(i)
            widget = item.widget()
            if widget and hasattr(widget, "load_config"):
                widget.load_config()
            elif widget and hasattr(widget, "update_weather"):
                widget.update_weather()

