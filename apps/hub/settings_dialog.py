from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
                             QPushButton, QTabWidget, QWidget, QLabel, QCheckBox, QGridLayout, QFrame, QComboBox)
from PySide6.QtCore import Qt, QMimeData, Signal, Signal

# ... (imports)

class SettingsDialog(QDialog):
    """
    The main settings dialog window.

    Combines the grid editor and widget strip editor into a tabbed interface.
    """
    data_reset = Signal()

    def __init__(self, settings_manager, app_registry, widget_registry, language_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.app_registry = app_registry
        self.widget_registry = widget_registry
        self.language_manager = language_manager
        self.res_manager = ResolutionManager()
        
        self.setWindowTitle(self.language_manager.translate("settings_title"))
        self.resize(self.res_manager.scale(900), self.res_manager.scale(600))
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND_COLOR}; color: {Theme.TEXT_PRIMARY};")
        
        self.setup_ui()
    def reset_data(self):
        """
        Initiates the data reset process with double confirmation.
        """
        # Confirmation 1
        msg1 = self.language_manager.translate("reset_data_confirm_1")
        reply1 = QMessageBox.question(self, self.language_manager.translate("warning"), msg1, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply1 == QMessageBox.StandardButton.Yes:
            # Confirmation 2
            msg2 = self.language_manager.translate("reset_data_confirm_2")
            reply2 = QMessageBox.question(self, self.language_manager.translate("warning"), msg2, 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)
            
            if reply2 == QMessageBox.StandardButton.Yes:
                deleted, errors = reset_application_data()
                
                if errors:
                    error_msg = "\n".join(errors)
                    QMessageBox.critical(self, self.language_manager.translate("error"), f"Errors during reset:\n{error_msg}")
                else:
                    QMessageBox.information(self, self.language_manager.translate("success"), 
                                          self.language_manager.translate("data_reset_success"))
                    self.data_reset.emit()
                    # Optional: Close app or restart? For now just notify.
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor
from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme
from src.core.data_manager import reset_application_data
from PySide6.QtWidgets import QMessageBox

"""
Settings Dialog Module.

Provides a tabbed interface for customizing the dashboard grid and widget strip 
layouts via drag-and-drop.
"""

# --- App Grid Components ---

class DraggableListWidget(QListWidget):
    """
    A QListWidget that supports dragging items.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def startDrag(self, supportedActions):
        """
        Initiates a drag operation for the current item.
        """
        item = self.currentItem()
        if not item:
            return
            
        app_id = item.data(Qt.ItemDataRole.UserRole)
        
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(app_id)
        drag.setMimeData(mime_data)
        
        # Create a pixmap for the drag
        # We can try to get the widget if it's a custom widget, or just draw the text
        pixmap = QPixmap(100, 30)
        pixmap.fill(QColor(Theme.GLASS_COLOR))
        painter = QPainter(pixmap)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, item.text())
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        
        drag.exec(supportedActions)

class DraggableAppItem(QFrame):
    """
    A visual representation of an app in the grid editor that can be dragged.
    """
    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.setFixedSize(100, 100)
        self.setStyleSheet(f"""
            background-color: {Theme.GLASS_COLOR};
            border: 1px solid #555;
            border-radius: 10px;
        """)
        
        layout = QVBoxLayout(self)
        label = QLabel(app_data["name"])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.app_data["id"])
            drag.setMimeData(mime_data)
            
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            
            drag.exec(Qt.DropAction.MoveAction)

class AppSlot(QFrame):
    """
    A drop target slot in the dashboard grid editor.
    """
    def __init__(self, row, col, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.app_id = None
        self.setAcceptDrops(True)
        self.setFixedSize(110, 110)
        self.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 0.05);
            border: 2px dashed #555;
            border-radius: 10px;
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
    def set_app(self, app_data):
        self.clear_app()
        self.app_id = app_data["id"]
        item = DraggableAppItem(app_data, self)
        self.layout.addWidget(item)
        
    def clear_app(self):
        self.app_id = None
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        app_id = event.mimeData().text()
        if self.window().handle_drop(self.row, self.col, app_id):
            event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.clear_app()
            self.window().handle_clear(self.row, self.col)

class GridEditorWidget(QWidget):
    """
    Widget for editing the dashboard application grid layout.
    """
    def __init__(self, app_registry, settings_manager, language_manager, parent=None):
        super().__init__(parent)
        self.app_registry = app_registry
        self.settings_manager = settings_manager
        self.language_manager = language_manager
        self.slots = {} # (row, col) -> AppSlot
        
        self.setup_ui()
        self.load_grid()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Available Apps List
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel(self.language_manager.translate("available_apps")))
        self.apps_list = DraggableListWidget()
        left_panel.addWidget(self.apps_list)
        layout.addLayout(left_panel, stretch=1)
        
        # Grid
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel(self.language_manager.translate("dashboard_grid")))
        
        grid_frame = QFrame()
        grid_frame.setStyleSheet("background-color: rgba(0,0,0,0.2); border-radius: 15px;")
        self.grid_layout = QGridLayout(grid_frame)
        self.grid_layout.setSpacing(10)
        
        for r in range(3):
            for c in range(3):
                slot = AppSlot(r, c)
                self.grid_layout.addWidget(slot, r, c)
                self.slots[(r, c)] = slot
                
        right_panel.addWidget(grid_frame)
        layout.addLayout(right_panel, stretch=2)
        
        self.populate_available_apps()

    def populate_available_apps(self):
        self.apps_list.clear()
        for app in self.app_registry.get_app_list(self.language_manager):
            item = QListWidgetItem(app["name"])
            item.setData(Qt.ItemDataRole.UserRole, app["id"])
            self.apps_list.addItem(item)

    def load_grid(self):
        positions = self.settings_manager.get_app_positions()
        all_apps = {app["id"]: app for app in self.app_registry.get_app_list(self.language_manager)}
        
        for app_id, pos in positions.items():
            row = pos.get("row")
            col = pos.get("col")
            if (row, col) in self.slots and app_id in all_apps:
                self.slots[(row, col)].set_app(all_apps[app_id])

    def get_positions(self):
        positions = {}
        for (r, c), slot in self.slots.items():
            if slot.app_id:
                positions[slot.app_id] = {"row": r, "col": c}
        return positions

# --- Widget Strip Components ---

class DraggableWidgetItem(QFrame):
    """
    A visual representation of a widget in the strip editor that can be dragged.
    """
    def __init__(self, widget_data, parent=None):
        super().__init__(parent)
        self.widget_data = widget_data
        self.setFixedSize(100, 60)
        self.setStyleSheet(f"""
            background-color: {Theme.GLASS_COLOR};
            border: 1px solid #555;
            border-radius: 10px;
        """)
        
        layout = QVBoxLayout(self)
        label = QLabel(widget_data["name"])
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(label)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.widget_data["id"])
            drag.setMimeData(mime_data)
            
            pixmap = self.grab()
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())
            
            drag.exec(Qt.DropAction.MoveAction)

class WidgetSlot(QFrame):
    """
    A drop target slot in the widget strip editor.
    """
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        self.widget_id = None
        self.setAcceptDrops(True)
        self.setFixedSize(110, 70)
        self.setStyleSheet(f"""
            background-color: rgba(255, 255, 255, 0.05);
            border: 2px dashed #555;
            border-radius: 10px;
        """)
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
    def set_widget(self, widget_data):
        self.clear_widget()
        self.widget_id = widget_data["id"]
        item = DraggableWidgetItem(widget_data, self)
        self.layout.addWidget(item)
        
    def clear_widget(self):
        self.widget_id = None
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        widget_id = event.mimeData().text()
        if self.window().handle_widget_drop(self.index, widget_id):
            event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.clear_widget()
            self.window().handle_widget_clear(self.index)

class WidgetStripEditor(QWidget):
    """
    Widget for editing the top bar widget strip layout.
    """
    def __init__(self, widget_registry, settings_manager, language_manager, parent=None):
        super().__init__(parent)
        self.widget_registry = widget_registry
        self.settings_manager = settings_manager
        self.language_manager = language_manager
        self.slots = [] # list of WidgetSlot
        
        self.setup_ui()
        self.load_strip()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Available Widgets
        top_panel = QHBoxLayout()
        top_panel.addWidget(QLabel(self.language_manager.translate("available_widgets")))
        self.widgets_list = DraggableListWidget()
        self.widgets_list.setFixedHeight(100)
        self.widgets_list.setFlow(QListWidget.Flow.LeftToRight)
        top_panel.addWidget(self.widgets_list)
        layout.addLayout(top_panel)
        
        # Strip
        bottom_panel = QVBoxLayout()
        bottom_panel.addWidget(QLabel(self.language_manager.translate("top_bar_layout")))
        
        strip_frame = QFrame()
        strip_frame.setStyleSheet("background-color: rgba(0,0,0,0.2); border-radius: 15px;")
        self.strip_layout = QHBoxLayout(strip_frame)
        self.strip_layout.setSpacing(10)
        self.strip_layout.addStretch()
        
        # Create 5 slots for now
        for i in range(5):
            slot = WidgetSlot(i)
            self.strip_layout.insertWidget(i, slot)
            self.slots.append(slot)
            
        self.strip_layout.addStretch()
        bottom_panel.addWidget(strip_frame)
        layout.addLayout(bottom_panel)
        
        self.populate_available_widgets()

    def populate_available_widgets(self):
        self.widgets_list.clear()
        for widget in self.widget_registry.get_widget_list():
            item = QListWidgetItem(widget["name"])
            item.setData(Qt.ItemDataRole.UserRole, widget["id"])
            self.widgets_list.addItem(item)

    def load_strip(self):
        positions = self.settings_manager.get_widget_positions()
        all_widgets = {w["id"]: w for w in self.widget_registry.get_widget_list()}
        
        for index, widget_id in positions.items():
            if index < len(self.slots) and widget_id in all_widgets:
                self.slots[index].set_widget(all_widgets[widget_id])

    def get_positions(self):
        positions = {}
        for slot in self.slots:
            if slot.widget_id:
                positions[slot.index] = slot.widget_id
        return positions

# --- Main Dialog ---

class SettingsDialog(QDialog):
    """
    The main settings dialog window.

    Combines the grid editor and widget strip editor into a tabbed interface.
    """
    data_reset = Signal()

    def __init__(self, settings_manager, app_registry, widget_registry, language_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.app_registry = app_registry
        self.widget_registry = widget_registry
        self.language_manager = language_manager
        self.res_manager = ResolutionManager()
        
        self.setWindowTitle(self.language_manager.translate("settings_title"))
        self.resize(self.res_manager.scale(900), self.res_manager.scale(600))
        self.setStyleSheet(f"background-color: {Theme.BACKGROUND_COLOR}; color: {Theme.TEXT_PRIMARY};")
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #444; }}
            QTabBar::tab {{ background: #333; color: #ccc; padding: 10px; }}
            QTabBar::tab:selected {{ background: #555; color: white; }}
        """)
        
        # General Tab
        self.general_tab = QWidget()
        general_layout = QVBoxLayout(self.general_tab)
        
        lang_layout = QHBoxLayout()
        lang_layout.addWidget(QLabel(f"{self.language_manager.translate('language')}:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(self.language_manager.get_available_languages())
        self.lang_combo.setCurrentText(self.settings_manager.get_language())
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        
        general_layout.addLayout(lang_layout)
        
        # Reset Data Button
        reset_layout = QHBoxLayout()
        reset_btn = QPushButton(self.language_manager.translate("reset_data"))
        reset_btn.setStyleSheet("background-color: #ff5555; color: white; padding: 8px;")
        reset_btn.clicked.connect(self.reset_data)
        reset_layout.addWidget(reset_btn)
        reset_layout.addStretch()
        
        general_layout.addLayout(reset_layout)
        general_layout.addStretch()
        
        self.tabs.addTab(self.general_tab, self.language_manager.translate("general"))

        # Apps Tab (Grid Editor)
        self.grid_editor = GridEditorWidget(self.app_registry, self.settings_manager, self.language_manager)
        self.tabs.addTab(self.grid_editor, self.language_manager.translate("apps_layout"))
        
        # Widgets Tab (Strip Editor)
        self.widget_editor = WidgetStripEditor(self.widget_registry, self.settings_manager, self.language_manager)
        self.tabs.addTab(self.widget_editor, self.language_manager.translate("widgets_layout"))
        
        layout.addWidget(self.tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton(self.language_manager.translate("save"))
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px;")
        
        cancel_btn = QPushButton(self.language_manager.translate("cancel"))
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px;")
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def save_settings(self):
        """
        Saves all configuration changes to the settings manager.
        """
        # General
        selected_lang = self.lang_combo.currentText()
        self.settings_manager.set_language(selected_lang)
        self.language_manager.load_language(selected_lang)

        # Apps
        positions = self.grid_editor.get_positions()
        self.settings_manager.set_app_positions(positions)
        
        # Also update enabled apps based on what's in the grid
        enabled_apps = list(positions.keys())
        self.settings_manager.set_enabled_apps(enabled_apps)
        
        # Widgets
        widget_positions = self.widget_editor.get_positions()
        self.settings_manager.set_widget_positions(widget_positions)
        
        # Update enabled/order for backward compatibility or other uses
        enabled_widgets = list(widget_positions.values())
        self.settings_manager.set_enabled_widgets(enabled_widgets)
        self.settings_manager.set_widget_order(enabled_widgets)
        
        self.accept()

    def reset_data(self):
        """
        Initiates the data reset process with double confirmation.
        """
        # Confirmation 1
        msg1 = self.language_manager.translate("reset_data_confirm_1")
        reply1 = QMessageBox.question(self, self.language_manager.translate("warning"), msg1, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        
        if reply1 == QMessageBox.StandardButton.Yes:
            # Confirmation 2
            msg2 = self.language_manager.translate("reset_data_confirm_2")
            reply2 = QMessageBox.question(self, self.language_manager.translate("warning"), msg2, 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)
            
            if reply2 == QMessageBox.StandardButton.Yes:
                deleted, errors = reset_application_data()
                
                if errors:
                    error_msg = "\n".join(errors)
                    QMessageBox.critical(self, self.language_manager.translate("error"), f"Errors during reset:\n{error_msg}")
                else:
                    QMessageBox.information(self, self.language_manager.translate("success"), 
                                          self.language_manager.translate("data_reset_success"))
                    self.data_reset.emit()
                    # Optional: Close app or restart? For now just notify.

    # Handlers for Grid Editor
    def handle_drop(self, row, col, app_id):
        # Check if app is already in another slot
        for (r, c), slot in self.grid_editor.slots.items():
            if slot.app_id == app_id:
                slot.clear_app()
                break
        
        # Find app data
        all_apps = {app["id"]: app for app in self.app_registry.get_app_list(self.language_manager)}
        if app_id in all_apps:
            self.grid_editor.slots[(row, col)].set_app(all_apps[app_id])
            return True
        return False

    def handle_clear(self, row, col):
        # Just cleared by the slot itself
        pass

    # Handlers for Widget Editor
    def handle_widget_drop(self, index, widget_id):
        # Check if widget is already in another slot
        for slot in self.widget_editor.slots:
            if slot.widget_id == widget_id:
                slot.clear_widget()
                break
        
        # Find widget data
        all_widgets = {w["id"]: w for w in self.widget_registry.get_widget_list()}
        if widget_id in all_widgets:
            self.widget_editor.slots[index].set_widget(all_widgets[widget_id])
            return True
        return False

    def handle_widget_clear(self, index):
        pass
