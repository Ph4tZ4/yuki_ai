# Yuki AI Migration Guide

## From Old Version (v1.0) to New Version (v2.0)

This guide helps you migrate from the old Windows-based Yuki AI to the new macOS-optimized version.

## What's New in v2.0

### 🎯 **Major Improvements**
- **Modern Architecture**: Complete rewrite with modular design
- **macOS Optimization**: Native support for macOS with proper application paths
- **Professional Structure**: Clean, maintainable codebase
- **Enhanced Features**: Better error handling, logging, and configuration
- **Cross-Platform**: Works on macOS, Windows, and Linux

### 🏗️ **New Project Structure**
```
yuki_ai/
├── src/                    # Main source code
│   ├── core/              # Core functionality
│   ├── commands/          # Command modules
│   ├── utils/             # Utilities
│   └── data/              # Configuration files
├── assets/                # Audio and media files
├── logs/                  # Application logs
├── tests/                 # Unit tests
├── config.yaml           # Main configuration
├── requirements.txt      # Dependencies
└── README.md            # Documentation
```

### 🔧 **Key Changes**

#### 1. **Configuration Management**
- **Old**: Hardcoded paths and settings
- **New**: YAML-based configuration with environment-specific settings

#### 2. **Application Paths**
- **Old**: Windows-specific paths (`C:/Program Files/...`)
- **New**: macOS paths (`/Applications/...`) with fallbacks

#### 3. **Voice Engine**
- **Old**: Basic speech recognition
- **New**: Enhanced voice engine with better error handling

#### 4. **Command Processing**
- **Old**: Monolithic command handling
- **New**: Modular command system with separate modules for different types

## Migration Steps

### 1. **Backup Your Old Project**
```bash
cp -r yuki_ai yuki_ai_backup_v1
```

### 2. **Install New Dependencies**
```bash
# Install system dependencies (macOS)
brew install portaudio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. **Configure Your Settings**
Edit `config.yaml` to customize:
- Application paths for your system
- Voice settings
- API keys (if needed)

### 4. **Test the Installation**
```bash
# Run basic tests
python3 test_basic.py

# Run demo (without voice)
python3 demo.py
```

### 5. **Start Yuki AI**
```bash
# Run the main application
python3 run.py
```

## Command Compatibility

### ✅ **Still Supported**
- "ยูกิ" (wake word)
- "ยูกิ สวัสดี" (greeting)
- "ยูกิ กี่โมงแล้ว" (time)
- "ยูกิ เปิด Google" (open websites)
- "ยูกิ เล่นเพลง [song]" (play music)
- "ยูกิ ค้นหา [query]" (search)
- "ยูกิ shutdown" (exit)

### 🆕 **New Commands**
- "ยูกิ เปิด VS Code" (open applications)
- "ยูกิ อากาศเป็นอย่างไร" (weather)
- "ยูกิ เปิด Spotify" (streaming services)
- System commands (CPU, memory, etc.)

## File Locations

### **Old Structure → New Structure**
- `yuki_ai.py` → `src/main.py`
- `commands.json` → `src/data/commands.json`
- `signal.mp3` → `assets/audio/signal.mp3`
- `output/` → `output/` (same location)

### **New Files**
- `config.yaml` - Main configuration
- `requirements.txt` - Dependencies
- `src/core/` - Core functionality
- `src/commands/` - Command modules
- `src/utils/` - Utilities
- `logs/` - Application logs

## Troubleshooting

### **Common Issues**

1. **Import Errors**
   ```bash
   # Make sure you're in the project root
   cd /path/to/yuki_ai
   python3 test_basic.py
   ```

2. **Audio Issues**
   ```bash
   # Install portaudio
   brew install portaudio
   
   # Check microphone permissions in System Preferences
   ```

3. **Permission Errors**
   ```bash
   # Make scripts executable
   chmod +x run.py
   chmod +x install.sh
   ```

### **Getting Help**
- Check the logs in `logs/yuki_ai.log`
- Run `python3 test_basic.py` to verify installation
- Review the README.md for detailed documentation

## Rollback

If you need to go back to the old version:
```bash
# Restore from backup
cp -r yuki_ai_backup_v1/* .
```

## Support

For issues or questions:
1. Check the logs in `logs/`
2. Run the test suite: `python3 test_basic.py`
3. Review the configuration in `config.yaml`
4. Check the README.md for detailed documentation

---

**Welcome to Yuki AI v2.0!** 🎉
