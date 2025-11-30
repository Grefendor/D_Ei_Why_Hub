import sys
import os
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.volume_manager import VolumeManager

def test_volume_manager():
    print("Testing VolumeManager...")
    vm = VolumeManager()
    
    print(f"OS: {vm.os_name}")
    
    # Test Get Volume
    vol = vm.get_volume()
    print(f"Current Volume: {vol}")
    
    # Test Mute Status
    muted = vm.is_muted()
    print(f"Is Muted: {muted}")
    
    # Test Set Volume (Small change to verify)
    # Be careful not to blast ears, maybe just set to current value
    print(f"Setting volume to {vol} (no change)...")
    vm.set_volume(vol)
    
    # Test Toggle Mute
    print("Toggling mute...")
    vm.toggle_mute()
    print(f"Is Muted after toggle: {vm.is_muted()}")
    time.sleep(1)
    
    print("Toggling mute back...")
    vm.toggle_mute()
    print(f"Is Muted after second toggle: {vm.is_muted()}")
    
    print("VolumeManager Test Complete.")

if __name__ == "__main__":
    test_volume_manager()
