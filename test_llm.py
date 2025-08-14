#!/usr/bin/env python3
"""
Test script for LLM integration with Yuki AI
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_llm_basic():
    """Test basic LLM functionality"""
    try:
        from core.llm_engine import llm_engine
        
        print("🤖 Testing LLM Integration")
        print("=" * 30)
        
        # Check if any LLM service is available
        if not llm_engine.is_available():
            print("❌ No LLM service is available")
            print("LLM will use fallback responses")
        
        print(f"📦 Using model: {llm_engine.model_name}")
        print(f"🔧 LLM enabled: {llm_engine.enable_llm}")
        
        # Test simple conversation
        test_questions = [
            "สวัสดี ยูกิ",
            "คุณช่วยอะไรได้บ้าง?",
            "เล่าเรื่องประเทศไทยให้ฟังหน่อย",
            "What is artificial intelligence?",
            "ช่วยแนะนำอาหารไทยอร่อยๆ หน่อย"
        ]
        
        for question in test_questions:
            print(f"\n🤔 User: {question}")
            response = llm_engine.generate_response(question)
            print(f"🤖 Yuki: {response}")
            print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_llm_with_context():
    """Test LLM with context"""
    try:
        from core.llm_engine import llm_engine
        
        print("\n🧠 Testing LLM with Context")
        print("=" * 30)
        
        # Test conversation with context
        context = "You are helping a user plan a trip to Thailand"
        
        questions = [
            "แนะนำสถานที่เที่ยวในกรุงเทพ",
            "อาหารอะไรที่ต้องลอง",
            "ควรไปช่วงไหนดี"
        ]
        
        for question in questions:
            print(f"\n🤔 User: {question}")
            response = llm_engine.generate_response(question, context)
            print(f"🤖 Yuki: {response}")
            print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Yuki AI - LLM Integration Test")
    print("=" * 40)
    
    # Test basic functionality
    if test_llm_basic():
        print("\n✅ Basic LLM test passed!")
    else:
        print("\n❌ Basic LLM test failed!")
        return
    
    # Test with context
    if test_llm_with_context():
        print("\n✅ Context LLM test passed!")
    else:
        print("\n❌ Context LLM test failed!")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    main()
