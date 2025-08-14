"""
Configuration management for Yuki AI
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for Yuki AI"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self._config = yaml.safe_load(file) or {}
            else:
                self._config = self._get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = self._get_default_config()
    
    def save_config(self) -> None:
        """Save configuration to YAML file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as file:
                yaml.dump(self._config, file, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """Get voice-related settings"""
        return self.get('voice', {})
    
    def get_audio_settings(self) -> Dict[str, Any]:
        """Get audio-related settings"""
        return self.get('audio', {})
    
    def get_applications(self) -> Dict[str, str]:
        """Get application paths"""
        return self.get('applications', {})
    
    def get_web_services(self) -> Dict[str, str]:
        """Get web service URLs"""
        return self.get('web_services', {})
    
    def get_api_keys(self) -> Dict[str, str]:
        """Get API keys"""
        return self.get('api_keys', {})
    
    def get_weather_settings(self) -> Dict[str, Any]:
        """Get weather-related settings"""
        return self.get('weather', {})
    
    def get_logging_settings(self) -> Dict[str, Any]:
        """Get logging settings"""
        return self.get('logging', {})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'voice': {
                'language': 'th-TH',
                'tts_language': 'th',
                'speech_rate': 1.0,
                'volume': 1.0,
                'wake_word': 'ยูกิ',
                'alternative_wake_words': ['yuki', 'ยูกิ']
            },
            'audio': {
                'sample_rate': 16000,
                'chunk_size': 1024,
                'format': 'mp3',
                'output_directory': 'output',
                'signal_sound': 'assets/audio/signal.mp3',
                'error_sound': 'assets/audio/error.mp3'
            },
            'applications': {},
            'web_services': {
                'google': 'https://www.google.com',
                'youtube': 'https://www.youtube.com',
                'facebook': 'https://www.facebook.com',
                'instagram': 'https://www.instagram.com'
            },
            'api_keys': {},
            'weather': {
                'default_location': 'Thailand',
                'units': 'metric'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/yuki_ai.log'
            }
        }


# Global configuration instance
config = Config()
