"""
Screensaver UI Module.

Displays the screensaver window with cycling images.
"""

import os
import random
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, Signal, QEvent
from PySide6.QtGui import QPixmap, QColor, QPalette

class ScreensaverWindow(QWidget):
    """
    The screensaver window that covers the entire screen.
    """
    activity_detected = Signal()

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        
        # Window setup

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        # Explicitly set geometry to primary screen
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Black background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
        self.setPalette(palette)
        
        # Image Label
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)
        
        # Timer for cycling images
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)
        
        self.image_files = []
        self.current_image_index = 0

    def start(self):
        """Starts the screensaver."""
        self.load_settings()
        self.load_images()
        
        # Ensure geometry is correct before showing
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
            
        self.showFullScreen()
        
        if self.image_files:
            self.next_image()
            self.timer.start()
        else:
            # No images, just black screen
            self.image_label.clear()
            self.timer.stop()

    def stop(self):
        """Stops the screensaver."""
        self.timer.stop()
        self.hide()

    def load_settings(self):
        """Loads settings for slide duration."""
        settings = self.settings_manager.get_screensaver_settings()
        duration_sec = settings.get("slide_duration", 10)
        self.timer.setInterval(duration_sec * 1000)
        self.image_path = settings.get("image_path", "data/screensaver_images")

    def load_images(self):
        """Scans the image directory for valid images."""
        self.image_files = []
        if os.path.exists(self.image_path):
            valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif')
            for f in os.listdir(self.image_path):
                if f.lower().endswith(valid_extensions):
                    self.image_files.append(os.path.join(self.image_path, f))
            
            # Shuffle for variety
            random.shuffle(self.image_files)

    def next_image(self):
        """
        Advances to the next image in the list.
        If the list is empty, this does nothing.
        """
        if not self.image_files:
            return

        image_path = self.image_files[self.current_image_index]
        pixmap = QPixmap(image_path)
        
        if not pixmap.isNull():
            # Scale the image to fit the screen, maintaining aspect ratio.
            # SmoothTransformation ensures it doesn't look pixelated.
            scaled_pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)

    def mouseMoveEvent(self, event):
        """Detects mouse movement and signals that the user is back."""
        self.activity_detected.emit()
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """Detects mouse clicks and signals that the user is back."""
        self.activity_detected.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """Detects key presses and signals that the user is back."""
        self.activity_detected.emit()
        super().keyPressEvent(event)
