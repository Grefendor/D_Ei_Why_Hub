from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QGraphicsView, QGraphicsScene, QGraphicsPathItem, 
                             QMessageBox, QFrame, QGraphicsPixmapItem)
from PySide6.QtCore import Qt, QPointF, QRectF, QTimer
from PySide6.QtGui import QPen, QPainter, QPainterPath, QColor, QBrush, QPixmap, QImage
import os
import threading

from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme

"""
Whiteboard Application Module.

This module provides a digital whiteboard for freehand drawing.
It supports basic tools like a pen and an eraser, allowing users to
quickly jot down notes or sketches.
"""

class WhiteboardApp(QWidget):
    """
    The main view for the Whiteboard application.

    This widget hosts the drawing area and the toolbar for selecting tools
    and clearing the board.
    """
    def __init__(self, language_manager=None):
        """
        Initializes the Whiteboard application.

        Args:
            language_manager (LanguageManager, optional): The manager for handling translations.
        """
        super().__init__()
        self.language_manager = language_manager
        self.res_manager = ResolutionManager()
        
        # Drawing state
        self.current_tool = 'pen'  # 'pen' or 'eraser'
        self.pen_color = Qt.white
        self.pen_width = 3
        self.eraser_width = 20
        self.last_point = None
        self.is_drawing = False
        
        # Persistence
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.save_file = os.path.join(self.data_dir, "whiteboard.png")
        
        # Auto-save timer for debouncing
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(2000)  # 2 seconds debounce
        self.save_timer.timeout.connect(self.save_canvas)
        
        self.setup_ui()
        self.update_texts()
        self.load_canvas()
        
        if self.language_manager:
            self.language_manager.language_changed.connect(self.update_texts)

    def setup_ui(self):
        """
        Constructs the user interface elements.
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(self.res_manager.scale(10))
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(self.res_manager.scale(10))
        
        # Tool Buttons
        self.pen_btn = self.create_tool_button("Pen", self.select_pen)
        self.eraser_btn = self.create_tool_button("Eraser", self.select_eraser)
        self.clear_btn = self.create_tool_button("Clear", self.confirm_clear)
        
        # Style the clear button differently to indicate a destructive action
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #F44336; 
                color: white; 
                font-size: {self.res_manager.scale(16)}px; 
                border-radius: {self.res_manager.scale(5)}px;
                padding: {self.res_manager.scale(10)}px;
            }}
            QPushButton:hover {{
                background-color: #D32F2F;
            }}
        """)

        toolbar_layout.addWidget(self.pen_btn)
        toolbar_layout.addWidget(self.eraser_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.clear_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Drawing Area
        self.scene = QGraphicsScene(self)
        # Set a fixed large scene rect to prevent auto-centering/shifting while drawing
        self.scene.setSceneRect(0, 0, 5000, 5000)
        
        self.view = DrawingView(self.scene, self)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Set a dark background for the drawing area
        self.view.setStyleSheet("background-color: #1e1e1e; border: 1px solid #444;")
        
        layout.addWidget(self.view)
        
        # Highlight the default tool
        self.update_tool_styles()

    def create_tool_button(self, text, callback):
        """
        Helper to create a standard toolbar button.

        Args:
            text (str): The label text for the button.
            callback (callable): The function to call when clicked.

        Returns:
            QPushButton: The configured button.
        """
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        btn.setFixedSize(self.res_manager.scale(100), self.res_manager.scale(50))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #2196F3; 
                color: white; 
                font-size: {self.res_manager.scale(16)}px; 
                border-radius: {self.res_manager.scale(5)}px;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """)
        return btn

    def update_texts(self, lang_code=None):
        """
        Updates the UI text based on the current language.

        Args:
            lang_code (str, optional): The language code (unused here as we pull from manager).
        """
        title = "Whiteboard"
        pen_text = "Pen"
        eraser_text = "Eraser"
        clear_text = "Clear"
        
        if self.language_manager:
            title = self.language_manager.translate("whiteboard", title)
            pen_text = self.language_manager.translate("pen", pen_text)
            eraser_text = self.language_manager.translate("eraser", eraser_text)
            clear_text = self.language_manager.translate("clear_board", clear_text)
            
        self.setWindowTitle(title)
        self.pen_btn.setText(pen_text)
        self.eraser_btn.setText(eraser_text)
        self.clear_btn.setText(clear_text)

    def select_pen(self):
        """Switches the active tool to the Pen."""
        self.current_tool = 'pen'
        self.update_tool_styles()

    def select_eraser(self):
        """Switches the active tool to the Eraser."""
        self.current_tool = 'eraser'
        self.update_tool_styles()

    def update_tool_styles(self):
        """Updates the visual state of buttons to show which tool is active."""
        active_style = f"""
            QPushButton {{
                background-color: #1565C0; 
                color: white; 
                font-size: {self.res_manager.scale(16)}px; 
                border-radius: {self.res_manager.scale(5)}px;
                border: 2px solid #90CAF9;
            }}
        """
        inactive_style = f"""
            QPushButton {{
                background-color: #2196F3; 
                color: white; 
                font-size: {self.res_manager.scale(16)}px; 
                border-radius: {self.res_manager.scale(5)}px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #1976D2;
            }}
        """
        
        self.pen_btn.setStyleSheet(active_style if self.current_tool == 'pen' else inactive_style)
        self.eraser_btn.setStyleSheet(active_style if self.current_tool == 'eraser' else inactive_style)

    def confirm_clear(self):
        """Prompts the user for confirmation before clearing the board."""
        title = "Clear Board"
        msg = "Are you sure you want to clear the whiteboard?"
        
        if self.language_manager:
            title = self.language_manager.translate("confirm_clear", title)
            msg = self.language_manager.translate("confirm_clear_msg", msg)
            
        reply = QMessageBox.question(
            self, title, msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.scene.clear()
            self.save_canvas()

    def trigger_save(self):
        """
        Restarts the debounce timer for auto-saving.
        """
        self.save_timer.start()

    def save_canvas(self):
        """
        Saves the current state of the canvas to a PNG file in a background thread.
        """
        # Create a pixmap large enough to hold the scene content
        rect = self.scene.sceneRect()
        # Render to QImage in the main thread (GUI operations must be in main thread)
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        
        # Define the saving task
        def save_task(img, path):
            try:
                img.save(path)
            except Exception as e:
                print(f"Error saving whiteboard: {e}")

        # Run in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=save_task, args=(image, self.save_file))
        thread.start()

    def load_canvas(self):
        """
        Loads the saved canvas state from the file.
        """
        if os.path.exists(self.save_file):
            pixmap = QPixmap(self.save_file)
            if not pixmap.isNull():
                self.scene.addPixmap(pixmap)

class DrawingView(QGraphicsView):
    """
    A custom QGraphicsView to handle mouse events for drawing.
    """
    def __init__(self, scene, parent_app):
        super().__init__(scene)
        self.parent_app = parent_app
        self.setMouseTracking(True)
        self.last_point = None

    def mousePressEvent(self, event):
        """Handles the start of a drawing stroke."""
        if event.button() == Qt.LeftButton:
            self.last_point = self.mapToScene(event.pos())
            
            # If it's a single dot click
            self.draw_to(self.last_point)

    def mouseMoveEvent(self, event):
        """Handles the drawing movement."""
        if event.buttons() & Qt.LeftButton and self.last_point:
            new_point = self.mapToScene(event.pos())
            self.draw_to(new_point)
            self.last_point = new_point

    def mouseReleaseEvent(self, event):
        """Handles the end of a drawing stroke."""
        if event.button() == Qt.LeftButton:
            self.last_point = None
            # Trigger auto-save with debounce
            self.parent_app.trigger_save()

    def draw_to(self, point):
        """
        Draws a line from the last point to the new point.

        Args:
            point (QPointF): The target point to draw to.
        """
        if not self.last_point:
            return

        pen = QPen()
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        
        if self.parent_app.current_tool == 'pen':
            pen.setColor(self.parent_app.pen_color)
            pen.setWidth(self.parent_app.pen_width)
            self.scene().addLine(self.last_point.x(), self.last_point.y(), point.x(), point.y(), pen)
            
        elif self.parent_app.current_tool == 'eraser':
            # For eraser, we can just draw with the background color or remove items.
            # Drawing with background color is simpler for a basic whiteboard.
            # Assuming background is #1e1e1e
            pen.setColor(QColor("#1e1e1e"))
            pen.setWidth(self.parent_app.eraser_width)
            self.scene().addLine(self.last_point.x(), self.last_point.y(), point.x(), point.y(), pen)
