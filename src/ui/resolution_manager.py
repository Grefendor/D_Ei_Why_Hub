"""
Resolution Manager Module.

This module provides the `ResolutionManager` class, which handles UI scaling
based on the user's screen resolution. It implements a singleton pattern to
ensure consistent scaling across the application.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QScreen

class ResolutionManager:
    """
    Singleton service for handling DPI-aware UI scaling across different screen resolutions.

    Calculates a uniform scaling factor based on a reference 1080p resolution to ensure 
    consistent visual sizing on various displays.

    Attributes:
        base_width (int): The reference width for scaling (default: 1920).
        base_height (int): The reference height for scaling (default: 1080).
        scale_factor (float): The calculated scaling multiplier.
    """
    _instance = None

    def __new__(cls):
        """Ensures only one instance of ResolutionManager exists (Singleton)."""
        if cls._instance is None:
            cls._instance = super(ResolutionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initializes the ResolutionManager and calculates the initial scale factor."""
        if self._initialized:
            return
        
        self.base_width = 1920
        self.base_height = 1080
        self.scale_factor = 1.0
        self.update_screen_info()
        self._initialized = True

    def update_screen_info(self, resolution_setting: str = "auto"):
        """
        Updates the screen resolution information and recalculates the scale factor.

        Args:
            resolution_setting (str): The resolution setting ("auto" or "WxH").
        """
        target_width = 1920
        target_height = 1080
        
        # Parse resolution setting
        if resolution_setting and resolution_setting.lower() != "auto":
            try:
                parts = resolution_setting.lower().split('x')
                if len(parts) == 2:
                    target_width = int(parts[0])
                    target_height = int(parts[1])
                    
                    # Use these as the "current" dimensions for scaling purposes
                    self.current_width = target_width
                    self.current_height = target_height
                    
                    # Calculate scale factor
                    width_ratio = self.current_width / self.base_width
                    height_ratio = self.current_height / self.base_height
                    self.scale_factor = min(width_ratio, height_ratio)
                    return
            except ValueError:
                print(f"Invalid resolution setting: {resolution_setting}, falling back to auto.")

        # Auto-detect
        screen = QApplication.primaryScreen()
        if screen:
            size = screen.size()
            self.current_width = size.width()
            self.current_height = size.height()
            
            width_ratio = self.current_width / self.base_width
            height_ratio = self.current_height / self.base_height
            
            self.scale_factor = min(width_ratio, height_ratio)
        else:
            self.current_width = 1920
            self.current_height = 1080
            self.scale_factor = 1.0

    def scale(self, value: int) -> int:
        """
        Scales a numeric value based on the current resolution.

        Args:
            value (int): The base value to scale.

        Returns:
            int: The scaled value.
        """
        return int(value * self.scale_factor)

    def font_size(self, size: int) -> str:
        """
        Returns a CSS font size string scaled to the current resolution.

        Args:
            size (int): The base font size in pixels.

        Returns:
            str: The scaled font size string (e.g., "18px").
        """
        return f"{self.scale(size)}px"
