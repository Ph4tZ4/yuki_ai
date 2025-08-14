"""
System commands for Yuki AI
"""

import os
import subprocess
import psutil
from typing import Dict, List, Optional
from datetime import datetime

import sys
from pathlib import Path

# Add parent directories to path for imports
current_dir = Path(__file__).parent
utils_path = current_dir.parent / "utils"
sys.path.insert(0, str(utils_path))

from utils.config import config
from utils.logger import logger
from utils.helpers import is_macos, is_windows, format_time


class SystemCommands:
    """Handle system-related commands"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
    
    def process_command(self, command: str) -> str:
        """Process system-related commands"""
        command_lower = command.lower()
        
        # System information commands
        if self._is_system_info_command(command_lower):
            return self._handle_system_info_command(command)
        
        # System control commands
        if self._is_system_control_command(command_lower):
            return self._handle_system_control_command(command)
        
        # Process management commands
        if self._is_process_command(command_lower):
            return self._handle_process_command(command)
        
        # File system commands
        if self._is_file_command(command_lower):
            return self._handle_file_command(command)
        
        return "ไม่เข้าใจคำสั่งระบบค่ะ กรุณาลองใหม่อีกครั้ง"
    
    def _is_system_info_command(self, command: str) -> bool:
        """Check if command is for system information"""
        info_triggers = [
            "system info", "system information", "ข้อมูลระบบ",
            "cpu", "memory", "ram", "disk", "storage",
            "uptime", "เวลาทำงาน", "system status", "สถานะระบบ"
        ]
        return any(trigger in command for trigger in info_triggers)
    
    def _handle_system_info_command(self, command: str) -> str:
        """Handle system information commands"""
        if "cpu" in command or "memory" in command or "ram" in command:
            return self._get_system_resources()
        elif "disk" in command or "storage" in command:
            return self._get_disk_usage()
        elif "uptime" in command or "เวลาทำงาน" in command:
            return self._get_uptime()
        else:
            return self._get_full_system_info()
    
    def _is_system_control_command(self, command: str) -> bool:
        """Check if command is for system control"""
        control_triggers = [
            "shutdown", "restart", "reboot", "sleep", "hibernate",
            "ปิดเครื่อง", "รีสตาร์ท", "รีบูต", "สลีป", "ไฮเบอร์เนต"
        ]
        return any(trigger in command for trigger in control_triggers)
    
    def _handle_system_control_command(self, command: str) -> str:
        """Handle system control commands"""
        if "shutdown" in command or "ปิดเครื่อง" in command:
            return self._shutdown_system()
        elif "restart" in command or "reboot" in command or "รีสตาร์ท" in command or "รีบูต" in command:
            return self._restart_system()
        elif "sleep" in command or "สลีป" in command:
            return self._sleep_system()
        else:
            return "ไม่เข้าใจคำสั่งควบคุมระบบค่ะ"
    
    def _is_process_command(self, command: str) -> bool:
        """Check if command is for process management"""
        process_triggers = [
            "process", "task", "kill", "end", "terminate",
            "โปรเซส", "งาน", "ฆ่า", "จบ", "ยุติ"
        ]
        return any(trigger in command for trigger in process_triggers)
    
    def _handle_process_command(self, command: str) -> str:
        """Handle process management commands"""
        if "kill" in command or "end" in command or "terminate" in command:
            return self._kill_process(command)
        elif "process" in command or "task" in command:
            return self._list_processes()
        else:
            return "ไม่เข้าใจคำสั่งจัดการโปรเซสค่ะ"
    
    def _is_file_command(self, command: str) -> bool:
        """Check if command is for file operations"""
        file_triggers = [
            "file", "folder", "directory", "create", "delete", "copy", "move",
            "ไฟล์", "โฟลเดอร์", "ไดเรกทอรี", "สร้าง", "ลบ", "คัดลอก", "ย้าย"
        ]
        return any(trigger in command for trigger in file_triggers)
    
    def _handle_file_command(self, command: str) -> str:
        """Handle file operations"""
        if "create" in command or "สร้าง" in command:
            return self._create_file_or_folder(command)
        elif "delete" in command or "ลบ" in command:
            return self._delete_file_or_folder(command)
        else:
            return "ไม่เข้าใจคำสั่งจัดการไฟล์ค่ะ"
    
    def _get_system_resources(self) -> str:
        """Get CPU and memory usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024**3)  # GB
            memory_total = memory.total / (1024**3)  # GB
            
            return f"การใช้ CPU: {cpu_percent:.1f}% การใช้ RAM: {memory_percent:.1f}% ({memory_used:.1f}GB จาก {memory_total:.1f}GB)"
        except Exception as e:
            logger.error(f"Error getting system resources: {e}")
            return "ไม่สามารถดึงข้อมูลการใช้ทรัพยากรระบบได้ค่ะ"
    
    def _get_disk_usage(self) -> str:
        """Get disk usage information"""
        try:
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used / (1024**3)  # GB
            disk_total = disk.total / (1024**3)  # GB
            
            return f"การใช้พื้นที่ดิสก์: {disk_percent:.1f}% ({disk_used:.1f}GB จาก {disk_total:.1f}GB)"
        except Exception as e:
            logger.error(f"Error getting disk usage: {e}")
            return "ไม่สามารถดึงข้อมูลการใช้พื้นที่ดิสก์ได้ค่ะ"
    
    def _get_uptime(self) -> str:
        """Get system uptime"""
        try:
            import time
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_formatted = format_time(int(uptime_seconds))
            return f"ระบบทำงานมาแล้ว {uptime_formatted}"
        except Exception as e:
            logger.error(f"Error getting uptime: {e}")
            return "ไม่สามารถดึงข้อมูลเวลาทำงานของระบบได้ค่ะ"
    
    def _get_full_system_info(self) -> str:
        """Get full system information"""
        try:
            cpu_info = f"CPU: {psutil.cpu_count()} cores"
            memory_info = f"RAM: {psutil.virtual_memory().total / (1024**3):.1f}GB"
            disk_info = f"Disk: {psutil.disk_usage('/').total / (1024**3):.1f}GB"
            
            return f"ข้อมูลระบบ: {cpu_info}, {memory_info}, {disk_info}"
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return "ไม่สามารถดึงข้อมูลระบบได้ค่ะ"
    
    def _shutdown_system(self) -> str:
        """Shutdown the system"""
        try:
            if is_macos():
                subprocess.run(["sudo", "shutdown", "-h", "now"])
            elif is_windows():
                subprocess.run(["shutdown", "/s", "/t", "0"])
            else:
                subprocess.run(["sudo", "shutdown", "-h", "now"])
            
            return "กำลังปิดระบบค่ะ"
        except Exception as e:
            logger.error(f"Error shutting down system: {e}")
            return "ไม่สามารถปิดระบบได้ค่ะ"
    
    def _restart_system(self) -> str:
        """Restart the system"""
        try:
            if is_macos():
                subprocess.run(["sudo", "reboot"])
            elif is_windows():
                subprocess.run(["shutdown", "/r", "/t", "0"])
            else:
                subprocess.run(["sudo", "reboot"])
            
            return "กำลังรีสตาร์ทระบบค่ะ"
        except Exception as e:
            logger.error(f"Error restarting system: {e}")
            return "ไม่สามารถรีสตาร์ทระบบได้ค่ะ"
    
    def _sleep_system(self) -> str:
        """Put system to sleep"""
        try:
            if is_macos():
                subprocess.run(["pmset", "sleepnow"])
            elif is_windows():
                subprocess.run(["powercfg", "/hibernate", "off"])
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
            else:
                subprocess.run(["systemctl", "suspend"])
            
            return "กำลังเข้าสู่โหมดสลีปค่ะ"
        except Exception as e:
            logger.error(f"Error putting system to sleep: {e}")
            return "ไม่สามารถเข้าสู่โหมดสลีปได้ค่ะ"
    
    def _kill_process(self, command: str) -> str:
        """Kill a process"""
        # This is a simplified implementation
        # In a real system, you'd want to extract the process name from the command
        return "การฆ่าโปรเซสต้องระบุชื่อโปรเซสที่ต้องการค่ะ"
    
    def _list_processes(self) -> str:
        """List running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
            
            # Return top 5 processes
            top_processes = processes[:5]
            result = "โปรเซสที่ใช้ทรัพยากรมากที่สุด:\n"
            for proc in top_processes:
                result += f"- {proc['name']}: CPU {proc['cpu_percent']:.1f}%, RAM {proc['memory_percent']:.1f}%\n"
            
            return result
        except Exception as e:
            logger.error(f"Error listing processes: {e}")
            return "ไม่สามารถแสดงรายการโปรเซสได้ค่ะ"
    
    def _create_file_or_folder(self, command: str) -> str:
        """Create a file or folder"""
        # This is a simplified implementation
        return "การสร้างไฟล์หรือโฟลเดอร์ต้องระบุชื่อและตำแหน่งค่ะ"
    
    def _delete_file_or_folder(self, command: str) -> str:
        """Delete a file or folder"""
        # This is a simplified implementation
        return "การลบไฟล์หรือโฟลเดอร์ต้องระบุชื่อและตำแหน่งค่ะ"
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get basic system information"""
        return {
            "platform": "macOS" if is_macos() else "Windows" if is_windows() else "Linux",
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
            "architecture": os.sys.platform
        }
