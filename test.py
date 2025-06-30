import os
import speech_recognition as sr
from gtts import gTTS
import pywhatkit
from datetime import datetime
import webbrowser
import json
import subprocess
import re
import logging
import serial
import time
import urllib.request

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Initialize serial communication
# arduino = serial.Serial('', 9600, timeout=1)

# def send_command_to_arduino(command):
#     if arduino.is_open:
#         arduino.write(f"{command}\n".encode())
        
# Function to play sound
def play_sound(file_path):
    if os.path.exists(file_path):
        try:
            from playsound import playsound
            playsound(file_path)
        except Exception as e:
            logging.error(f"Error playing sound {file_path}: {e}")
    else:
        logging.error(f"{file_path} not found!")

# Function to load commands from a JSON file
def load_commands(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                logging.error("Invalid JSON in commands file.")
                return {}
    else:
        logging.error(f"{file_path} not found.")
        return {}

# Function to save commands to a JSON file
def save_commands(file_path, commands):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(commands, file, ensure_ascii=False, indent=4)

# Function to process text
def process_text(text):
    if "ผม" in text:
        text = text.replace("ผม", "ฉันเองก็")
    if "ครับ" in text:
        text = text.replace("ครับ", "ค่ะ")
    return text

# Text-to-speech and audio playback
def speak(response):
    try:
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        # Clean up old audio files
        for file in os.listdir(output_dir):
            os.remove(os.path.join(output_dir, file))
        tts = gTTS(text=response, lang='th')
        file_path = os.path.join(output_dir, "response.mp3")
        tts.save(file_path)
        play_sound(file_path)
    except Exception as e:
        logging.error(f"Error in speak function: {e}")

# Helper function to open applications
def open_application(app_path, app_name):
    try:
        subprocess.Popen([app_path])
        return f"เปิด {app_name} แล้วค่ะ"
    except Exception as e:
        logging.error(f"Error opening {app_name}: {e}")
        return f"เกิดข้อผิดพลาดในการเปิด {app_name}"

# Function to execute commands
def execute_command(text, commands):
    global response
    response = ""
    text = text.lower()  # Convert text to lowercase for case-insensitive matching
    
    # Check for weather-related commands
    weather_commands = ["อากาศเป็นอย่างไร", "เช็คสภาพอากาศ", "เช็คพยากรณ์อากาศ", "weather"]
    for command in weather_commands:
        if command in text:
            response = get_weather()
            break
    
    # Specific response handling for "ยูกิ / Yuki"
    if text.strip().lower() in ["ยูกิ", "yuki"]:
        yuki_responses = [
            "ค่ะ ยูกิอยู่นี่ค่ะ",
            "เรียกใช้ยูกิได้เลยค่ะ",
            "ยูกิพร้อมช่วยเหลือค่ะ",
            "นี่!! ตั้งใจแกล้งกันรึป่าวคะ?",
            "แบบนี้แกล้งกันชัด ๆ เลย!!!"
        ]
        call_count_path = "yuki_call_count.json"

        if os.path.exists(call_count_path):
            with open(call_count_path, 'r') as file:
                call_count = json.load(file).get("count", 0)
        else:
            call_count = 0

        call_count = (call_count + 1) % 6

        if call_count < 5:
            response = yuki_responses[call_count]
        else:
            response = "ถ้าไม่อยากคุยกับยูกิแล้วให้พูดว่า 'ยูกิ shutdown' นะคะ มาเรียกแล้วไม่พูดแบบนี้ยูกิก็เสียใจ"

        with open(call_count_path, 'w') as file:
            json.dump({"count": call_count}, file)
        return response
    elif not text.startswith("ยูกิ") and text not in ["สวัสดี", "ชื่ออะไร", "คุณคือใคร", "สวัสดีครับ", "สวัสดีค่ะ", "หวัดดี", "เธอคือใคร", "hello", "hi", "คุณชื่ออะไร", "เธอชื่ออะไร", "สวัสดียูกิ", "ยูกิสวัสดี", "กี่โมงแล้ว", "เวลาตอนนี้คือ", "ตอนนี้เวลาเท่าไหร่"]:
        response = "..."
        return response

    # Remove "yuki " prefix for actual command processing
    if text.startswith("ยูกิ"):
        text = text[len("ยูกิ"):].strip()

    # Check predefined commands first
    for command, action in commands.items():
        if re.search(command, text):  # Use regex search for flexible matching
            try:
                if action == "time":
                    now = datetime.now()
                    response = f"ขณะนี้เวลา {now.hour} นาฬิกา {now.minute} นาที {now.second} วินาที"
                elif action == "greeting":
                    response = "สวัสดีค่ะ มีอะไรให้ช่วยไหมคะ?"
                elif action == "name":
                    response = "ฉันคือผู้ช่วยอัจฉริยะของคุณค่ะ"
                elif action.startswith("open_"):
                    program_path = action.split("_", 1)[1]
                    response = open_application(program_path, command.split(' ', 1)[1])
                elif action.startswith("close_"):
                    program_name = action.split("_", 1)[1]
                    os.system(f'taskkill /im {program_name} /f')
                    response = f"ปิด {command.split(' ', 1)[1]} แล้วค่ะ"
                elif action == "shutdown":
                    response = "ยูกิกำลังปิดตัวลงค่ะ"
                    speak(response)
                    os._exit(0)
                else:
                    response = action
            except Exception as e:
                logging.error(f"Error executing command {command}: {e}")
            break

    # Open Google 
    google_open = ["เปิด google", "เข้าเว็บ google", "google", "open google", "เข้า google"]
    for command in google_open:
        if command in text and not any(cmd in text for cmd in ["และพิมพ์ว่า", "and search", "google map", "map", "ai"]):
            webbrowser.open("https://www.google.com")
            response = "เปิด Google แล้วค่ะ"
            break

    # Handle flexible Google search commands
    google_search_commands = ["ค้นหาว่า", "search ว่า", "Search that", "เสิร์ชว่า"]
    for command in google_search_commands:
        if command in text:
            query = re.sub("|".join(map(re.escape, google_search_commands)), "", text).strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            response = f"ค้นหา {query} บน Google แล้วค่ะ"
            break
    
    # Open YouTube without search
    youtube_open = ["เปิด youtube", "เข้าเว็บ youtube", "youtube", "open youtube", "เข้า youtube"]
    for command in youtube_open:
        if command in text and not any(cmd in text for cmd in ["และพิมพ์ว่า", "and search"]):
            webbrowser.open("https://www.youtube.com/")
            response = "เปิด YouTube แล้วค่ะ"
            break
        
    # Open IG
    ig_open = ["เปิด ig", "เข้าเว็บ ig", "ig", "open ig", "เข้า ig"]
    for command in ig_open:
        if command in text and not any(cmd in text for cmd in ["และพิมพ์ว่า", "and search"]):
            webbrowser.open("https://www.instagram.com/")
            response = "เปิด Instagram แล้วค่ะ"
            break
    
    # Open Facebook
    fb_open = ["เปิด facebook", "เข้าเว็บ facebook", "facebook", "open facebook", "เข้า facebook"]
    for command in fb_open:
        if command in text and not any(cmd in text for cmd in ["และพิมพ์ว่า", "and search"]):
            webbrowser.open("https://www.facebook.com")
            response = "เปิด Facebook แล้วค่ะ"
            break
            
    # Open Steam
    steam_open = ["เปิด steam", "open steam", "เปิดสตรีม"]
    for command in steam_open:
        if command in text:
            response = open_application("C:/Program Files (x86)/Steam/steam.exe", "Steam")
            break
    
    # Open Epic Games
    epic_open = ["เปิด epic", "open epic", "เปิด epic game"]
    for command in epic_open:
        if command in text:
            response = open_application("C:/Program Files (x86)/Epic Games/Launcher/Portal/Binaries/Win64/EpicGamesLauncher.exe", "Epic Games")
            break
    
    # Open Minecraft
    minecraft_open = ["เปิด minecraft", "open minecraft", "minecraft"]
    for command in minecraft_open:
        if command in text:
            response = open_application("C:/XboxGames/Minecraft Launcher/Content/gamelaunchhelper.exe", "Minecraft")
            break
        
    # Open OBS
    obs_open = ["เปิด obs", "open obs", "obs"]
    for command in obs_open:
        if command in text:
            response = open_application("D:/obs-studio/bin/64bit/obs64.exe", "OBS")
            break
    
    # Open VS Code
    vscode_open = ["เปิด vscode", "open vscode", "vscode", "เปิด vs code", "เปิด vs Code", "เปิด VS Code", "เปิด VS code"]
    for command in vscode_open:
        if command in text:
            response = open_application("C:/Users/PHACPHAI/AppData/Local/Programs/Microsoft VS Code/Code.exe", "VS Code")
            break
    
    # Open Line
    line_open = ["เปิด line", "เปิด LINE", "เข้า LINE", "open line", "เข้า line", "open LINE"]
    for command in line_open:
        if command in text and not any(cmd in text for cmd in ["และพิมพ์ว่า", "and search"]):
            response = open_application("C:/Users/PHACPHAI/AppData/Local/LINE/bin/LineLauncher.exe", "Line")
            break
    
    # Open EA
    ea_open = ["เปิด ea", "open ea", "ea", "เปิด e a", "open e a"]
    for command in ea_open:
        if command in text:
            response = open_application("C:/Program Files/Electronic Arts/EA Desktop/EA Desktop/EALauncher.exe", "EA")
            break
        
    # Open Power BI
    powerbi_open = ["เปิด power bi", "open power bi", "power bi"]
    for command in powerbi_open:
        if command in text:
            response = open_application("D:/Microsoft Power BI Desktop/bin/PBIDesktop.exe", "Power BI")
            break
        
    # Open PR
    pr_open = ["เปิด premiere pro", "open premiere pro", "premiere pro"]
    for command in pr_open:
        if command in text:
            response = open_application("C:/Program Files/Adobe/Adobe Premiere Pro 2024/Adobe Premiere Pro.exe", "Premiere Pro")
            break
    
    # Open Discord
    discord_open = ["เปิด discord", "open discord", "discord"]
    for command in discord_open:
        if command in text:
            response = open_application("C:/Users/PHACPHAI/AppData/Local/Discord/Update.exe", "Discord")
            break
        
    # Open Canva
    canva_open = ["เปิด canva", "open canva", "canva"]
    for command in canva_open:
        if command in text:
            response = open_application("C:/Users/PHACPHAI/AppData/Local/Programs/Canva/Canva.exe", "Canva")
            break
    
    # Open Arduino IDE
    arduino_open = ["เปิด arduino ide", "open arduino ide", "arduino ide"]
    for command in arduino_open:
        if command in text:
            response = open_application("C:/Program Files/Arduino IDE/Arduino IDE.exe", "Arduino IDE")
            break

    # Open Logitech G HUB
    logitech_hub_open = ["เปิด logitech g hub", "open logitech g hub", "เปิด logitech"]
    for command in logitech_hub_open:
        if command in text:
            response = open_application("C:/Program Files/LGHUB/system_tray/lghub_system_tray.exe", "Logitech G HUB")
            break

    # Open Audacity
    audacity_open = ["เปิด audacity", "open audacity", "audacity"]
    for command in audacity_open:
        if command in text:
            response = open_application("C:/Program Files/Audacity/Audacity.exe", "Audacity")
            break

    # Open Clip Studio Paint
    clip_studio_open = ["เปิด clip studio paint", "open clip studio paint", "clip studio paint"]
    for command in clip_studio_open:
        if command in text:
            response = open_application("C:/Program Files/CELSYS/CLIP STUDIO 1_5/CLIPStudioPaint.exe", "Clip Studio Paint")
            break
        
    # Open Google Maps
    google_maps_open = ["เปิด google map", "open google map", "google map"]
    for command in google_maps_open:
        if command in text and not any(cmd in text for cmd in ["และพิมพ์ว่า", "and search"]):
            webbrowser.open("https://www.google.co.th/maps")
            response = "เปิด Google Maps แล้วค่ะ"
            break
        
    # Open Google Maps and search
    google_maps_open_and_type = ["เปิด google map และพิมพ์ว่า", "open google map and search", "เข้าเว็บ google map และพิมพ์ว่า", "เปิด google map และ search ว่า", "เข้าเว็บ google map และ search ว่า", "ต้องการไปที", "ปักหมุดไปที", "ปักหมุดที่", "อยากไป", "อยากไปที่"]
    for command in google_maps_open_and_type:
        if command in text:
            query = re.sub("|".join(map(re.escape, google_maps_open_and_type)), "", text).strip()
            webbrowser.open(f"https://www.google.co.th/maps/search/{query}")
            response = f"ค้นหา {query} บน Google Maps แล้วค่ะ"
            break

    # Open YouTube and search
    youtube_open_and_type = ["เปิด youtube และพิมพ์ว่า", "เข้าเว็บ youtube และพิมพ์ว่า", "open youtube and search", "เข้า youtube และพิมพ์ว่า", "เปิด youtube และ search ว่า", "เข้าเว็บ youtube และ search ว่า", "เข้า youtube และ search ว่า"]
    for command in youtube_open_and_type:
        if command in text:
            query = re.sub("|".join(map(re.escape, youtube_open_and_type)), "", text).strip()
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            response = f"ค้นหา {query} บน YouTube แล้วค่ะ"
            break
        
    # Open ChatGPT
    chatgpt_open = ["เปิด chatgpt", "open chatgpt", "chatgpt", "เปิดแชท gpt", "เปิด แชท gpt", "เปิดเชทจีพีที"]
    for command in chatgpt_open:
        if command in text:
            webbrowser.open("https://chatgpt.com")
            response = "เปิด ChatGPT แล้วค่ะ"
            break
        
    # Open Meet
    meet_open = ["เปิด meet", "open meet", "meet", "เปิดมีท", "openไมท์", "มีท"]
    for command in meet_open:
        if command in text:
            webbrowser.open("https://meet.google.com/")
            response = "เปิด Meet แล้วค่ะ"
            break
        
    # Open Spotify
    spotify_open = ["เปิด spotify", "open spotify", "spotify", "เปิดสโพที", "open spotify playlists", "สโพที", "เปิดสโพทีเพลส", "open spotify playlists"]
    for command in spotify_open:
        if command in text:
            webbrowser.open("https://open.spotify.com/")
            response = "เปิด Spotify แล้วค่ะ"
            break
    
    # Open Netflix
    netflix_open = ["เปิด netflix", "open netflix", "netflix", "เปิดเน็ตฟลิกซ์", "open netflix movies", "เน็ตฟลิกซ์", "เปิดเน็ตฟลิกซ์หนัง", "open netflix movies"]
    for command in netflix_open:
        if command in text:
            webbrowser.open("https://www.netflix.com/browse")
            response = "เปิด Netflix แล้วค่ะ"
            break
        
    # Open Gemini
    gemini_open = ["เปิด gemini", "open gemini", "gemini", "เปิดจีมินิ", "เปิดเจมินี้", "เปิดเจมิไนย์", "เปิด google ai", "เปิด ai google"]
    for command in gemini_open:
        if command in text:
            webbrowser.open("https://gemini.google.com/app")
            response = "เปิด Gemini แล้วค่ะ"
            break

    # Handle flexible YouTube search commands and play specific songs
    youtube_search_commands = ["เล่นเพลง", "อยากฟัง", "เรื่องราว", "เรื่องเล่า", "ดู", "เล่น", "play music", "stories", "watch", "play", "อยากฟังเพลงของ", "อยากฟังเพลง", "อยากดูคลิป"]
    for command in youtube_search_commands:
        if command in text:
            query = re.sub("|".join(map(re.escape, youtube_search_commands)), "", text).strip()
            if "ของ" in query:
                artist = query.split("ของ")[-1].strip()
                pywhatkit.playonyt(artist)
                response = f"เล่น YouTube ของ {artist} แล้วค่ะ"
            else:
                pywhatkit.playonyt(query)
                response = f"เล่น {query} บน YouTube แล้วค่ะ"
            break

    # Open any website with the command "เปิด [something]" or "open [something]"
    match = re.search(r"เปิดเว็บ (.+)|open website (.+)", text)
    if match:
        query = match.group(1) or match.group(2)
        url = f"https://{query.replace(' ', '')}.com"
        try:
            webbrowser.open(url)
            response = f"เปิดเว็บไซต์ {query} แล้วค่ะ"
        except Exception as e:
            response = f"ไม่สามารถเปิดเว็บไซต์ {query} ได้ค่ะ"
            logging.error(f"Error opening website {query}: {e}")
            
    send_command_to_arduino("DONE")

    return response

# Weather
def get_weather():
    try:
        ResultBytes = urllib.request.urlopen("https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/thailand?unitGroup=metric&include=days&key=GSFRJ7UZCS6G98FWSJPNX7EAL&contentType=json")
        jsonData = json.load(ResultBytes)
        
        # Extract relevant weather information
        current_conditions = jsonData['days'][0]['temp']
        condition_desc = jsonData['days'][0]['conditions']
        
        return f"อุณหภูมิปัจจุบันในประเทศไทยคือ {current_conditions} องศาเซลเซียส และสภาพอากาศ {condition_desc} ค่ะ"
    except urllib.error.HTTPError as e:
        logging.error(f"HTTP Error: {e.code} - {e.read().decode()}")
        return "เกิดข้อผิดพลาดในการเชื่อมต่อกับบริการสภาพอากาศค่ะ"
    except urllib.error.URLError as e:
        logging.error(f"URL Error: {e.reason}")
        return "ไม่สามารถเชื่อมต่อกับบริการสภาพอากาศได้ค่ะ"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "เกิดข้อผิดพลาดในการดึงข้อมูลสภาพอากาศค่ะ"

# Main function
def main():
    speak("เรียกชื่อ ยูกิ ทุกครั้งก่อนสั่งการนะคะ")
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    play_sound("./signal.mp3")
    send_command_to_arduino("LISTENING")
    print("ยูกิกำลังฟังค่ะ...")
    speak("ยูกิกำลังฟังค่ะ")

    last_error = None  # Track the last error

    while True:
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
            try:
                command_text = recognizer.recognize_google(audio, language="th-TH")
                print(f"คุณพูดว่า : {command_text}")
                command_text = process_text(command_text)
                response = execute_command(command_text, load_commands("commands.json"))
                print(f"ยูกิ     : {response}")
                speak(response)
                send_command_to_arduino("DONE")
                send_command_to_arduino("LISTENING")
                print("ยูกิกำลังฟังค่ะ...")
                last_error = None  # Reset the error tracker

            except sr.UnknownValueError:
                if last_error != "UnknownValueError" and not response:  # Check if the response is empty before showing error
                    print("ขอโทษค่ะ ฉันไม่เข้าใจที่คุณพูด")
                    speak("ขอโทษค่ะ ฉันไม่เข้าใจที่คุณพูด")
                    send_command_to_arduino("ERROR")
                    send_command_to_arduino("LISTENING")
                    print("ยูกิกำลังฟังค่ะ...")
                last_error = "UnknownValueError"  # Set the last error to track it

            except sr.RequestError as e:
                print(f"เกิดข้อผิดพลาดในการติดต่อ Google Speech Recognition service: {e}")
                send_command_to_arduino("ERROR")
                last_error = None  # Reset the error tracker


print("-----------------------------")
if __name__ == "__main__":
    main()
