import json
import os
from PySide6.QtCore import QObject, Signal

class LanguageManager(QObject):
    """
    Handles the app's language and translations.
    """
    language_changed = Signal(str)

    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = root_dir
        self.languages_dir = os.path.join(root_dir, "languages")
        self.current_language = "en"
        self.translations = {}
        
        # Ensure languages directory exists
        if not os.path.exists(self.languages_dir):
            os.makedirs(self.languages_dir)

    def load_language(self, lang_code):
        """
        Loads the translation file for the chosen language.
        """
        self.current_language = lang_code
        file_path = os.path.join(self.languages_dir, f"{lang_code}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
            except Exception as e:
                print(f"Error loading language {lang_code}: {e}")
                self.translations = {}
        else:
            print(f"Language file not found: {file_path}")
            self.translations = {}
            
        self.language_changed.emit(lang_code)

    def translate(self, key, default=None):
        """
        Gets the translated text for a key.
        """
        return self.translations.get(key, default if default is not None else key)

    def get_available_languages(self):
        """
        Finds all the languages we have files for.
        """
        if not os.path.exists(self.languages_dir):
            return ["en"]
            
        langs = []
        for filename in os.listdir(self.languages_dir):
            if filename.endswith(".json"):
                langs.append(filename[:-5])
        return sorted(langs)
