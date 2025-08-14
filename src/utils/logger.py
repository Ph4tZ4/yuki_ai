"""
Logging utilities for Yuki AI
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from .config import config


class YukiLogger:
    """Custom logger for Yuki AI"""
    
    def __init__(self, name: str = "yuki_ai"):
        self.name = name
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """Setup logger configuration"""
        # Get logging settings from config
        log_settings = config.get_logging_settings()
        log_level = getattr(logging, log_settings.get('level', 'INFO'))
        log_format = log_settings.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file = log_settings.get('file', 'logs/yuki_ai.log')
        
        # Create logs directory if it doesn't exist
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure logger
        self.logger.setLevel(log_level)
        
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """Log debug message"""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log critical message"""
        self.logger.critical(message)
    
    def log_command(self, command: str, user: str = "user") -> None:
        """Log user commands"""
        self.info(f"Command from {user}: {command}")
    
    def log_response(self, response: str) -> None:
        """Log AI responses"""
        self.info(f"AI Response: {response}")
    
    def log_error(self, error: Exception, context: str = "") -> None:
        """Log errors with context"""
        self.error(f"Error in {context}: {str(error)}")
    
    def log_performance(self, operation: str, duration: float) -> None:
        """Log performance metrics"""
        self.info(f"Performance - {operation}: {duration:.2f}s")


# Global logger instance
logger = YukiLogger()
