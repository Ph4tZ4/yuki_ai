#!/usr/bin/env python3
"""
Demo script for Yuki AI - Test functionality without voice input
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from core.command_processor import command_processor
from utils.logger import logger


def demo_commands():
    """Demo various commands"""
    print("🎤 Yuki AI Demo - Testing Commands")
    print("=" * 50)
    
    # Test commands
    test_commands = [
        "ยูกิ",
        "ยูกิ สวัสดี",
        "ยูกิ กี่โมงแล้ว",
        "ยูกิ ชื่ออะไร",
        "ยูกิ อากาศวันนี้เป็นอย่างไร",
        "ยูกิ เปิด Google",
        "ยูกิ เล่นเพลง despacito",
        "ยูกิ ค้นหา python programming",
        "ยูกิ shutdown"
    ]
    
    for i, command in enumerate(test_commands, 1):
        print(f"\n{i}. Testing: '{command}'")
        print("-" * 30)
        
        try:
            response = command_processor.process_command(command)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Don't actually shutdown in demo
        if "shutdown" in command:
            print("(Shutdown command simulated)")
            break


def demo_config():
    """Demo configuration functionality"""
    print("\n🔧 Testing Configuration")
    print("=" * 30)
    
    from utils.config import config
    
    # Test config values
    print(f"Voice language: {config.get('voice.language')}")
    print(f"TTS language: {config.get('voice.tts_language')}")
    print(f"Wake word: {config.get('voice.wake_word')}")
    print(f"Output directory: {config.get('audio.output_directory')}")


def demo_helpers():
    """Demo helper functions"""
    print("\n🛠️  Testing Helper Functions")
    print("=" * 30)
    
    from utils.helpers import clean_text, process_thai_text, is_macos
    
    # Test text cleaning
    test_text = "  Hello   World  "
    cleaned = clean_text(test_text)
    print(f"Text cleaning: '{test_text}' -> '{cleaned}'")
    
    # Test Thai text processing
    thai_text = "ผมจะไปครับ"
    processed = process_thai_text(thai_text)
    print(f"Thai processing: '{thai_text}' -> '{processed}'")
    
    # Test platform detection
    platform = "macOS" if is_macos() else "Other"
    print(f"Platform detection: {platform}")


def main():
    """Main demo function"""
    try:
        print("🎤 Yuki AI - Thai Voice Assistant Demo")
        print("=" * 50)
        print("This demo tests the core functionality without voice input.")
        print("=" * 50)
        
        # Test configuration
        demo_config()
        
        # Test helper functions
        demo_helpers()
        
        # Test commands
        demo_commands()
        
        print("\n✅ Demo completed successfully!")
        print("To run the full voice assistant, use: python run.py")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        logger.error(f"Demo error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
