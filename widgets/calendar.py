"""
Calendar Widget Module.

Compact calendar view showing upcoming events and birthdays.
Integrates with the Calendar App database to show relevant reminders.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QFont
from apps.calendar.database import get_upcoming_events, init_db
from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme

class CalendarWidget(QFrame):
    """
    A dashboard widget displaying the date and upcoming events.

    Updates automatically every minute.
    """
    def __init__(self):
        """Initializes the CalendarWidget."""
        super().__init__()
        init_db()
        self.res_manager = ResolutionManager()
        
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        
        # Dynamic Size
        width = self.res_manager.scale(250)
        height = self.res_manager.scale(120)
        self.setFixedSize(width, height)
        
        self.setStyleSheet(f"""
            CalendarWidget {{
                background-color: {Theme.GLASS_COLOR};
                border-radius: {self.res_manager.scale(15)}px;
                border: {Theme.GLASS_BORDER};
            }}
        """)
        
        layout = QVBoxLayout(self)
        margin_x = self.res_manager.scale(15)
        margin_y = self.res_manager.scale(10)
        layout.setContentsMargins(margin_x, margin_y, margin_x, margin_y)
        
        # Date Display
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        date_font_size = self.res_manager.scale(24)
        self.date_label.setStyleSheet(f"color: {Theme.TEXT_PRIMARY}; font-size: {date_font_size}px; font-weight: bold;")
        layout.addWidget(self.date_label)
        
        # Events Display
        self.events_label = QLabel("No upcoming events")
        self.events_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.events_label.setWordWrap(True)
        events_font_size = self.res_manager.scale(14)
        self.events_label.setStyleSheet(f"color: #ddd; font-size: {events_font_size}px;")
        layout.addWidget(self.events_label)
        
        # Timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_widget)
        self.timer.start(60000) # Update every minute
        
        self.update_widget()

    def update_widget(self):
        # Update Date
        now = QDate.currentDate()
        self.date_label.setText(now.toString("ddd, MMM d"))
        
        # Update Events
        upcoming = get_upcoming_events(days_ahead=7)
        
        if not upcoming:
            self.events_label.setText("No upcoming events")
            events_font_size = self.res_manager.scale(14)
            self.events_label.setStyleSheet(f"color: #888; font-size: {events_font_size}px;")
        else:
            # Show top 1-2 events to fit
            text_lines = []
            
            icons = {
                "Birthday": "🎂",
                "Meeting": "🤝",
                "Holiday": "🎉",
                "General": "📅"
            }
            
            for e in upcoming[:2]:
                days = e['days_until']
                cat = e.get("category", "General")
                icon = icons.get(cat, "📅")
                
                if days == 0:
                    prefix = f"{icon} Today:"
                elif days == 1:
                    prefix = f"{icon} Tomorrow:"
                else:
                    prefix = f"{icon} In {days}d:"
                
                text_lines.append(f"{prefix} {e['title']}")
            
            if len(upcoming) > 2:
                text_lines.append(f"+{len(upcoming)-2} more")
                
            self.events_label.setText("\n".join(text_lines))
            events_font_size = self.res_manager.scale(14)
            self.events_label.setStyleSheet(f"color: #FF9800; font-size: {events_font_size}px; font-weight: bold;")

