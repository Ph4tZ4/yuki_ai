"""
Web commands for Yuki AI
"""

import webbrowser
import urllib.parse
from typing import Dict, List, Optional

import sys
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
utils_path = current_dir.parent / "utils"
sys.path.insert(0, str(utils_path))

from utils.config import config
from utils.logger import logger
from utils.helpers import extract_query_from_command, create_search_url


class WebCommands:
    """Handle web-related commands"""
    
    def __init__(self):
        self.web_services = config.get_web_services()
        self.search_engines = {
            "google": "https://www.google.com",
            "youtube": "https://www.youtube.com",
            "bing": "https://www.bing.com",
            "duckduckgo": "https://duckduckgo.com"
        }
    
    def process_command(self, command: str) -> str:
        """Process web-related commands"""
        command_lower = command.lower()
        
        # Check for website opening commands
        for service_name, url in self.web_services.items():
            if self._matches_service(command_lower, service_name):
                return self._open_website(service_name, url)
        
        # Check for search commands
        if self._is_search_command(command_lower):
            return self._handle_search(command)
        
        # Check for specific website patterns
        if self._is_website_pattern(command_lower):
            return self._handle_website_pattern(command)
        
        return "ไม่เข้าใจคำสั่งเว็บค่ะ กรุณาลองใหม่อีกครั้ง"
    
    def _matches_service(self, command: str, service_name: str) -> bool:
        """Check if command matches a web service"""
        patterns = [
            f"เปิดเว็บ {service_name}",
            f"open website {service_name}",
            f"เปิดเว็บไซต์ {service_name}",
            f"open site {service_name}",
            f"เข้าเว็บ {service_name}",
            f"เข้าเว็บไซต์ {service_name}"
        ]
        return any(pattern in command for pattern in patterns)
    
    def _open_website(self, service_name: str, url: str) -> str:
        """Open a website"""
        try:
            webbrowser.open(url)
            return f"เปิด {service_name} แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error opening {service_name}: {e}")
            return f"เกิดข้อผิดพลาดในการเปิด {service_name} ค่ะ"
    
    def _is_search_command(self, command: str) -> bool:
        """Check if command is a search command"""
        search_triggers = [
            "ค้นหา", "search", "เสิร์ช", "หา",
            "google search", "youtube search",
            "ค้นหาใน google", "ค้นหาใน youtube"
        ]
        return any(trigger in command for trigger in search_triggers)
    
    def _handle_search(self, command: str) -> str:
        """Handle search commands"""
        # Extract search query
        search_triggers = ["ค้นหา", "search", "เสิร์ช", "หา"]
        query = extract_query_from_command(command, search_triggers)
        
        if not query:
            return "กรุณาระบุสิ่งที่ต้องการค้นหาค่ะ"
        
        # Determine search engine
        search_engine = self._determine_search_engine(command)
        
        # Create search URL
        search_url = create_search_url(self.search_engines[search_engine], query)
        
        try:
            webbrowser.open(search_url)
            return f"ค้นหา '{query}' ใน {search_engine} แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            return "เกิดข้อผิดพลาดในการค้นหาค่ะ"
    
    def _determine_search_engine(self, command: str) -> str:
        """Determine which search engine to use"""
        if "youtube" in command.lower():
            return "youtube"
        elif "bing" in command.lower():
            return "bing"
        elif "duckduckgo" in command.lower():
            return "duckduckgo"
        else:
            return "google"  # Default to Google
    
    def _is_website_pattern(self, command: str) -> bool:
        """Check if command matches website opening pattern"""
        patterns = [
            r"เปิดเว็บ (.+)",
            r"open website (.+)",
            r"เข้าเว็บ (.+)"
        ]
        import re
        return any(re.search(pattern, command) for pattern in patterns)
    
    def _handle_website_pattern(self, command: str) -> str:
        """Handle website opening patterns"""
        import re
        
        # Extract website name
        patterns = [
            r"เปิดเว็บ (.+)",
            r"open website (.+)",
            r"เข้าเว็บ (.+)"
        ]
        
        website_name = None
        for pattern in patterns:
            match = re.search(pattern, command)
            if match:
                website_name = match.group(1).strip()
                break
        
        if not website_name:
            return "กรุณาระบุชื่อเว็บไซต์ที่ต้องการเปิดค่ะ"
        
        # Try to construct URL
        url = self._construct_website_url(website_name)
        
        try:
            webbrowser.open(url)
            return f"เปิดเว็บไซต์ {website_name} แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error opening website {website_name}: {e}")
            return f"เกิดข้อผิดพลาดในการเปิดเว็บไซต์ {website_name} ค่ะ"
    
    def _construct_website_url(self, website_name: str) -> str:
        """Construct URL from website name"""
        # Remove common TLDs if present
        name = website_name.replace('.com', '').replace('.co.th', '').replace('.org', '')
        
        # Add .com as default
        return f"https://{name}.com"
    
    def open_google_maps_search(self, query: str) -> str:
        """Open Google Maps with search query"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/maps/search/{encoded_query}"
            webbrowser.open(url)
            return f"ค้นหา {query} ใน Google Maps แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error opening Google Maps search: {e}")
            return "เกิดข้อผิดพลาดในการค้นหาใน Google Maps ค่ะ"
    
    def open_youtube_search(self, query: str) -> str:
        """Open YouTube with search query"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(url)
            return f"ค้นหา {query} ใน YouTube แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error opening YouTube search: {e}")
            return "เกิดข้อผิดพลาดในการค้นหาใน YouTube ค่ะ"
