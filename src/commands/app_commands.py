"""
Application commands for Yuki AI
"""

import os
import subprocess
from typing import Dict, List, Optional

import sys
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
utils_path = current_dir.parent / "utils"
sys.path.insert(0, str(utils_path))

from utils.config import config
from utils.logger import logger
from utils.helpers import open_application, is_macos, is_windows


class AppCommands:
    """Handle application opening commands"""
    
    def __init__(self):
        self.applications = config.get_applications()
        self.app_aliases = self._get_app_aliases()
    
    def process_command(self, command: str) -> str:
        """Process application opening commands"""
        command_lower = command.lower()
        
        # Check for specific application patterns
        for app_name, app_path in self.applications.items():
            if self._matches_app(command_lower, app_name):
                return self._open_application(app_name, app_path)
        
        # Check for aliases
        for alias, app_name in self.app_aliases.items():
            if alias in command_lower:
                app_path = self.applications.get(app_name)
                if app_path:
                    return self._open_application(app_name, app_path)
        
        # Check for common application patterns
        return self._handle_common_apps(command)
    
    def _matches_app(self, command: str, app_name: str) -> bool:
        """Check if command matches an application"""
        patterns = [
            f"เปิดแอป {app_name}",
            f"open app {app_name}",
            f"เปิดแอปพลิเคชัน {app_name}",
            f"open application {app_name}",
            f"เปิดแอป {app_name.lower()}",
            f"open app {app_name.lower()}",
            f"เปิดแอปพลิเคชัน {app_name.lower()}",
            f"เปิด application {app_name.lower()}",
            f"open application {app_name.lower()}"
        ]
        return any(pattern in command for pattern in patterns)
    
    def _open_application(self, app_name: str, app_path: str) -> str:
        """Open an application"""
        try:
            if os.path.exists(app_path):
                subprocess.Popen([app_path])
                return f"เปิด {app_name} แล้วค่ะ"
            else:
                # Try alternative methods
                return self._try_alternative_open(app_name)
        except Exception as e:
            logger.error(f"Error opening {app_name}: {e}")
            return f"เกิดข้อผิดพลาดในการเปิด {app_name} ค่ะ"
    
    def _try_alternative_open(self, app_name: str) -> str:
        """Try alternative methods to open application"""
        try:
            if is_macos():
                # Try using 'open' command for .app bundles
                app_bundle = f"/Applications/{app_name}.app"
                if os.path.exists(app_bundle):
                    subprocess.run(["open", app_bundle])
                    return f"เปิด {app_name} แล้วค่ะ"
                
                # Try with spaces in name
                app_bundle = f"/Applications/{app_name.replace(' ', '')}.app"
                if os.path.exists(app_bundle):
                    subprocess.run(["open", app_bundle])
                    return f"เปิด {app_name} แล้วค่ะ"
            
            elif is_windows():
                # Try common Windows paths
                common_paths = [
                    f"C:\\Program Files\\{app_name}\\{app_name}.exe",
                    f"C:\\Program Files (x86)\\{app_name}\\{app_name}.exe",
                    f"C:\\Users\\{os.getenv('USERNAME')}\\AppData\\Local\\Programs\\{app_name}\\{app_name}.exe"
                ]
                
                for path in common_paths:
                    if os.path.exists(path):
                        subprocess.Popen([path])
                        return f"เปิด {app_name} แล้วค่ะ"
            
            return f"ไม่พบ {app_name} ในระบบค่ะ"
            
        except Exception as e:
            logger.error(f"Error in alternative open for {app_name}: {e}")
            return f"ไม่สามารถเปิด {app_name} ได้ค่ะ"
    
    def _handle_common_apps(self, command: str) -> str:
        """Handle common application patterns"""
        common_apps = {
            "vscode": ["vscode", "vs code", "visual studio code", "code editor"],
            "chrome": ["chrome", "google chrome", "browser"],
            "safari": ["safari", "apple browser"],
            "firefox": ["firefox", "mozilla"],
            "terminal": ["terminal", "command line", "cmd"],
            "calculator": ["calculator", "calc", "เครื่องคิดเลข"],
            "calendar": ["calendar", "ปฏิทิน"],
            "mail": ["mail", "email", "อีเมล"],
            "spotify": ["spotify", "music player", "เพลง"],
            "discord": ["discord", "chat"],
            "slack": ["slack", "team chat"],
            "zoom": ["zoom", "video call", "meeting"],
            "teams": ["teams", "microsoft teams"],
            "photoshop": ["photoshop", "adobe photoshop", "photo editor"],
            "premiere": ["premiere", "adobe premiere", "video editor"],
            "illustrator": ["illustrator", "adobe illustrator", "vector editor"],
            "figma": ["figma", "design tool"],
            "canva": ["canva", "design"],
            "steam": ["steam", "game launcher"],
            "minecraft": ["minecraft", "game"],
            "obs": ["obs", "streaming", "recording"],
            "vlc": ["vlc", "media player", "video player"],
            "itunes": ["itunes", "music", "apple music"]
        }
        
        for app_name, aliases in common_apps.items():
            if any(alias in command.lower() for alias in aliases):
                app_path = self.applications.get(app_name)
                if app_path:
                    return self._open_application(app_name, app_path)
                else:
                    return self._try_alternative_open(app_name)
        
        return "ไม่เข้าใจคำสั่งเปิดแอปพลิเคชันค่ะ กรุณาลองใหม่อีกครั้ง"
    
    def _get_app_aliases(self) -> Dict[str, str]:
        """Get application aliases"""
        return {
            "code": "vscode",
            "editor": "vscode",
            "browser": "chrome",
            "web browser": "chrome",
            "music": "spotify",
            "player": "spotify",
            "chat": "discord",
            "messaging": "discord",
            "video": "vlc",
            "media": "vlc",
            "photo": "photoshop",
            "image": "photoshop",
            "video editor": "premiere",
            "design": "figma",
            "game": "steam",
            "stream": "obs",
            "record": "obs"
        }
    
    def list_available_apps(self) -> List[str]:
        """List available applications"""
        return list(self.applications.keys())
    
    def add_application(self, app_name: str, app_path: str) -> bool:
        """Add a new application to the configuration"""
        try:
            self.applications[app_name] = app_path
            # Update config
            config.set(f"applications.{app_name}", app_path)
            logger.info(f"Added application: {app_name} -> {app_path}")
            return True
        except Exception as e:
            logger.error(f"Error adding application {app_name}: {e}")
            return False
    
    def remove_application(self, app_name: str) -> bool:
        """Remove an application from the configuration"""
        try:
            if app_name in self.applications:
                del self.applications[app_name]
                # Update config
                config.set(f"applications.{app_name}", None)
                logger.info(f"Removed application: {app_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing application {app_name}: {e}")
            return False
