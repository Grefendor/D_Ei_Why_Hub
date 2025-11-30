from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QIcon

from src.core.volume_manager import VolumeManager
from src.ui.theme import Theme

class VolumeControlWidget(QFrame):
    """
    A widget that provides volume control (mute/unmute and slider).
    
    It polls the system volume to stay in sync with external changes.
    """
    
    def __init__(self, language_manager, res_manager):
        """
        Initializes the volume control widget.

        Args:
            language_manager: The LanguageManager instance for translations.
            res_manager: The ResolutionManager instance for scaling.
        """
        super().__init__()
        self.language_manager = language_manager
        self.res_manager = res_manager
        self.volume_manager = VolumeManager()
        
        self.is_muted = False
        self.current_volume = 0
        
        self.setup_ui()
        
        # Initial sync
        self.update_volume_from_system()
        
        # Timer for polling system volume (every 2 seconds)
        # This ensures the UI stays updated if the user changes volume via OS controls
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_volume_from_system)
        self.timer.start(2000)

    def setup_ui(self):
        """Sets up the layout and widgets."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(self.res_manager.scale(10))
        
        # Mute Button
        self.mute_btn = QPushButton()
        self.mute_btn.setFixedSize(self.res_manager.scale(40), self.res_manager.scale(40))
        self.mute_btn.clicked.connect(self.toggle_mute)
        self.mute_btn.setStyleSheet(Theme.get_button_style(font_size=self.res_manager.scale(14)))
        layout.addWidget(self.mute_btn)
        
        # Volume Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setFixedWidth(self.res_manager.scale(100))
        self.slider.valueChanged.connect(self.on_slider_changed)
        
        # Style the slider to look nice
        self.slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #bbb;
                background: white;
                height: {self.res_manager.scale(10)}px;
                border-radius: {self.res_manager.scale(4)}px;
            }}

            QSlider::sub-page:horizontal {{
                background: {Theme.ACCENT_COLOR};
                border: 1px solid #777;
                height: {self.res_manager.scale(10)}px;
                border-radius: {self.res_manager.scale(4)}px;
            }}

            QSlider::add-page:horizontal {{
                background: #fff;
                border: 1px solid #777;
                height: {self.res_manager.scale(10)}px;
                border-radius: {self.res_manager.scale(4)}px;
            }}

            QSlider::handle:horizontal {{
                background: {Theme.TEXT_PRIMARY};
                border: 1px solid #777;
                width: {self.res_manager.scale(18)}px;
                margin-top: -{self.res_manager.scale(5)}px;
                margin-bottom: -{self.res_manager.scale(5)}px;
                border-radius: {self.res_manager.scale(9)}px;
            }}
        """)
        layout.addWidget(self.slider)
        
        self.update_ui_state()

    def update_volume_from_system(self):
        """Reads the current volume and mute state from the system and updates UI."""
        vol = self.volume_manager.get_volume()
        muted = self.volume_manager.is_muted()
        
        # Only update if changed to avoid loops/jitter
        if vol != self.current_volume or muted != self.is_muted:
            self.current_volume = vol
            self.is_muted = muted
            
            # Block signals to prevent feedback loop
            self.slider.blockSignals(True)
            self.slider.setValue(self.current_volume)
            self.slider.blockSignals(False)
            
            self.update_ui_state()

    def on_slider_changed(self, value):
        """
        Called when the slider is moved by the user.
        
        Args:
            value (int): The new volume value.
        """
        self.current_volume = value
        self.volume_manager.set_volume(value)
        
        # If dragging slider, we probably want to unmute
        if self.is_muted:
            self.volume_manager.unmute()
            self.is_muted = False
            self.update_ui_state()

    def toggle_mute(self):
        """Toggles the mute state."""
        self.volume_manager.toggle_mute()
        self.is_muted = not self.is_muted
        self.update_ui_state()

    def update_ui_state(self):
        """Updates the button icon/text based on state."""
        if self.is_muted or self.current_volume == 0:
            self.mute_btn.setText("🔇")
        elif self.current_volume < 30:
            self.mute_btn.setText("🔈")
        elif self.current_volume < 70:
            self.mute_btn.setText("🔉")
        else:
            self.mute_btn.setText("🔊")
