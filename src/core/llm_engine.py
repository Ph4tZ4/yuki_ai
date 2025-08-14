"""
LLM Engine for Yuki AI - Mini/Nano LLM Integration
"""

import requests
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import sys

# Add parent directories to path for imports
current_dir = Path(__file__).parent
utils_path = current_dir.parent / "utils"
sys.path.insert(0, str(utils_path))

from utils.config import config
from utils.logger import logger


class LLMEngine:
    """LLM Engine for handling conversations with mini/nano LLMs"""
    
    def __init__(self):
        self.ollama_url = config.get('llm.ollama_url', 'http://localhost:11434')
        self.model_name = config.get('llm.model_name', 'llama3.2:1b')
        self.max_tokens = config.get('llm.max_tokens', 500)
        self.temperature = config.get('llm.temperature', 0.7)
        self.context_window = config.get('llm.context_window', 10)
        self.enable_llm = config.get('llm.enable_llm', True)
        
        # Cloud API settings
        self.use_cloud_api = config.get('llm.use_cloud_api', False)
        self.openai_api_key = config.get('api_keys.openai_api')
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        
        # System prompt for Yuki
        self.system_prompt = self._get_system_prompt()
        
        logger.info(f"LLM Engine initialized with model: {self.model_name}")
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for Yuki AI"""
        return """You are Yuki (ยูกิ), a helpful Thai AI assistant. You are friendly, polite, and speak in Thai with some English when appropriate.

Key characteristics:
- You are helpful and always try to assist users
- You speak in Thai primarily, but can use English when needed
- You are polite and use respectful language (ค่ะ/ครับ)
- You have a cheerful personality
- You can help with various tasks like answering questions, providing information, and having conversations
- You are a voice assistant - keep responses concise and natural for speech

When responding:
- Keep responses VERY SHORT (maximum 1 sentence, 20-30 words)
- Use natural Thai language
- Be friendly and engaging
- If you don't know something, say so politely
- Don't make up information
- Responses should be easy to speak and understand
- NO long explanations or lists

