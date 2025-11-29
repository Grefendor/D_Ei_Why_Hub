import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.settings_manager import SettingsManager
from src.ui.resolution_manager import ResolutionManager
from PySide6.QtWidgets import QApplication

def test_resolution_settings():
    print("Testing Resolution Settings...")
    
    # 1. Test SettingsManager
    sm = SettingsManager()
    original_res = sm.get_resolution()
    print(f"Original Resolution: {original_res}")
    
    sm.set_resolution("1280x720")
    assert sm.get_resolution() == "1280x720"
    print("SettingsManager: Set/Get works.")
    
    # 2. Test ResolutionManager
    app = QApplication(sys.argv) # Needed for QScreen
    rm = ResolutionManager()
    
    # Test Auto (should be default)
    rm.update_screen_info("auto")
    print(f"Auto Scale Factor: {rm.scale_factor}")
    
    # Test Override
    rm.update_screen_info("1280x720") # Base is 1920x1080
    # 1280/1920 = 0.666...
    # 720/1080 = 0.666...
    expected_scale = 1280 / 1920
    print(f"Override Scale Factor (1280x720): {rm.scale_factor}")
    
    assert abs(rm.scale_factor - expected_scale) < 0.01
    print("ResolutionManager: Override works.")
    
    # Restore settings
    sm.set_resolution(original_res)
    print("Settings restored.")
    
    print("Verification Passed!")

if __name__ == "__main__":
    test_resolution_settings()
