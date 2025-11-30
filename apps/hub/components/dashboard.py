from PySide6.QtWidgets import QWidget, QGridLayout
from PySide6.QtCore import Signal, Qt
from widgets.app_tile import AppTile

class Dashboard(QWidget):
    """
    The dashboard widget displaying app tiles.
    """
    app_launched = Signal(str)

    def __init__(self, settings_manager, app_registry, language_manager, res_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.app_registry = app_registry
        self.language_manager = language_manager
        self.res_manager = res_manager
        
        self.layout = QGridLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.setSpacing(self.res_manager.scale(20))
        
        self.populate()

    def populate(self):
        """Fills the dashboard with app tiles."""
        # Clear existing
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        positions = self.settings_manager.get_app_positions()
        
        if not positions:
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
                    preview_w = self.res_manager.scale(800)
                    preview_h = self.res_manager.scale(600)
                    app_instance.resize(preview_w, preview_h)
                preview_pixmap = app_instance.grab()
            
            tile = AppTile(app_id, app_name, preview_pixmap=preview_pixmap)
            tile.launch_app.connect(self.app_launched.emit)
            
            row = pos.get("row", 0)
            col = pos.get("col", 0)
            self.layout.addWidget(tile, row, col)

    def refresh_previews(self):
        """Refreshes app previews."""
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            widget = item.widget()
            
            if isinstance(widget, AppTile):
                app_id = widget.app_id
                app_instance = self.app_registry.get_app_instance(app_id, self.language_manager)
                
                if app_instance:
                    if not app_instance.isVisible():
                        preview_w = self.res_manager.scale(800)
                        preview_h = self.res_manager.scale(600)
                        app_instance.resize(preview_w, preview_h)
                    
                    preview_pixmap = app_instance.grab()
                    widget.update_preview(preview_pixmap)
