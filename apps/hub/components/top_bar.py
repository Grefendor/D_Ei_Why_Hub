from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal, Qt
from src.ui.theme import Theme
from src.ui.volume_control import VolumeControlWidget

class TopBar(QWidget):
    """
    The top bar widget containing widgets, volume control, and navigation buttons.
    """
    home_clicked = Signal()
    settings_clicked = Signal()

    def __init__(self, settings_manager, widget_registry, language_manager, res_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.widget_registry = widget_registry
        self.language_manager = language_manager
        self.res_manager = res_manager
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(self.res_manager.scale(20))
        
        self.setup_ui()

    def setup_ui(self):
        self.populate()

    def populate(self):
        """Fills the top bar with widgets and buttons."""
        # Clear existing items
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Home Button (Hidden by default, controlled by parent)
        self.home_btn = QPushButton(f"🏠 {self.language_manager.translate('home')}")
        btn_width = self.res_manager.scale(140)
        btn_height = self.res_manager.scale(60)
        self.home_btn.setFixedSize(btn_width, btn_height)
        self.home_btn.setStyleSheet(Theme.get_button_style(font_size=self.res_manager.scale(18)))
        self.home_btn.clicked.connect(self.home_clicked.emit)
        self.home_btn.hide()
        
        # Settings Button
        self.settings_btn = QPushButton(f"⚙️ {self.language_manager.translate('settings')}")
        self.settings_btn.setFixedSize(btn_width, btn_height)
        self.settings_btn.setStyleSheet(Theme.get_button_style(font_size=self.res_manager.scale(18)))
        self.settings_btn.clicked.connect(self.settings_clicked.emit)

        # Load Widgets
        positions = self.settings_manager.get_widget_positions()
        
        for i in range(5):
            if i in positions:
                widget_id = positions[i]
                widget_instance = self.widget_registry.get_widget_instance(widget_id, self.language_manager, self.res_manager)
                if widget_instance:
                    self.layout.addWidget(widget_instance)
                else:
                    self.layout.addSpacing(self.res_manager.scale(150))
            else:
                spacer = QWidget()
                spacer.setFixedSize(self.res_manager.scale(150), self.res_manager.scale(10))
                spacer.setStyleSheet("background: transparent;")
                self.layout.addWidget(spacer)
            
            self.layout.addSpacing(self.res_manager.scale(20))
        
        self.layout.addStretch()
        
        # Volume Control
        self.volume_control = VolumeControlWidget(self.language_manager, self.res_manager)
        self.layout.addWidget(self.volume_control)
        
        self.layout.addWidget(self.home_btn)
        self.layout.addWidget(self.settings_btn)

    def set_home_visible(self, visible):
        self.home_btn.setVisible(visible)
        self.settings_btn.setVisible(not visible)

    def update_texts(self):
        self.home_btn.setText(f"🏠 {self.language_manager.translate('home')}")
        self.settings_btn.setText(f"⚙️ {self.language_manager.translate('settings')}")
