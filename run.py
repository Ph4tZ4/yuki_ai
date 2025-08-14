#!/usr/bin/env python3
"""
Simple launcher script for Yuki AI
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main launcher function"""
    try:
        # Import and run the main application
        from main import main as yuki_main
        yuki_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting Yuki AI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
