import sys
import os
import unittest
import shutil

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.language_manager import LanguageManager
from src.core.settings_manager import SettingsManager

class TestLanguageImplementation(unittest.TestCase):
    def setUp(self):
        self.test_dir = "tests/temp_data"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
            
        # Create dummy language files
        self.lang_dir = os.path.join(self.test_dir, "languages")
        os.makedirs(self.lang_dir)
        
        with open(os.path.join(self.lang_dir, "en.json"), "w") as f:
            f.write('{"hello": "Hello", "world": "World"}')
            
        with open(os.path.join(self.lang_dir, "de.json"), "w") as f:
            f.write('{"hello": "Hallo", "world": "Welt"}')

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_language_manager_loading(self):
        lm = LanguageManager(self.test_dir)
        
        # Test default/initial state
        self.assertEqual(lm.current_language, "en")
        
        # Test loading English
        lm.load_language("en")
        self.assertEqual(lm.translate("hello"), "Hello")
        
        # Test loading German
        lm.load_language("de")
        self.assertEqual(lm.translate("hello"), "Hallo")
        
        # Test missing key
        self.assertEqual(lm.translate("missing"), "missing")
        self.assertEqual(lm.translate("missing", "Default"), "Default")

    def test_settings_manager_integration(self):
        sm = SettingsManager(self.test_dir)
        
        # Test default language
        self.assertEqual(sm.get_language(), "en")
        
        # Test setting language
        sm.set_language("de")
        self.assertEqual(sm.get_language(), "de")
        
        # Verify persistence
        sm2 = SettingsManager(self.test_dir)
        self.assertEqual(sm2.get_language(), "de")

    def test_available_languages(self):
        lm = LanguageManager(self.test_dir)
        langs = lm.get_available_languages()
        self.assertIn("en", langs)
        self.assertIn("de", langs)
        self.assertEqual(len(langs), 2)

if __name__ == "__main__":
    unittest.main()
