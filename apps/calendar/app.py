from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QCalendarWidget, QDialog, QLineEdit, 
                             QComboBox, QMessageBox, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QBrush

from .database import init_db, add_event, get_all_events, delete_event
from src.ui.resolution_manager import ResolutionManager
from src.ui.theme import Theme

"""
Calendar Application Module.

This module handles the Calendar app. It lets you manage events, birthdays, 
and reminders.
"""

class CalendarApp(QWidget):
    """
    The main view for the Calendar.

    It shows the calendar grid and your list of events. You can add, view, 
    and delete events from here.
    """
    def __init__(self, language_manager=None):
        """Sets up the calendar app, connects to the database, and builds the UI."""
        super().__init__()
        self.language_manager = language_manager
        init_db()
        self.res_manager = ResolutionManager()
        self.setup_ui()
        
        title = "Calendar"
        if self.language_manager:
            title = self.language_manager.translate("calendar", "Calendar")
        self.setWindowTitle(title)
        
        self.refresh_data()

    def setup_ui(self):
        """
        Builds the UI, including the calendar widget, event list, and buttons.
        """
        layout = QHBoxLayout(self)
        layout.setSpacing(self.res_manager.scale(20))
        
        # Left Side: Calendar
        left_layout = QVBoxLayout()
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        
        # Scaled Calendar Styles
        font_size = self.res_manager.scale(18)
        nav_size = self.res_manager.scale(16)
        icon_size = self.res_manager.scale(24)
        
        self.calendar.setStyleSheet(f"""
            QCalendarWidget QAbstractItemView:enabled {{
                font-size: {font_size}px;
                color: {Theme.TEXT_PRIMARY};
                background-color: #333;
                selection-background-color: #666;
                selection-color: white;
            }}
            QCalendarWidget QWidget {{
                alternate-background-color: #444;
            }}
            QCalendarWidget QToolButton {{
                color: white;
                font-size: {nav_size}px;
                icon-size: {icon_size}px;
                background-color: #555;
            }}
            QCalendarWidget QMenu {{
                color: white;
                background-color: #333;
            }}
            QCalendarWidget QSpinBox {{
                color: white;
                background-color: #333;
                selection-background-color: #555;
            }}
        """)
        left_layout.addWidget(self.calendar)
        layout.addLayout(left_layout, stretch=2)
        
        # Right Side: Controls & List
        right_layout = QVBoxLayout()
        right_layout.setSpacing(self.res_manager.scale(10))
        
        # Title
        self.title_label = QLabel()
        title_font = self.res_manager.scale(24)
        self.title_label.setStyleSheet(f"font-size: {title_font}px; font-weight: bold; margin-bottom: {self.res_manager.scale(10)}px; color: {Theme.TEXT_PRIMARY};")
        right_layout.addWidget(self.title_label)
        
        # Add Button
        self.add_btn = QPushButton()
        self.add_btn.setMinimumHeight(self.res_manager.scale(60))
        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50; 
                color: white; 
                font-size: {self.res_manager.scale(18)}px; 
                border-radius: {self.res_manager.scale(10)}px;
                padding: {self.res_manager.scale(10)}px;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        self.add_btn.clicked.connect(self.open_add_dialog)
        right_layout.addWidget(self.add_btn)
        
        # Event List
        self.event_list = QListWidget()
        list_font = self.res_manager.scale(16)
        self.event_list.setStyleSheet(f"""
            QListWidget {{
                background-color: #333;
                border-radius: {self.res_manager.scale(8)}px;
                padding: {self.res_manager.scale(5)}px;
                font-size: {list_font}px;
                color: {Theme.TEXT_PRIMARY};
            }}
            QListWidget::item {{
                padding: {self.res_manager.scale(5)}px;
                border-bottom: 1px solid #444;
            }}
        """)
        right_layout.addWidget(self.event_list)
        
        # Delete Button
        self.del_btn = QPushButton()
        self.del_btn.setMinimumHeight(self.res_manager.scale(50))
        self.del_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f44336; 
                color: white; 
                border-radius: {self.res_manager.scale(5)}px;
                padding: {self.res_manager.scale(8)}px;
                font-size: {self.res_manager.scale(16)}px;
            }}
            QPushButton:hover {{
                background-color: #d32f2f;
            }}
        """)
        self.del_btn.clicked.connect(self.delete_selected)
        right_layout.addWidget(self.del_btn)

        layout.addLayout(right_layout, stretch=1)
        
        self.update_texts()
        if self.language_manager:
            self.language_manager.language_changed.connect(self.update_texts)

    def update_texts(self, lang_code=None):
        """Updates UI texts based on current language."""
        title = "Calendar"
        events_title = "Events"
        add_text = "+ Add Event"
        del_text = "Delete Selected"
        
        if self.language_manager:
            title = self.language_manager.translate("calendar", "Calendar")
            events_title = self.language_manager.translate("events", "Events")
            add_text = self.language_manager.translate("add_event", "+ Add Event")
            del_text = self.language_manager.translate("delete_selected", "Delete Selected")
            
        self.setWindowTitle(title)
        self.title_label.setText(events_title)
        self.add_btn.setText(add_text)
        self.del_btn.setText(del_text)

    def refresh_data(self):
        """
        Reloads events from the database and updates the UI.
        """
        self.events = get_all_events()
        self.update_calendar_highlights()
        self.update_list()

    def update_calendar_highlights(self):
        """
        Colors dates on the calendar that have events.
        """
        colors = {
            "Birthday": "#FF9800", # Orange
            "Meeting": "#2196F3",  # Blue
            "Holiday": "#4CAF50",  # Green
            "General": "#9E9E9E"   # Grey
        }
        
        current_year = QDate.currentDate().year()
        years_to_highlight = [current_year - 1, current_year, current_year + 1]
        
        for e in self.events:
            cat = e.get("category", "General")
            color_code = colors.get(cat, "#9E9E9E")
            
            fmt = QTextCharFormat()
            fmt.setBackground(QBrush(QColor(color_code)))
            fmt.setForeground(QBrush(QColor("black")))
            
            for year in years_to_highlight:
                try:
                    date = QDate(year, e['month'], e['day'])
                    if date.isValid():
                        self.calendar.setDateTextFormat(date, fmt)
                except:
                    pass

    def update_list(self):
        """
        Refreshes the list of events on the right side.
        """
        self.event_list.clear()
        sorted_events = sorted(self.events, key=lambda x: (x['month'], x['day']))
        
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        icons = {
            "Birthday": "🎂",
            "Meeting": "🤝",
            "Holiday": "🎉",
            "General": "📅"
        }
        
        for e in sorted_events:
            month_str = months[e['month'] - 1]
            cat = e.get("category", "General")
            icon = icons.get(cat, "📅")
            
            text = f"{e['day']}. {month_str} - {icon} {e['title']}"
            if e['year']:
                text += f" ({e['year']})"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, e['id'])
            self.event_list.addItem(item)

    def open_add_dialog(self):
        """
        Shows the dialog for adding a new event.
        """
        dialog = AddEventDialog(self, self.language_manager)
        if dialog.exec():
            self.refresh_data()

    def delete_selected(self):
        """
        Deletes the event you selected, but asks for confirmation first.
        """
        row = self.event_list.currentRow()
        if row >= 0:
            item = self.event_list.item(row)
            e_id = item.data(Qt.ItemDataRole.UserRole)
            
            title = "Confirm Delete"
            msg = "Are you sure you want to delete this event?"
            if self.language_manager:
                title = self.language_manager.translate("confirm_delete", title)
                msg = self.language_manager.translate("delete_event_confirm", msg)
                
            confirm = QMessageBox.question(self, title, msg,
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                delete_event(e_id)
                self.refresh_data()

class AddEventDialog(QDialog):
    """
    A popup dialog for creating a new event.
    """
    def __init__(self, parent=None, language_manager=None):
        """Sets up the dialog."""
        super().__init__(parent)
        self.language_manager = language_manager
        self.res_manager = ResolutionManager()
        
        title = "Add Event"
        if self.language_manager:
            title = self.language_manager.translate("add_event", title).replace("+ ", "") # Remove + for dialog title
            
        self.setWindowTitle(title)
        
        # Dynamic Size
        width = self.res_manager.scale(400)
        height = self.res_manager.scale(450) # Increased height
        self.setFixedSize(width, height)
        
        self.setStyleSheet(f"background-color: #2b2b2b; color: {Theme.TEXT_PRIMARY}; font-size: {self.res_manager.scale(16)}px;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(self.res_manager.scale(15))
        
        layout.setSpacing(self.res_manager.scale(15))
        
        lbl_title = "Title:"
        if self.language_manager:
            lbl_title = self.language_manager.translate("title", lbl_title) + ":"
        layout.addWidget(QLabel(lbl_title))
        self.title_input = QLineEdit()
        self.title_input.setStyleSheet(f"padding: {self.res_manager.scale(5)}px;")
        layout.addWidget(self.title_input)
        
        layout.addWidget(self.title_input)
        
        lbl_cat = "Category:"
        if self.language_manager:
            lbl_cat = self.language_manager.translate("category", lbl_cat) + ":"
        layout.addWidget(QLabel(lbl_cat))
        self.cat_input = QComboBox()
        self.cat_input.addItems(["General", "Birthday", "Meeting", "Holiday"])
        self.cat_input.setStyleSheet(f"padding: {self.res_manager.scale(5)}px;")
        layout.addWidget(self.cat_input)
        
        self.cat_input.setStyleSheet(f"padding: {self.res_manager.scale(5)}px;")
        layout.addWidget(self.cat_input)
        
        lbl_day = "Day:"
        if self.language_manager:
            lbl_day = self.language_manager.translate("day", lbl_day) + ":"
        layout.addWidget(QLabel(lbl_day))
        self.day_input = QComboBox()
        self.day_input.addItems([str(i) for i in range(1, 32)])
        layout.addWidget(self.day_input)
        
        self.day_input.addItems([str(i) for i in range(1, 32)])
        layout.addWidget(self.day_input)
        
        lbl_month = "Month:"
        if self.language_manager:
            lbl_month = self.language_manager.translate("month", lbl_month) + ":"
        layout.addWidget(QLabel(lbl_month))
        self.month_input = QComboBox()
        months = ["January", "February", "March", "April", "May", "June", 
                  "July", "August", "September", "October", "November", "December"]
        self.month_input.addItems(months)
        layout.addWidget(self.month_input)
        
        self.month_input.addItems(months)
        layout.addWidget(self.month_input)
        
        lbl_year = "Year (Optional):"
        if self.language_manager:
            lbl_year = self.language_manager.translate("year", lbl_year) + ":"
        layout.addWidget(QLabel(lbl_year))
        self.year_input = QLineEdit()
        self.year_input.setPlaceholderText("YYYY")
        layout.addWidget(self.year_input)
        
        self.year_input.setPlaceholderText("YYYY")
        layout.addWidget(self.year_input)
        
        save_text = "Save"
        if self.language_manager:
            save_text = self.language_manager.translate("save_btn", save_text)
        save_btn = QPushButton(save_text)
        save_btn.setMinimumHeight(self.res_manager.scale(50))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #4CAF50; 
                color: white; 
                padding: {self.res_manager.scale(8)}px; 
                margin-top: {self.res_manager.scale(10)}px;
                border-radius: {self.res_manager.scale(5)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #45a049;
            }}
        """)
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

    def save(self):
        """
        Checks if everything is okay and saves the event.
        """
        title = self.title_input.text().strip()
        if not title:
            msg = "Title is required"
            if self.language_manager:
                msg = self.language_manager.translate("title_required", msg)
            QMessageBox.warning(self, self.language_manager.translate("error", "Error") if self.language_manager else "Error", msg)
            return
            
        category = self.cat_input.currentText()
        day = int(self.day_input.currentText())
        month = self.month_input.currentIndex() + 1
        
        year_str = self.year_input.text().strip()
        year = int(year_str) if year_str.isdigit() else None
        
        add_event(title, day, month, year, category)
        self.accept()

