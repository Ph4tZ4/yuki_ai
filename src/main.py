"""
Main application entry point for Yuki AI
"""

import sys
import signal
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from core.voice_engine import voice_engine
from core.command_processor import command_processor
from utils.config import config
from utils.logger import logger
from utils.helpers import ensure_directory


class YukiAI:
    """Main Yuki AI application class"""
    
    def __init__(self):
        self.is_running = False
        self.voice_engine = voice_engine
        self.command_processor = command_processor
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Yuki AI initialized")
    
    def start(self):
        """Start the Yuki AI application"""
        try:
            self.is_running = True
            
            # Ensure required directories exist
            ensure_directory("output")
            ensure_directory("logs")
            
            # Welcome message
            welcome_message = "ยูกิพร้อมใช้งานแล้วค่ะ เรียกชื่อยูกิเพื่อเริ่มต้นใช้งาน"
            logger.info("Starting Yuki AI")
            print("=" * 50)
            print("🎤 Yuki AI - Thai Voice Assistant")
            print("=" * 50)
            print(f"Version: {config.get('version', '2.0.0')}")
            print(f"Platform: {config.get('platform', 'macOS')}")
            print("=" * 50)
            print("Commands:")
            print("- Say 'ยูกิ' to wake up")
            print("- Say 'ยูกิ shutdown' to exit")
            print("- Say 'ยูกิ help' for more commands")
            print("=" * 50)
            
            # Speak welcome message
            self.voice_engine.speak(welcome_message)
            
            # Start listening for voice commands
            self.voice_engine.start_listening(self._handle_command)
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
            self.stop()
        except Exception as e:
            logger.error(f"Error starting Yuki AI: {e}")
            self.stop()
    
    def stop(self):
        """Stop the Yuki AI application"""
        if self.is_running:
            logger.info("Stopping Yuki AI")
            self.is_running = False
            self.voice_engine.stop_listening()
            
            # Farewell message
            farewell_message = "ยูกิปิดตัวลงแล้วค่ะ ขอบคุณที่ใช้งาน"
            self.voice_engine.speak(farewell_message)
            
            logger.info("Yuki AI stopped")
            sys.exit(0)
    
    def _handle_command(self, text: str):
        """Handle voice commands"""
        try:
            if not text:
                return
            
            print(f"\n🎤 คุณพูดว่า: {text}")
            
            # Process the command
            response = self.command_processor.process_command(text)
            
            if response:
                print(f"🤖 ยูกิ: {response}")
                
                # Check for shutdown command
                if "shutdown" in response.lower() or "ปิดตัวลง" in response:
                    self.stop()
                else:
                    # Speak the response
                    self.voice_engine.speak(response)
            
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            error_message = "เกิดข้อผิดพลาดในการประมวลผลคำสั่งค่ะ"
            print(f"🤖 ยูกิ: {error_message}")
            self.voice_engine.speak(error_message)
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}")
        self.stop()


def main():
    """Main function"""
    try:
        # Create and start Yuki AI
        yuki = YukiAI()
        yuki.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
