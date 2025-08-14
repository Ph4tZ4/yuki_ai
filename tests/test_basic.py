"""
Basic tests for Yuki AI
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config import config
from utils.helpers import clean_text, process_thai_text, is_macos


def test_config_loading():
    """Test configuration loading"""
    assert config is not None
    assert config.get('voice.language') == 'th-TH'


def test_text_cleaning():
    """Test text cleaning functionality"""
    test_text = "  Hello   World  "
    cleaned = clean_text(test_text)
    assert cleaned == "hello world"


def test_thai_text_processing():
    """Test Thai text processing"""
    test_text = "ผมจะไปครับ"
    processed = process_thai_text(test_text)
    assert "ผม" not in processed
    assert "ครับ" not in processed


def test_platform_detection():
    """Test platform detection"""
    # This should work on macOS
    assert is_macos() in [True, False]


def test_config_get():
    """Test configuration get method"""
    # Test getting a value that exists
    language = config.get('voice.language')
    assert language == 'th-TH'
    
    # Test getting a value that doesn't exist
    non_existent = config.get('non.existent', 'default')
    assert non_existent == 'default'


if __name__ == "__main__":
    pytest.main([__file__])
