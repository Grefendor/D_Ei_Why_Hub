import platform
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VolumeManager:
    """
    Manages system volume control across different platforms (Windows, Linux, macOS).
    
    This class provides a unified interface to get, set, mute, and unmute the system volume.
    It uses 'pycaw' for Windows and standard command-line tools for Linux ('amixer') and macOS ('osascript').
    """

    def __init__(self):
        """
        Initializes the VolumeManager and determines the current operating system.
        """
        self.os_name = platform.system()
        self.volume_interface = None
        
        if self.os_name == "Windows":
            try:
                from pycaw.pycaw import AudioUtilities
                
                devices = AudioUtilities.GetSpeakers()
                self.volume_interface = devices.EndpointVolume
            except ImportError:
                logger.error("pycaw or comtypes not found. Windows volume control will not work.")
            except Exception as e:
                logger.error(f"Failed to initialize Windows volume control: {e}")

    def get_volume(self) -> int:
        """
        Gets the current system volume level.

        Returns:
            int: The volume level between 0 and 100. Returns 0 if retrieval fails.
        """
        try:
            if self.os_name == "Windows":
                if self.volume_interface:
                    # pycaw returns scalar volume (0.0 to 1.0)
                    return int(round(self.volume_interface.GetMasterVolumeLevelScalar() * 100))
            
            elif self.os_name == "Linux":
                # Using amixer to get master volume
                result = subprocess.run(["amixer", "get", "Master"], capture_output=True, text=True)
                if result.returncode == 0:
                    # Parse output to find percentage, e.g., [50%]
                    import re
                    match = re.search(r"\[(\d+)%\]", result.stdout)
                    if match:
                        return int(match.group(1))
            
            elif self.os_name == "Darwin": # macOS
                result = subprocess.run(["osascript", "-e", "output volume of (get volume settings)"], capture_output=True, text=True)
                if result.returncode == 0:
                    return int(result.stdout.strip())
                    
        except Exception as e:
            logger.error(f"Error getting volume: {e}")
            
        return 0

    def set_volume(self, level: int):
        """
        Sets the system volume level.

        Args:
            level (int): The desired volume level between 0 and 100.
        """
        # Clamp level between 0 and 100
        level = max(0, min(100, level))
        
        try:
            if self.os_name == "Windows":
                if self.volume_interface:
                    self.volume_interface.SetMasterVolumeLevelScalar(level / 100.0, None)
            
            elif self.os_name == "Linux":
                subprocess.run(["amixer", "set", "Master", f"{level}%"])
            
            elif self.os_name == "Darwin": # macOS
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
                
        except Exception as e:
            logger.error(f"Error setting volume: {e}")

    def is_muted(self) -> bool:
        """
        Checks if the system is currently muted.

        Returns:
            bool: True if muted, False otherwise.
        """
        try:
            if self.os_name == "Windows":
                if self.volume_interface:
                    return bool(self.volume_interface.GetMute())
            
            elif self.os_name == "Linux":
                result = subprocess.run(["amixer", "get", "Master"], capture_output=True, text=True)
                if result.returncode == 0:
                    return "[off]" in result.stdout
            
            elif self.os_name == "Darwin": # macOS
                result = subprocess.run(["osascript", "-e", "output muted of (get volume settings)"], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip() == "true"
                    
        except Exception as e:
            logger.error(f"Error checking mute status: {e}")
            
        return False

    def mute(self):
        """Mutes the system volume."""
        self._set_mute(True)

    def unmute(self):
        """Unmutes the system volume."""
        self._set_mute(False)

    def toggle_mute(self):
        """Toggles the system mute state."""
        self._set_mute(not self.is_muted())

    def _set_mute(self, mute: bool):
        """
        Internal method to set the mute state.

        Args:
            mute (bool): True to mute, False to unmute.
        """
        try:
            if self.os_name == "Windows":
                if self.volume_interface:
                    self.volume_interface.SetMute(mute, None)
            
            elif self.os_name == "Linux":
                state = "mute" if mute else "unmute"
                subprocess.run(["amixer", "set", "Master", state])
            
            elif self.os_name == "Darwin": # macOS
                state = "true" if mute else "false"
                subprocess.run(["osascript", "-e", f"set volume output muted {state}"])
                
        except Exception as e:
            logger.error(f"Error setting mute state: {e}")
