"""
App Tile Widget Module.

Interactive dashboard tile representing an installed application.
Handles click events to launch the associated app and renders the app's icon or preview.
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QFont

from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme

class AppTile(QPushButton):
    """
    A dashboard tile representing an application.

    Displays an icon (or preview) and the application name.
    Emits `launch_app` signal with the app ID when clicked.
    """
    launch_app = Signal(str) # Emits app_id

    def __init__(self, app_id, name, icon_path=None, preview_pixmap=None, parent=None):
        """
        Initializes the AppTile.

        Args:
            app_id (str): The unique identifier of the app.
            name (str): The display name of the app.
            icon_path (str, optional): Path to the app icon. Defaults to None.
            preview_pixmap (QPixmap, optional): A preview image for the tile. Defaults to None.
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent)
        self.app_id = app_id
        self.name = name
        
        self.res_manager = ResolutionManager()
        
        # Dynamic Size (4:3 aspect ratio)
        width = self.res_manager.scale(360)
        height = self.res_manager.scale(270)
        self.setFixedSize(width, height) 
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Theme.GLASS_COLOR};
                border-radius: {self.res_manager.scale(20)}px;
                border: {Theme.GLASS_BORDER};
                color: {Theme.TEXT_PRIMARY};
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {Theme.GLASS_HOVER};
                border: 1px solid rgba(255, 255, 255, 0.4);
            }}
            QPushButton:pressed {{
                background-color: {Theme.GLASS_PRESSED};
            }}
        """)
        
        layout = QVBoxLayout(self)
        margin = self.res_manager.scale(15)
        layout.setContentsMargins(margin, margin, margin, margin)
        
        # Preview or Icon
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("background: transparent; border: none;")
        
        if preview_pixmap:
            # Scale pixmap to fit inside the tile, leaving room for text
            target_w = width - (margin * 2)
            target_h = height - (margin * 2) - self.res_manager.scale(30) # Space for text
            scaled_pixmap = preview_pixmap.scaled(target_w, target_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
        else:
            # Icon (Placeholder if none provided)
            self.preview_label.setText("📱") 
            font_size = self.res_manager.scale(64)
            self.preview_label.setStyleSheet(f"font-size: {font_size}px; background: transparent; border: none;")
        
        self.name_label = QLabel(name)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        name_font_size = self.res_manager.scale(16)
        self.name_label.setStyleSheet(f"font-size: {name_font_size}px; font-weight: bold; background: transparent; border: none; color: {Theme.TEXT_PRIMARY};")

        layout.addWidget(self.preview_label)
        layout.addWidget(self.name_label)
        
        self.clicked.connect(self.on_click)

    def on_click(self):
        self.launch_app.emit(self.app_id)

