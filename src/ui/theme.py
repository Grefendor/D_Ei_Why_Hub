"""
Theme Module.

This module defines the `Theme` class, which serves as a central repository for
application styling constants. It includes color definitions, gradient presets,
and helper methods for generating CSS stylesheets for common UI elements.
"""

class Theme:
    """
    Defines the visual theme and style constants for the application.

    This class contains static properties for colors and utility methods
    to generate Qt stylesheets for consistent UI styling.
    """
    # Colors
    BACKGROUND_COLOR = "#1e1e2e"
    BACKGROUND_GRADIENT = "qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a2e, stop:1 #16213e)"
    
    # Glassmorphism
    GLASS_COLOR = "rgba(255, 255, 255, 0.05)"
    GLASS_BORDER = "1px solid rgba(255, 255, 255, 0.1)"
    GLASS_HOVER = "rgba(255, 255, 255, 0.1)"
    GLASS_PRESSED = "rgba(255, 255, 255, 0.02)"
    
    # Text
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a0a0a0"
    
    # Accents
    ACCENT_COLOR = "#0f3460"
    ACCENT_HOVER = "#1a4b8c"

    @staticmethod
    def get_glass_style(radius=20):
        """
        Generates a CSS stylesheet for a glassmorphism effect.

        Args:
            radius (int): The border radius in pixels.

        Returns:
            str: The CSS stylesheet string.
        """
        return f"""
            background-color: {Theme.GLASS_COLOR};
            border: {Theme.GLASS_BORDER};
            border-radius: {radius}px;
            color: {Theme.TEXT_PRIMARY};
        """

    @staticmethod
    def get_button_style(font_size=18, radius=15):
        """
        Generates a CSS stylesheet for a standard button.

        Args:
            font_size (int): The font size in pixels.
            radius (int): The border radius in pixels.

        Returns:
            str: The CSS stylesheet string.
        """
        return f"""
            QPushButton {{
                background-color: {Theme.GLASS_COLOR};
                border: {Theme.GLASS_BORDER};
                border-radius: {radius}px;
                color: {Theme.TEXT_PRIMARY};
                font-size: {font_size}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {Theme.GLASS_HOVER};
                border: 1px solid rgba(255, 255, 255, 0.3);
            }}
            QPushButton:pressed {{
                background-color: {Theme.GLASS_PRESSED};
            }}
        """
