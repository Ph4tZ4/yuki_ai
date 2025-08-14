#!/usr/bin/env python3
"""
Setup script for LLM integration with Yuki AI
"""

import os
import sys
import subprocess
import platform
import requests
from pathlib import Path

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], 
                              capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def install_ollama():
    """Install Ollama based on the platform"""
    system = platform.system().lower()
    
    print("Installing Ollama...")
    
    if system == "darwin":  # macOS
        print("Installing Ollama on macOS...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                         shell=True, check=True)
            print("✅ Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Ollama: {e}")
            return False
    
    elif system == "linux":
        print("Installing Ollama on Linux...")
        try:
            subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh', '|', 'sh'], 
                         shell=True, check=True)
            print("✅ Ollama installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Ollama: {e}")
            return False
    
    elif system == "windows":
        print("For Windows, please install Ollama manually:")
        print("1. Visit: https://ollama.ai/download")
        print("2. Download and install the Windows version")
        print("3. Run this script again after installation")
        return False
    
    else:
        print(f"❌ Unsupported operating system: {system}")
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def start_ollama():
    """Start Ollama service"""
    print("Starting Ollama service...")
    try:
        # Start Ollama in the background
        subprocess.Popen(['ollama', 'serve'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        # Wait a moment for it to start
        import time
        time.sleep(3)
        
        if check_ollama_running():
            print("✅ Ollama service started successfully!")
            return True
        else:
            print("❌ Failed to start Ollama service")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def download_model(model_name="llama3.2:1b"):
    """Download a mini LLM model"""
    print(f"Downloading model: {model_name}")
    print("This may take a few minutes depending on your internet connection...")
    
    try:
        result = subprocess.run(['ollama', 'pull', model_name], 
                              capture_output=True, text=True, timeout=600)  # 10 minutes timeout
        
        if result.returncode == 0:
            print(f"✅ Model {model_name} downloaded successfully!")
            return True
        else:
            print(f"❌ Failed to download model: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Download timed out. Please try again.")
        return False
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def list_available_models():
    """List available mini LLM models"""
    models = [
        {"name": "llama3.2:1b", "size": "~1GB", "description": "Fast and efficient 1B parameter model"},
        {"name": "phi3:mini", "size": "~1.5GB", "description": "Microsoft's Phi-3 Mini model"},
        {"name": "qwen2.5:0.5b", "size": "~0.5GB", "description": "Very small and fast model"},
        {"name": "gemma2:2b", "size": "~2GB", "description": "Google's Gemma 2B model"},
        {"name": "mistral:7b-instruct", "size": "~4GB", "description": "Larger but more capable model"}
    ]
    
    print("\nAvailable Mini/Nano LLM Models:")
    print("=" * 50)
    for model in models:
        print(f"📦 {model['name']}")
        print(f"   Size: {model['size']}")
        print(f"   Description: {model['description']}")
        print()

def test_llm_integration():
    """Test the LLM integration"""
    print("Testing LLM integration...")
    
    try:
        # Add src to path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from core.llm_engine import llm_engine
        
        if llm_engine.is_available():
            print("✅ LLM integration working!")
            
            # Test a simple conversation
            response = llm_engine.generate_response("สวัสดี ยูกิ")
            print(f"Test response: {response}")
            
            return True
        else:
            print("❌ LLM integration not working")
            return False
            
    except Exception as e:
        print(f"❌ Error testing LLM integration: {e}")
        return False

def main():
    """Main setup function"""
    print("🤖 Yuki AI - LLM Setup")
    print("=" * 30)
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("❌ Ollama is not installed")
        choice = input("Would you like to install Ollama? (y/n): ").lower()
        if choice == 'y':
            if not install_ollama():
                return
        else:
            print("Please install Ollama manually and run this script again.")
            return
    
    print("✅ Ollama is installed")
    
    # Check if Ollama is running
    if not check_ollama_running():
        print("❌ Ollama service is not running")
        if not start_ollama():
            return
    
    print("✅ Ollama service is running")
    
    # List available models
    list_available_models()
    
    # Ask user which model to download
    model_choice = input("\nWhich model would you like to download? (default: llama3.2:1b): ").strip()
    if not model_choice:
        model_choice = "llama3.2:1b"
    
    # Download the model
    if download_model(model_choice):
        print(f"✅ Setup completed! Model {model_choice} is ready to use.")
        
        # Update config with the chosen model
        try:
            import yaml
            config_path = Path(__file__).parent / "config.yaml"
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            config['llm']['model_name'] = model_choice
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            print("✅ Configuration updated!")
            
        except Exception as e:
            print(f"⚠️  Could not update config: {e}")
        
        # Test integration
        print("\nTesting integration...")
        test_llm_integration()
        
    else:
        print("❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main()
