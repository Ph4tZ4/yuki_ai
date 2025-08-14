"""
Helper utilities for Yuki AI
"""

import os
import re
import subprocess
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import platform


def is_macos() -> bool:
    """Check if running on macOS"""
    return platform.system() == "Darwin"


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == "Windows"


def is_linux() -> bool:
    """Check if running on Linux"""
    return platform.system() == "Linux"


def clean_text(text: str) -> str:
    """Clean and normalize text input"""
    if not text:
        return ""
    
    # Convert to lowercase and strip whitespace
    text = text.lower().strip()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text


def process_thai_text(text: str) -> str:
    """Process Thai text for better recognition"""
    if not text:
        return ""
    
    # Replace common Thai male pronouns with neutral ones
    replacements = {
        "ผม": "ฉันเองก็",
        "ครับ": "ค่ะ",
        "ผมจะ": "ฉันจะ",
        "ผมอยาก": "ฉันอยาก"
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def extract_query_from_command(command: str, trigger_words: List[str]) -> str:
    """Extract search query from command after trigger words"""
    command_lower = command.lower()
    
    for trigger in trigger_words:
        if trigger in command_lower:
            # Remove the trigger word and clean up
            query = command_lower.replace(trigger, "").strip()
            return query
    
    return ""


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file operations"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    
    return filename


def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except OSError:
        return 0.0


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.1f} วินาที"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} นาที"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} ชั่วโมง"


def retry_operation(func, max_attempts: int = 3, delay: float = 1.0):
    """Retry an operation with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise e
            time.sleep(delay * (2 ** attempt))


def open_application_macos(app_path: str, app_name: str) -> str:
    """Open application on macOS"""
    try:
        if os.path.exists(app_path):
            subprocess.Popen([app_path])
            return f"เปิด {app_name} แล้วค่ะ"
        else:
            # Try using 'open' command for .app bundles
            app_bundle = f"/Applications/{app_name}.app"
            if os.path.exists(app_bundle):
                subprocess.run(["open", app_bundle])
                return f"เปิด {app_name} แล้วค่ะ"
            else:
                return f"ไม่พบ {app_name} ในระบบค่ะ"
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเปิด {app_name}: {str(e)}"


def open_application_windows(app_path: str, app_name: str) -> str:
    """Open application on Windows"""
    try:
        if os.path.exists(app_path):
            subprocess.Popen([app_path])
            return f"เปิด {app_name} แล้วค่ะ"
        else:
            return f"ไม่พบ {app_name} ในระบบค่ะ"
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการเปิด {app_name}: {str(e)}"


def open_application(app_path: str, app_name: str) -> str:
    """Open application based on platform"""
    if is_macos():
        return open_application_macos(app_path, app_name)
    elif is_windows():
        return open_application_windows(app_path, app_name)
    else:
        # Linux fallback
        try:
            subprocess.Popen([app_path])
            return f"เปิด {app_name} แล้วค่ะ"
        except Exception as e:
            return f"เกิดข้อผิดพลาดในการเปิด {app_name}: {str(e)}"


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))


def create_search_url(base_url: str, query: str) -> str:
    """Create search URL with query parameters"""
    if "google.com" in base_url:
        return f"{base_url}/search?q={query}"
    elif "youtube.com" in base_url:
        return f"{base_url}/results?search_query={query}"
    else:
        return f"{base_url}?q={query}"


def get_system_info() -> Dict[str, str]:
    """Get system information"""
    return {
        "platform": platform.system(),
        "platform_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version()
    }


def format_time(seconds: int) -> str:
    """Format time in Thai format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours} ชั่วโมง {minutes} นาที {secs} วินาที"
    elif minutes > 0:
        return f"{minutes} นาที {secs} วินาที"
    else:
        return f"{secs} วินาที"
