"""
Voice engine for speech recognition and text-to-speech
"""

import speech_recognition as sr
from gtts import gTTS
import time
import threading
from typing import Optional, Callable, Dict, Any
from pathlib import Path

import sys
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
utils_path = current_dir.parent / "utils"
sys.path.insert(0, str(utils_path))

from utils.config import config
from utils.logger import logger
from utils.helpers import ensure_directory, retry_operation


class VoiceEngine:
    """Voice engine for speech recognition and text-to-speech"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.callback: Optional[Callable[[str], None]] = None
        
        # Get settings from config
        voice_settings = config.get_voice_settings()
        audio_settings = config.get_audio_settings()
        
        self.language = voice_settings.get('language', 'th-TH')
        self.tts_language = voice_settings.get('tts_language', 'th')
        self.sample_rate = audio_settings.get('sample_rate', 16000)
        self.chunk_size = audio_settings.get('chunk_size', 1024)
        self.output_dir = audio_settings.get('output_directory', 'output')
        
        # Ensure output directory exists
        ensure_directory(self.output_dir)
        
        # Configure recognizer
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        logger.info("Voice engine initialized")
    
    def start_listening(self, callback: Callable[[str], None]) -> None:
        """Start listening for voice commands"""
        self.callback = callback
        self.is_listening = True
        
        # Adjust for ambient noise
        with self.microphone as source:
            logger.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
        
        logger.info("Started listening for voice commands")
        
        while self.is_listening:
            try:
                with self.microphone as source:
                    logger.debug("Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                # Process the audio
                self._process_audio(audio)
                
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                logger.debug("Could not understand audio")
                continue
            except Exception as e:
                logger.error(f"Error in voice recognition: {e}")
                continue
    
    def stop_listening(self) -> None:
        """Stop listening for voice commands"""
        self.is_listening = False
        logger.info("Stopped listening for voice commands")
    
    def _process_audio(self, audio: sr.AudioData) -> None:
        """Process audio and convert to text"""
        try:
            start_time = time.time()
            
            # Convert speech to text
            text = self.recognizer.recognize_google(
                audio, 
                language=self.language
            )
            
            processing_time = time.time() - start_time
            logger.log_performance("Speech recognition", processing_time)
            
            if text and self.callback:
                logger.log_command(text)
                self.callback(text)
            
        except sr.UnknownValueError:
            logger.debug("Speech not recognized")
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition service: {e}")
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
    
    def speak(self, text: str, save_audio: bool = True) -> None:
        """Convert text to speech and play it"""
        if not text:
            return
        
        try:
            start_time = time.time()
            
            # Create TTS object
            tts = gTTS(text=text, lang=self.tts_language, slow=False)
            
            # Generate unique filename
            timestamp = int(time.time())
            filename = f"response_{timestamp}.mp3"
            file_path = Path(self.output_dir) / filename
            
            # Save audio file
            tts.save(str(file_path))
            
            # Play audio
            self._play_audio(str(file_path))
            
            processing_time = time.time() - start_time
            logger.log_performance("Text-to-speech", processing_time)
            logger.log_response(text)
            
            # Clean up old audio files
            if save_audio:
                self._cleanup_old_audio_files()
            else:
                # Remove the file immediately if not saving
                file_path.unlink(missing_ok=True)
                
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
    
    def _play_audio(self, file_path: str) -> None:
        """Play audio file"""
        try:
            from playsound import playsound
            playsound(file_path)
        except ImportError:
            logger.warning("playsound not available, trying alternative method")
            self._play_audio_alternative(file_path)
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            self._play_audio_alternative(file_path)
    
    def _play_audio_alternative(self, file_path: str) -> None:
        """Alternative audio playback method"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["afplay", file_path])
            elif platform.system() == "Windows":
                subprocess.run(["start", file_path], shell=True)
            else:  # Linux
                subprocess.run(["aplay", file_path])
        except Exception as e:
            logger.error(f"Alternative audio playback failed: {e}")
    
    def _cleanup_old_audio_files(self, max_files: int = 10) -> None:
        """Clean up old audio files to save space"""
        try:
            output_path = Path(self.output_dir)
            if not output_path.exists():
                return
            
            # Get all mp3 files
            audio_files = list(output_path.glob("*.mp3"))
            
            if len(audio_files) > max_files:
                # Sort by modification time and remove oldest
                audio_files.sort(key=lambda x: x.stat().st_mtime)
                files_to_remove = audio_files[:-max_files]
                
                for file in files_to_remove:
                    file.unlink()
                    logger.debug(f"Removed old audio file: {file}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {e}")
    
    def test_microphone(self) -> bool:
        """Test microphone functionality"""
        try:
            with self.microphone as source:
                logger.info("Testing microphone...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Microphone test successful: {text}")
                return True
        except Exception as e:
            logger.error(f"Microphone test failed: {e}")
            return False
    
    def get_available_microphones(self) -> list:
        """Get list of available microphones"""
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            logger.error(f"Error getting microphone list: {e}")
            return []
    
    def set_microphone(self, device_index: int) -> bool:
        """Set specific microphone device"""
        try:
            self.microphone = sr.Microphone(device_index=device_index)
            logger.info(f"Set microphone to device index: {device_index}")
            return True
        except Exception as e:
            logger.error(f"Error setting microphone: {e}")
            return False


# Global voice engine instance
voice_engine = VoiceEngine()
