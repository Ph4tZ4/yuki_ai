"""
Media commands for Yuki AI
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
from utils.helpers import extract_query_from_command


class MediaCommands:
    """Handle media and entertainment commands"""
    
    def __init__(self):
        self.media_services = {
            "youtube": "https://www.youtube.com",
            "spotify": "https://open.spotify.com",
            "netflix": "https://www.netflix.com",
            "apple_music": "https://music.apple.com",
            "soundcloud": "https://soundcloud.com",
            "deezer": "https://www.deezer.com"
        }
    
    def process_command(self, command: str) -> str:
        """Process media-related commands"""
        command_lower = command.lower()
        
        # Check for music playing commands
        if self._is_music_command(command_lower):
            return self._handle_music_command(command)
        
        # Check for video playing commands
        if self._is_video_command(command_lower):
            return self._handle_video_command(command)
        
        # Check for streaming service commands
        if self._is_streaming_command(command_lower):
            return self._handle_streaming_command(command)
        
        # Check for general media commands
        if self._is_media_command(command_lower):
            return self._handle_general_media_command(command)
        
        return "ไม่เข้าใจคำสั่งสื่อค่ะ กรุณาลองใหม่อีกครั้ง"
    
    def _is_music_command(self, command: str) -> bool:
        """Check if command is for music"""
        music_triggers = [
            "เล่นเพลง", "play music", "ฟังเพลง", "listen to music",
            "เปิดเพลง", "open music", "เพลง", "music"
        ]
        return any(trigger in command for trigger in music_triggers)
    
    def _handle_music_command(self, command: str) -> str:
        """Handle music playing commands"""
        # Extract song/artist name
        music_triggers = ["เล่นเพลง", "play music", "ฟังเพลง", "listen to music", "เล่น", "play", "ฟัง", "listen"]
        query = extract_query_from_command(command, music_triggers)
        
        if not query:
            return "กรุณาระบุเพลงหรือศิลปินที่ต้องการฟังค่ะ"
        
        # Determine platform
        platform = self._determine_music_platform(command)
        
        if platform == "youtube":
            return self._play_on_youtube(query)
        elif platform == "spotify":
            return self._play_on_spotify(query)
        else:
            # Default to YouTube
            return self._play_on_youtube(query)
    
    def _is_video_command(self, command: str) -> bool:
        """Check if command is for video"""
        video_triggers = [
            "ดูวิดีโอ", "watch video", "ดูคลิป", "watch clip",
            "ดูหนัง", "watch movie", "ดูซีรีส์", "watch series",
            "เปิดวิดีโอ", "open video"
        ]
        return any(trigger in command for trigger in video_triggers)
    
    def _handle_video_command(self, command: str) -> str:
        """Handle video playing commands"""
        # Extract video title
        video_triggers = ["ดู", "watch", "ดูวิดีโอ", "watch video", "ดูคลิป", "watch clip"]
        query = extract_query_from_command(command, video_triggers)
        
        if not query:
            return "กรุณาระบุวิดีโอที่ต้องการดูค่ะ"
        
        # Determine platform
        platform = self._determine_video_platform(command)
        
        if platform == "youtube":
            return self._play_on_youtube(query)
        elif platform == "netflix":
            return self._search_on_netflix(query)
        else:
            # Default to YouTube
            return self._play_on_youtube(query)
    
    def _is_streaming_command(self, command: str) -> bool:
        """Check if command is for streaming services"""
        streaming_triggers = [
            "netflix", "spotify", "youtube", "apple music", "soundcloud", "deezer"
        ]
        return any(trigger in command for trigger in streaming_triggers)
    
    def _handle_streaming_command(self, command: str) -> str:
        """Handle streaming service commands"""
        for service_name, url in self.media_services.items():
            if service_name in command.lower():
                try:
                    webbrowser.open(url)
                    return f"เปิด {service_name} แล้วค่ะ"
                except Exception as e:
                    logger.error(f"Error opening {service_name}: {e}")
                    return f"เกิดข้อผิดพลาดในการเปิด {service_name} ค่ะ"
        
        return "ไม่เข้าใจคำสั่งบริการสตรีมมิ่งค่ะ"
    
    def _is_media_command(self, command: str) -> bool:
        """Check if command is a general media command"""
        media_triggers = [
            "media", "entertainment", "ความบันเทิง", "สื่อ"
        ]
        return any(trigger in command for trigger in media_triggers)
    
    def _handle_general_media_command(self, command: str) -> str:
        """Handle general media commands"""
        # Default to opening YouTube
        try:
            webbrowser.open("https://www.youtube.com")
            return "เปิด YouTube แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error opening YouTube: {e}")
            return "เกิดข้อผิดพลาดในการเปิด YouTube ค่ะ"
    
    def _determine_music_platform(self, command: str) -> str:
        """Determine which music platform to use"""
        if "spotify" in command.lower():
            return "spotify"
        elif "youtube" in command.lower():
            return "youtube"
        elif "apple music" in command.lower() or "apple" in command.lower():
            return "apple_music"
        elif "soundcloud" in command.lower():
            return "soundcloud"
        elif "deezer" in command.lower():
            return "deezer"
        else:
            return "youtube"  # Default to YouTube
    
    def _determine_video_platform(self, command: str) -> str:
        """Determine which video platform to use"""
        if "netflix" in command.lower():
            return "netflix"
        elif "youtube" in command.lower():
            return "youtube"
        else:
            return "youtube"  # Default to YouTube
    
    def _play_on_youtube(self, query: str) -> str:
        """Play music/video on YouTube"""
        try:
            import pywhatkit
            pywhatkit.playonyt(query)
            return f"เล่น {query} บน YouTube แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error playing on YouTube: {e}")
            # Fallback to web search
            try:
                encoded_query = urllib.parse.quote(query)
                url = f"https://www.youtube.com/results?search_query={encoded_query}"
                webbrowser.open(url)
                return f"ค้นหา {query} บน YouTube แล้วค่ะ"
            except Exception as e2:
                logger.error(f"Error with YouTube fallback: {e2}")
                return "เกิดข้อผิดพลาดในการเล่นบน YouTube ค่ะ"
    
    def _play_on_spotify(self, query: str) -> str:
        """Play music on Spotify"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://open.spotify.com/search/{encoded_query}"
            webbrowser.open(url)
            return f"ค้นหา {query} บน Spotify แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error playing on Spotify: {e}")
            return "เกิดข้อผิดพลาดในการเล่นบน Spotify ค่ะ"
    
    def _search_on_netflix(self, query: str) -> str:
        """Search on Netflix"""
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.netflix.com/search?q={encoded_query}"
            webbrowser.open(url)
            return f"ค้นหา {query} บน Netflix แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error searching on Netflix: {e}")
            return "เกิดข้อผิดพลาดในการค้นหาบน Netflix ค่ะ"
    
    def play_specific_song(self, song_name: str, artist: str = "") -> str:
        """Play a specific song"""
        query = f"{song_name} {artist}".strip()
        return self._play_on_youtube(query)
    
    def play_artist(self, artist_name: str) -> str:
        """Play music by a specific artist"""
        return self._play_on_youtube(artist_name)
    
    def open_playlist(self, playlist_name: str) -> str:
        """Open a playlist"""
        try:
            encoded_query = urllib.parse.quote(playlist_name)
            url = f"https://www.youtube.com/results?search_query={encoded_query}+playlist"
            webbrowser.open(url)
            return f"ค้นหาเพลย์ลิสต์ {playlist_name} แล้วค่ะ"
        except Exception as e:
            logger.error(f"Error opening playlist: {e}")
            return "เกิดข้อผิดพลาดในการเปิดเพลย์ลิสต์ค่ะ"