Remember: You are Yuki, a helpful Thai AI voice assistant! Keep responses brief and voice-friendly!"""
    
    def is_available(self) -> bool:
        """Check if any LLM service is available"""
        if not self.enable_llm:
            return False
            
        # Try Ollama first
        if self._check_ollama_available():
            return True
            
        # Try cloud API as fallback
        if self.use_cloud_api and self.openai_api_key:
            return True
            
        return False
    
    def _check_ollama_available(self) -> bool:
        """Check if Ollama is available and the model is loaded"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == self.model_name for model in models)
            return False
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def load_model(self) -> bool:
        """Load the specified model"""
        try:
            logger.info(f"Loading model: {self.model_name}")
            response = requests.post(
                f"{self.ollama_url}/api/pull",
                json={"name": self.model_name},
                timeout=300  # 5 minutes timeout for model download
            )
            if response.status_code == 200:
                logger.info(f"Model {self.model_name} loaded successfully")
                return True
            else:
                logger.error(f"Failed to load model: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def generate_response(self, user_input: str, context: str = "") -> str:
        """Generate a response using the LLM"""
        try:
            # Try Ollama first
            if self._check_ollama_available():
                return self._generate_ollama_response(user_input, context)
            
            # Try cloud API as fallback
            if self.use_cloud_api and self.openai_api_key:
                return self._generate_cloud_response(user_input, context)
            
            # Fallback to simple responses
            return self._generate_fallback_response(user_input)
                
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return "ขออภัยค่ะ ไม่สามารถเชื่อมต่อกับระบบ AI ได้"
    
    def _generate_ollama_response(self, user_input: str, context: str = "") -> str:
        """Generate response using Ollama"""
        try:
            # Build the conversation context
            messages = self._build_messages(user_input, context)
            
            # Prepare the request
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens
                }
            }
            
            # Make the request
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['message']['content']
                
                # Update conversation history
                self._update_history(user_input, assistant_message)
                
                return assistant_message
            else:
                logger.error(f"Ollama API error: {response.text}")
                return "ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผลคำตอบ"
                
        except Exception as e:
            logger.error(f"Error with Ollama: {e}")
            return "ขออภัยค่ะ ไม่สามารถเชื่อมต่อกับ Ollama ได้"
    
    def _generate_cloud_response(self, user_input: str, context: str = "") -> str:
        """Generate response using cloud API (OpenAI)"""
        try:
            headers = {
                "Authorization": f"Bearer {self.openai_api_key}",
                "Content-Type": "application/json"
            }
            
            messages = self._build_messages(user_input, context)
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            response = requests.post(
                self.openai_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                assistant_message = result['choices'][0]['message']['content']
                
                # Update conversation history
                self._update_history(user_input, assistant_message)
                
                return assistant_message
            else:
                logger.error(f"Cloud API error: {response.text}")
                return "ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผลคำตอบ"
                
        except Exception as e:
            logger.error(f"Error with cloud API: {e}")
            return "ขออภัยค่ะ ไม่สามารถเชื่อมต่อกับ cloud API ได้"
    
    def _generate_fallback_response(self, user_input: str) -> str:
        """Generate simple fallback responses"""
        user_input_lower = user_input.lower()
        
        # Simple keyword-based responses
        if any(word in user_input_lower for word in ["สวัสดี", "hello", "hi"]):
            return "สวัสดีค่ะ ยูกิยินดีที่ได้รู้จักคุณ!"
        
        elif any(word in user_input_lower for word in ["ชื่อ", "name", "คุณคือใคร"]):
            return "ฉันชื่อยูกิค่ะ เป็นผู้ช่วย AI ที่พร้อมช่วยเหลือคุณ!"
        
        elif any(word in user_input_lower for word in ["ช่วย", "help", "ช่วยเหลือ"]):
            return "ยูกิสามารถช่วยคุณได้หลายอย่างค่ะ เช่น เปิดแอปพลิเคชัน เปิดเว็บไซต์ เล่นเพลง หรือตอบคำถามต่างๆ"
        
        elif any(word in user_input_lower for word in ["ขอบคุณ", "thank", "thanks"]):
            return "ยินดีค่ะ ยูกิยินดีช่วยเหลือคุณเสมอ!"
        
        elif any(word in user_input_lower for word in ["อาหาร", "food", "กิน", "แนะนำอาหาร"]):
            return "อาหารไทยมีหลากหลายและอร่อยมากค่ะ เช่น ต้มยำกุ้ง ผัดไทย ส้มตำ แกงเขียวหวาน ลาบ น้ำพริก และข้าวผัดกุ้ง"
        
        elif any(word in user_input_lower for word in ["ประเทศไทย", "thailand", "ไทย"]):
            return "ประเทศไทยเป็นประเทศที่สวยงามในเอเชียตะวันออกเฉียงใต้ มีวัฒนธรรมที่หลากหลาย อาหารอร่อย และผู้คนเป็นมิตรค่ะ"
        
        else:
            return "ขออภัยค่ะ ยูกิยังไม่เข้าใจคำถามนี้ แต่ยูกิสามารถช่วยคุณเปิดแอปพลิเคชัน เปิดเว็บไซต์ หรือเล่นเพลงได้ค่ะ"
    
    def _build_messages(self, user_input: str, context: str = "") -> List[Dict[str, str]]:
        """Build the messages array for the LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add context if provided
        if context:
            messages.append({
                "role": "system", 
                "content": f"Context: {context}"
            })
        
        # Add recent conversation history
        for msg in self.conversation_history[-self.context_window:]:
            messages.append(msg)
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages
    
    def _update_history(self, user_input: str, assistant_response: str):
        """Update conversation history"""
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # Keep only recent history to manage memory
        if len(self.conversation_history) > self.context_window * 2:
            self.conversation_history = self.conversation_history[-self.context_window * 2:]
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            response = requests.get(f"{self.ollama_url}/api/show", 
                                 json={"name": self.model_name}, 
                                 timeout=5)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {}


# Global LLM engine instance
llm_engine = LLMEngine()
