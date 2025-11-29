
import sys
import os
import json
import unittest
from PySide6.QtWidgets import QApplication

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.language_manager import LanguageManager
from apps.calendar.app import CalendarApp
from apps.task_board.app import TaskBoardApp
from apps.pantry_manager.ui_qt import LebensmittelManagerApp

class TestI18n(unittest.TestCase):
    def setUp(self):
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()
            
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.lang_manager = LanguageManager(root_dir)
        self.lang_manager.load_language("de")

    def test_language_loading(self):
        """Test if German language pack loads correctly."""
        self.assertEqual(self.lang_manager.current_language, "de")
        self.assertEqual(self.lang_manager.translate("pantry_manager", ""), "Vorratsmanager Pro")
        self.assertEqual(self.lang_manager.translate("add_entry", ""), "Eintrag hinzufügen")

    def test_pantry_manager_translation(self):
        """Test if Pantry Manager uses translations."""
        app = LebensmittelManagerApp(language_manager=self.lang_manager)
        self.assertEqual(app.windowTitle(), "Vorratsmanager Pro")
        # Check specific buttons if possible, or just ensure no crash
        
    def test_calendar_translation(self):
        """Test if Calendar App uses translations."""
        app = CalendarApp(language_manager=self.lang_manager)
        self.assertEqual(app.windowTitle(), "Kalender")

    def test_task_board_translation(self):
        """Test if Task Board uses translations."""
        app = TaskBoardApp(language_manager=self.lang_manager)
        self.assertEqual(app.windowTitle(), "Aufgaben")

    def test_dynamic_switching(self):
        """Test if apps update when language changes."""
        # Start with English
        self.lang_manager.load_language("en")
        
        cal = CalendarApp(language_manager=self.lang_manager)
        task = TaskBoardApp(language_manager=self.lang_manager)
        pantry = LebensmittelManagerApp(language_manager=self.lang_manager)
        
        self.assertEqual(cal.windowTitle(), "Calendar")
        self.assertEqual(task.windowTitle(), "Task Board")
        self.assertEqual(pantry.windowTitle(), "Pantry Manager Pro") # Default English key
        
        # Switch to German
        self.lang_manager.load_language("de")
        
        self.assertEqual(cal.windowTitle(), "Kalender")
        self.assertEqual(task.windowTitle(), "Aufgaben")
        self.assertEqual(pantry.windowTitle(), "Vorratsmanager Pro")

if __name__ == '__main__':
    unittest.main()
