"""
Command processor for Yuki AI
"""

import json
import re
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

import sys
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
utils_path = current_dir.parent / "utils"
sys.path.insert(0, str(utils_path))

from utils.config import config
from utils.logger import logger
from utils.helpers import clean_text, process_thai_text, extract_query_from_command

# Import LLM engine
try:
    from .llm_engine import llm_engine
    logger.info("LLM engine imported successfully")
except ImportError as e:
    logger.warning(f"Failed to import LLM engine: {e}")
    llm_engine = None

# Import voice engine
try:
    from voice_engine import voice_engine
except ImportError:
    # Create a mock voice engine for testing
    class MockVoiceEngine:
        def speak(self, text):
            pass
    voice_engine = MockVoiceEngine()


class CommandProcessor:
    """Command processor for handling voice commands"""
    
    def __init__(self):
        self.commands: Dict[str, Any] = {}
        self.responses: Dict[str, Any] = {}
        self.call_count = 0
        self.last_command_time = 0
        
        # Load commands and responses
        self._load_commands()
        self._load_responses()
        
        # Get wake word from config
        voice_settings = config.get_voice_settings()
        self.wake_word = voice_settings.get('wake_word', 'ยูกิ')
        self.alternative_wake_words = voice_settings.get('alternative_wake_words', ['yuki'])
        
        logger.info("Command processor initialized")
    
    def _load_commands(self) -> None:
        """Load commands from JSON file"""
        try:
            # Try multiple possible locations
            possible_paths = [
                "src/data/commands.json",
                "commands.json",
                Path(__file__).parent.parent / "data" / "commands.json"
            ]
            
            commands_file = None
            for path in possible_paths:
                if Path(path).exists():
                    commands_file = path
                    break
            
            if commands_file:
                with open(commands_file, 'r', encoding='utf-8') as file:
                    raw_commands = json.load(file)
                
                # Flatten the nested structure
                self.commands = {}
                for category, commands in raw_commands.items():
                    if isinstance(commands, dict):
                        for pattern, action in commands.items():
                            self.commands[pattern] = action
                    else:
                        # Handle flat structure
                        self.commands[category] = commands
                
                logger.info(f"Loaded {len(self.commands)} commands from {commands_file}")
            else:
                logger.warning("Commands file not found, using default commands")
                self.commands = self._get_default_commands()
        except Exception as e:
            logger.error(f"Error loading commands: {e}")
            self.commands = self._get_default_commands()
    
    def _load_responses(self) -> None:
        """Load response templates from JSON file"""
        try:
            # Try multiple possible locations
            possible_paths = [
                "src/data/responses.json",
                Path(__file__).parent.parent / "data" / "responses.json"
            ]
            
            responses_file = None
            for path in possible_paths:
                if Path(path).exists():
                    responses_file = path
                    break
            
            if responses_file:
                with open(responses_file, 'r', encoding='utf-8') as file:
                    self.responses = json.load(file)
                logger.info(f"Loaded {len(self.responses)} response templates from {responses_file}")
            else:
                logger.warning("Responses file not found, using default responses")
                self.responses = self._get_default_responses()
        except Exception as e:
            logger.error(f"Error loading responses: {e}")
            self.responses = self._get_default_responses()
    
    def process_command(self, text: str) -> str:
        """Process voice command and return response"""
        if not text:
            return ""
        
        # Clean and process text
        text = clean_text(text)
        text = process_thai_text(text)
        
        # Check if it's a wake word call
        if self._is_wake_word_call(text):
            return self._handle_wake_word_call()
        
        # Check if command starts with wake word
        if not self._starts_with_wake_word(text):
            return "..."
        
        # Extract command after wake word
        command = self._extract_command(text)
        if not command:
            return self._get_response("no_command")
        
        # Process the command
        response = self._execute_command(command)
        
        # Update last command time
        self.last_command_time = time.time()
        
        return response
    
    def _is_wake_word_call(self, text: str) -> bool:
        """Check if text is just a wake word call"""
        wake_words = [self.wake_word] + self.alternative_wake_words
        return text.strip().lower() in [w.lower() for w in wake_words]
    
    def _starts_with_wake_word(self, text: str) -> bool:
        """Check if command starts with wake word"""
        wake_words = [self.wake_word] + self.alternative_wake_words
        text_lower = text.lower()
        return any(text_lower.startswith(w.lower()) for w in wake_words)
    
    def _extract_command(self, text: str) -> str:
        """Extract command part after wake word"""
        wake_words = [self.wake_word] + self.alternative_wake_words
        
        for wake_word in wake_words:
            if text.lower().startswith(wake_word.lower()):
                command = text[len(wake_word):].strip()
                return command
        
        return text
    
    def _handle_wake_word_call(self) -> str:
        """Handle wake word calls with varied responses"""
        self.call_count += 1
        
        responses = [
            "ค่ะ ยูกิอยู่นี่ค่ะ",
            "เรียกใช้ยูกิได้เลยค่ะ",
            "ยูกิพร้อมช่วยเหลือค่ะ",
            "นี่!! ตั้งใจแกล้งกันรึป่าวคะ?",
            "แบบนี้แกล้งกันชัด ๆ เลย!!!"
        ]
        
        if self.call_count <= len(responses):
            return responses[self.call_count - 1]
        else:
            return "ถ้าไม่อยากคุยกับยูกิแล้วให้พูดว่า 'ยูกิ shutdown' นะคะ มาเรียกแล้วไม่พูดแบบนี้ยูกิก็เสียใจ"
    
    def _execute_command(self, command: str) -> str:
        """Execute the actual command"""
        command_lower = command.lower()
        
        # Check predefined commands first
        for pattern, action in self.commands.items():
            if re.search(pattern, command_lower, re.IGNORECASE):
                logger.info(f"Command '{command}' matched pattern '{pattern}' with action '{action}'")
                return self._execute_action(action, command)
        
        # Check for web searches
        if self._is_web_search(command):
            return self._handle_web_search(command)
        
        # Check for web service opening (before app commands)
        if self._is_web_service_command(command):
            return self._handle_web_service_command(command)
        
        # Check for application opening
        if self._is_app_command(command):
            return self._handle_app_command(command)
        
        # Check for media commands
        if self._is_media_command(command):
            return self._handle_media_command(command)
        
        # Try LLM conversation (will use fallback if no service available)
        if llm_engine:
            logger.info(f"Using LLM for command: {command}")
            return self._handle_llm_conversation(command)
        
        # Default response
        logger.info(f"No LLM available, using default response for: {command}")
        return self._get_response("unknown_command")
    
    def _execute_action(self, action: str, command: str) -> str:
        """Execute specific action"""
        try:
            if action == "time":
                return self._get_current_time()
            elif action == "greeting":
                return self._get_response("greeting")
            elif action == "name":
                return self._get_response("name")
            elif action == "weather":
                return self._get_weather()
            elif action == "shutdown":
                return self._shutdown()
            elif action.startswith("open_"):
                return self._handle_web_action(action, command)
            else:
                return action
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return self._get_response("error")
    
    def _get_current_time(self) -> str:
        """Get current time in Thai format"""
        now = datetime.now()
        return f"ขณะนี้เวลา {now.hour} นาฬิกา {now.minute} นาที {now.second} วินาที"
    
    def _get_weather(self) -> str:
        """Get weather information"""
        try:
            import urllib.request
            weather_settings = config.get_weather_settings()
            api_key = config.get_api_keys().get('weather_api')
            
            if not api_key:
                return "ขออภัยค่ะ ไม่สามารถดึงข้อมูลสภาพอากาศได้ เนื่องจากไม่มี API key"
            
            location = weather_settings.get('default_location', 'Thailand')
            url = f"{weather_settings.get('api_url')}/{location}?unitGroup=metric&include=days&key={api_key}&contentType=json"
            
            with urllib.request.urlopen(url) as response:
                data = json.load(response)
                current_temp = data['days'][0]['temp']
                condition = data['days'][0]['conditions']
                
                return f"อุณหภูมิปัจจุบันในประเทศไทยคือ {current_temp} องศาเซลเซียส และสภาพอากาศ {condition} ค่ะ"
                
        except Exception as e:
            logger.error(f"Error getting weather: {e}")
            return "ขออภัยค่ะ ไม่สามารถดึงข้อมูลสภาพอากาศได้"
    
    def _shutdown(self) -> str:
        """Shutdown the assistant"""
        response = "ยูกิกำลังปิดตัวลงค่ะ"
        voice_engine.speak(response)
        logger.info("Shutdown command received")
        return response
    
    def _handle_web_action(self, action: str, command: str) -> str:
        """Handle web-related actions"""
        try:
            import webbrowser
            
            # Map actions to URLs
            web_actions = {
                "open_google": "https://www.google.com",
                "open_youtube": "https://www.youtube.com",
                "open_facebook": "https://www.facebook.com",
                "open_instagram": "https://www.instagram.com",
                "open_chatgpt": "https://chat.openai.com",
                "open_gemini": "https://gemini.google.com/app"
            }
            
            if action in web_actions:
                url = web_actions[action]
                webbrowser.open(url)
                
                # Get service name for response
                service_names = {
                    "open_google": "Google",
                    "open_youtube": "YouTube",
                    "open_facebook": "Facebook",
                    "open_instagram": "Instagram",
                    "open_chatgpt": "ChatGPT",
                    "open_gemini": "Gemini"
                }
                
                service_name = service_names.get(action, action.replace("open_", "").title())
                return f"เปิด {service_name} แล้วค่ะ"
            else:
                return f"ขออภัยค่ะ ไม่สามารถเปิด {action} ได้"
                
        except Exception as e:
            logger.error(f"Error handling web action {action}: {e}")
            return "ขออภัยค่ะ เกิดข้อผิดพลาดในการเปิดเว็บไซต์"
    
    def _is_web_search(self, command: str) -> bool:
        """Check if command is a web search"""
        # More specific search triggers to avoid false matches
        search_triggers = ["ค้นหา", "search", "เสิร์ช"]
        command_lower = command.lower()
        
        # Check for exact search patterns
        for trigger in search_triggers:
            if trigger in command_lower:
                return True
        
        # Check for "หา" only if it's at the beginning or followed by specific words
        if "หา" in command_lower:
            # Don't match if it's part of other words like "แนะนำ" (recommend)
            if command_lower.startswith("หา") or " หา " in command_lower:
                return True
        
        return False
    
    def _handle_web_search(self, command: str) -> str:
        """Handle web search commands"""
        import webbrowser
        
        search_triggers = ["ค้นหา", "search", "เสิร์ช", "หา"]
        query = extract_query_from_command(command, search_triggers)
        
        if query:
            search_url = f"https://www.google.com/search?q={query}"
            webbrowser.open(search_url)
            return f"ค้นหา {query} บน Google แล้วค่ะ"
        
        return self._get_response("no_query")
    
    def _is_app_command(self, command: str) -> bool:
        """Check if command is for opening an application"""
        app_triggers = ["เปิดแอป", "open app", "เปิดแอปพลิเคชัน", "open application"]
        command_lower = command.lower()
        return any(trigger in command_lower for trigger in app_triggers)
    
    def _handle_app_command(self, command: str) -> str:
        """Handle application opening commands"""
        try:
            import sys
            from pathlib import Path
            commands_path = Path(__file__).parent.parent / "commands"
            sys.path.insert(0, str(commands_path))
            from app_commands import AppCommands
            app_commands = AppCommands()
            return app_commands.process_command(command)
        except ImportError:
            return "ไม่สามารถโหลดโมดูลแอปพลิเคชันได้ค่ะ"
    
    def _is_media_command(self, command: str) -> bool:
        """Check if command is for media control"""
        media_triggers = ["เล่นเพลง", "play music", "ฟังเพลง", "listen to music", "ดูวิดีโอ", "watch video", "เปิดเพลง", "open music", "เปิดวิดีโอ", "open video"]
        return any(trigger in command.lower() for trigger in media_triggers)
    
    def _handle_media_command(self, command: str) -> str:
        """Handle media control commands"""
        try:
            import sys
            from pathlib import Path
            commands_path = Path(__file__).parent.parent / "commands"
            sys.path.insert(0, str(commands_path))
            from media_commands import MediaCommands
            media_commands = MediaCommands()
            return media_commands.process_command(command)
        except ImportError:
            return "ไม่สามารถโหลดโมดูลสื่อได้ค่ะ"
    
    def _is_web_service_command(self, command: str) -> bool:
        """Check if command is for opening a web service"""
        web_triggers = ["เปิดเว็บ", "open website", "เปิดเว็บไซต์", "open site", "เข้าเว็บ", "เข้าเว็บไซต์"]
        command_lower = command.lower()
        return any(trigger in command_lower for trigger in web_triggers)
    
    def _handle_web_service_command(self, command: str) -> str:
        """Handle web service opening commands"""
        try:
            import sys
            from pathlib import Path
            commands_path = Path(__file__).parent.parent / "commands"
            sys.path.insert(0, str(commands_path))
            from web_commands import WebCommands
            web_commands = WebCommands()
            return web_commands.process_command(command)
        except ImportError:
            return "ไม่สามารถโหลดโมดูลเว็บได้ค่ะ"
    
    def _handle_llm_conversation(self, command: str) -> str:
        """Handle conversation using LLM"""
        try:
            # Add context about Yuki being a voice assistant
            context = "You are being spoken to through a voice assistant. Keep responses concise and natural for speech."
            
            # Generate response using LLM
            response = llm_engine.generate_response(command, context)
            
            # Log the conversation
            logger.info(f"LLM Conversation - User: {command}")
            logger.info(f"LLM Conversation - Yuki: {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in LLM conversation: {e}")
            return "ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผลคำตอบ"
    
    def _get_response(self, response_type: str) -> str:
        """Get response template"""
        return self.responses.get(response_type, "ขอโทษค่ะ ฉันไม่เข้าใจที่คุณพูด")
    
    def _get_default_commands(self) -> Dict[str, str]:
        """Get default commands"""
        return {
            "กี่โมงแล้ว": "time",
            "ตอนนี้เวลาเท่าไหร่": "time",
            "เวลาตอนนี้คือ": "time",
            "สวัสดี": "greeting",
            "สวัสดียูกิ": "greeting",
            "ยูกิสวัสดี": "greeting",
            "หวัดดี": "greeting",
            "hello": "greeting",
            "hi": "greeting",
            "ชื่ออะไร": "name",
            "คุณชื่ออะไร": "name",
            "เธอชื่ออะไร": "name",
            "คุณคือใคร": "name",
            "เธอคือใคร": "name",
            "อากาศวันนี้เป็นอย่างไร": "weather",
            "shutdown": "shutdown",
            "shut down": "shutdown"
        }
    
    def _get_default_responses(self) -> Dict[str, str]:
        """Get default responses"""
        return {
            "greeting": "สวัสดีค่ะ มีอะไรให้ช่วยไหมคะ?",
            "name": "ฉันคือผู้ช่วยอัจฉริยะของคุณค่ะ",
            "unknown_command": "ขอโทษค่ะ ฉันไม่เข้าใจที่คุณพูด",
            "no_command": "กรุณาพูดคำสั่งที่ต้องการค่ะ",
            "no_query": "กรุณาระบุสิ่งที่ต้องการค้นหาค่ะ",
            "error": "เกิดข้อผิดพลาดในการประมวลผลคำสั่งค่ะ"
        }


# Global command processor instance
command_processor = CommandProcessor()
