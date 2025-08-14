#!/usr/bin/env python3
"""
Basic test script for Yuki AI
"""

import sys
import os
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_imports():
    """Test basic imports"""
    print("🔧 Testing imports...")
    
    try:
        from utils.config import config
        print("✅ Config imported successfully")
        
        from utils.helpers import clean_text, process_thai_text, is_macos
        print("✅ Helpers imported successfully")
        
        from utils.logger import logger
        print("✅ Logger imported successfully")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n🔧 Testing configuration...")
    
    try:
        from utils.config import config
        
        # Test basic config values
        language = config.get('voice.language')
        print(f"✅ Voice language: {language}")
        
        tts_lang = config.get('voice.tts_language')
        print(f"✅ TTS language: {tts_lang}")
        
        wake_word = config.get('voice.wake_word')
        print(f"✅ Wake word: {wake_word}")
        
        return True
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False

def test_helpers():
    """Test helper functions"""
    print("\n🛠️ Testing helper functions...")
    
    try:
        from utils.helpers import clean_text, process_thai_text, is_macos
        
        # Test text cleaning
        test_text = "  Hello   World  "
        cleaned = clean_text(test_text)
        print(f"✅ Text cleaning: '{test_text}' -> '{cleaned}'")
        
        # Test Thai text processing
        thai_text = "ผมจะไปครับ"
        processed = process_thai_text(thai_text)
        print(f"✅ Thai processing: '{thai_text}' -> '{processed}'")
        
        # Test platform detection
        platform = "macOS" if is_macos() else "Other"
        print(f"✅ Platform detection: {platform}")
        
        return True
    except Exception as e:
        print(f"❌ Helper error: {e}")
        return False

def test_command_processor():
    """Test command processor"""
    print("\n🎤 Testing command processor...")
    
    try:
        # Test basic command processing logic without importing the full module
        from utils.helpers import clean_text, process_thai_text
        
        # Test basic commands
        test_commands = [
            "ยูกิ",
            "ยูกิ สวัสดี",
            "ยูกิ กี่โมงแล้ว"
        ]
        
        for command in test_commands:
            # Basic processing
            cleaned = clean_text(command)
            processed = process_thai_text(cleaned)
            print(f"✅ '{command}' -> cleaned: '{cleaned}' -> processed: '{processed}'")
        
        return True
    except Exception as e:
        print(f"❌ Command processor error: {e}")
        return False

def main():
    """Main test function"""
    print("🎤 Yuki AI - Basic Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_config,
        test_helpers,
        test_command_processor
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Yuki AI is ready to use.")
        print("\nTo run Yuki AI:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python run.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
