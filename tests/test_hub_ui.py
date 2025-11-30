import pytest
from PySide6.QtWidgets import QStackedWidget
from apps.hub.ui import HubWindow
from apps.hub.components.top_bar import TopBar
from apps.hub.components.dashboard import Dashboard

def test_hub_window_initialization(qapp, mock_settings):
    """
    Test that the HubWindow initializes correctly.
    """
    # We need to patch the SettingsManager used inside HubWindow
    # Since HubWindow instantiates it internally, we might need to mock the class
    # or just let it run with the real one (but using our temp config dir if we can inject it)
    
    # HubWindow hardcodes the config path in __init__. 
    # To test properly without modifying HubWindow again to accept dependency injection (which would be better),
    # we can rely on the fact that it uses src.core.paths.CONFIG_DIR.
    # But we can't easily patch that constant after import.
    
    # For now, let's just instantiate it. It will use the real config dir, which is safe for reading.
    # Writing might be an issue if tests modify settings.
    
    window = HubWindow()
    assert window.windowTitle() == "The Hub" # Default title, might change with i18n
    assert isinstance(window.top_bar, TopBar)
    assert isinstance(window.dashboard, Dashboard)
    assert isinstance(window.stack, QStackedWidget)
    
    window.close()

def test_top_bar_structure(qapp, mock_settings):
    """
    Test TopBar components.
    """
    # We can instantiate TopBar directly with mocks
    from src.core.widget_registry import WidgetRegistry
    from src.core.language_manager import LanguageManager
    from src.ui.resolution_manager import ResolutionManager
    
    # Mocks
    widget_registry = WidgetRegistry("dummy_path")
    language_manager = LanguageManager("dummy_path")
    res_manager = ResolutionManager()
    
    top_bar = TopBar(mock_settings, widget_registry, language_manager, res_manager)
    
    assert top_bar.home_btn is not None
    assert top_bar.settings_btn is not None
    assert top_bar.volume_control is not None
    
    # Test visibility toggling
    top_bar.set_home_visible(True)
    assert not top_bar.home_btn.isHidden()
    assert top_bar.settings_btn.isHidden()
    
    top_bar.set_home_visible(False)
    assert top_bar.home_btn.isHidden()
    assert not top_bar.settings_btn.isHidden()

def test_dashboard_structure(qapp, mock_settings):
    """
    Test Dashboard components.
    """
    from src.core.app_registry import AppRegistry
    from src.core.language_manager import LanguageManager
    from src.ui.resolution_manager import ResolutionManager
    
    app_registry = AppRegistry("dummy_path")
    language_manager = LanguageManager("dummy_path")
    res_manager = ResolutionManager()
    
    dashboard = Dashboard(mock_settings, app_registry, language_manager, res_manager)
    
    assert dashboard.layout is not None
