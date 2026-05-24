import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import requests
import json
import sys
import threading
import time
import os
import tempfile
import asyncio
import edge_tts
import pygame
import pyautogui
import pygetwindow as gw
import base64
import re
import subprocess
import ctypes
from io import BytesIO

# Gesture control module
try:
    from gesture_control import (start_gesture_control, stop_gesture_control,
                                  is_gesture_active, add_custom_gesture,
                                  remove_custom_gesture, get_gesture_list,
                                  get_available_actions, parse_finger_pattern,
                                  AVAILABLE_ACTIONS)
    GESTURE_CONTROL_AVAILABLE = True
except ImportError:
    GESTURE_CONTROL_AVAILABLE = False
    print("[Warning: Gesture control not available - install mediapipe, opencv-python]")
# Helper for Antigravity (Temporary separate file import or I will paste content)
# For now, I will paste the content directly into CHAOS.py to keep it single-file as requested.

# Volume control imports (Windows)
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    VOLUME_CONTROL_AVAILABLE = True
except ImportError:
    VOLUME_CONTROL_AVAILABLE = False
    print("[Warning: Volume control not available - install pycaw]")

#copy paste this line in the terminal to make CHAOS run
# & "$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe" "c:\Users\User\OneDrive\Documents\STUDY\PROJECT C.H.A.O.S\CHAOS.py" 
# Ollama API settings
ollama_api_url = "http://localhost:11434/api/chat"
ollama_model = "llama3.2" # Switched to faster, reliable model
ollama_vision_model = "llava"  # Vision model for screen analysis

# Initialize pygame mixer for audio playback
pygame.mixer.init()

# Initialize pyttsx3 as backup
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 175)

# Edge TTS voice settings - Expanded with natural-sounding voices
VOICE_MAP = {
    # ===== BUTLER / JARVIS STYLE =====
    'butler': "en-GB-RyanNeural",       # British male - formal, butler-like, very polished
    'jarvis': "en-US-GuyNeural",        # Classic JARVIS AI assistant voice
    'alfred': "en-GB-RyanNeural",       # Batman's butler style
    'friday': "en-US-JennyNeural",      # Like Iron Man's FRIDAY AI (female)
    
    # ===== MOST NATURAL MALE VOICES =====
    'american': "en-US-GuyNeural",      # Standard American male
    'american male': "en-US-ChristopherNeural",  # Very natural American male
    'davis': "en-US-DavisNeural",       # Casual, friendly American male
    'tony': "en-US-TonyNeural",         # Conversational American male
    'jason': "en-US-JasonNeural",       # Clear, professional American male
    'british male': "en-GB-RyanNeural", # Refined British male (butler voice)
    'australian male': "en-AU-WilliamNeural",  # Australian male
    'irish': "en-IE-ConnorNeural",      # Irish male accent
    
    # ===== MOST NATURAL FEMALE VOICES =====
    'female': "en-US-JennyNeural",      # Most natural American female
    'american female': "en-US-AriaNeural",  # Expressive American female
    'emma': "en-US-EmmaNeural",         # Warm, friendly female
    'sara': "en-US-SaraNeural",         # Professional female
    'british female': "en-GB-SoniaNeural",  # British female
    'british': "en-GB-SoniaNeural",     # British female
    'australian female': "en-AU-NatashaNeural",  # Australian female
    
    # ===== NARRATOR / STORYTELLER VOICES =====
    'narrator': "en-US-DavisNeural",    # Great for storytelling
    'storyteller': "en-GB-RyanNeural",  # British narration style
    'newsreader': "en-US-ChristopherNeural",  # News anchor style
    'documentary': "en-GB-RyanNeural",  # Documentary narrator
    
    # ===== REGIONAL ACCENTS =====
    'uk': "en-GB-RyanNeural",
    'australian': "en-AU-WilliamNeural",
    'indian': "en-IN-PrabhatNeural",    # Indian English male
    'indian female': "en-IN-NeerjaNeural",  # Indian English female
    'south african': "en-ZA-LeahNeural",  # South African English
    'canadian': "en-CA-LiamNeural",     # Canadian English
    'irish female': "en-IE-EmilyNeural",  # Irish female
    
    # ===== NON-ENGLISH LANGUAGES =====
    'french': "fr-FR-HenriNeural",      # French male (more natural)
    'french female': "fr-FR-DeniseNeural",
    'german': "de-DE-ConradNeural",     # German male
    'spanish': "es-ES-AlvaroNeural",    # Spanish male
    'italian': "it-IT-DiegoNeural",     # Italian male
    'japanese': "ja-JP-KeitaNeural",    # Japanese male
    'korean': "ko-KR-InJoonNeural",     # Korean male
    'chinese': "zh-CN-YunxiNeural",     # Chinese male
    'arabic': "ar-SA-HamedNeural",      # Arabic male
    
    # ===== URDU / HINDI =====
    'urdu': "ur-PK-AsadNeural",
    'urdu male': "ur-PK-AsadNeural",
    'urdu female': "ur-PK-UzmaNeural",
    'pakistani': "ur-PK-AsadNeural",
    'hindi': "hi-IN-MadhurNeural",      # Hindi male
    'hindi female': "hi-IN-SwaraNeural",
    
    # ===== PERSONALITY PRESETS =====
    'professional': "en-US-ChristopherNeural",
    'casual': "en-US-DavisNeural",
    'friendly': "en-US-JennyNeural",
    'formal': "en-GB-RyanNeural",       # Butler voice
    'warm': "en-US-EmmaNeural",
    'calm': "en-GB-RyanNeural",
    'energetic': "en-US-TonyNeural",
    
    # ===== FUN PERSONALITY PRESETS =====
    'wise': "en-GB-RyanNeural",         # Wise mentor figure
    'mentor': "en-GB-RyanNeural",       # Guiding mentor
    'villain': "en-US-GuyNeural",       # Deep, menacing
    'hero': "en-US-ChristopherNeural",  # Heroic, confident
    'mysterious': "en-GB-RyanNeural",   # Enigmatic
    'sarcastic': "en-US-TonyNeural",    # Witty and dry
    'dramatic': "en-US-DavisNeural",    # Over-the-top
    'chill': "en-US-DavisNeural",       # Super relaxed
    'excited': "en-US-TonyNeural",      # High energy
    'royal': "en-GB-RyanNeural",        # Regal, aristocratic
    'knight': "en-GB-RyanNeural",       # Noble knight
    'wizard': "en-GB-RyanNeural",       # Mystical sage
    'tech': "en-US-GuyNeural",          # Tech/sci-fi AI
    'robot': "en-US-GuyNeural",         # Robotic AI
    'computer': "en-US-GuyNeural",      # Classic computer
    'spy': "en-GB-RyanNeural",          # Secret agent handler
    'commander': "en-US-ChristopherNeural",  # Military commander
    'captain': "en-US-ChristopherNeural",    # Ship captain
    'professor': "en-GB-RyanNeural",    # Academic professor
    'doctor': "en-US-ChristopherNeural", # Medical professional
    'therapist': "en-US-JennyNeural",   # Calm, understanding
    'coach': "en-US-TonyNeural",        # Motivational coach
    'pirate': "en-AU-WilliamNeural",    # Arrr matey!
    'cowboy': "en-US-DavisNeural",      # Western drawl
    'gentleman': "en-GB-RyanNeural",    # Refined gentleman
    'lady': "en-GB-SoniaNeural",        # Elegant lady
    'queen': "en-GB-SoniaNeural",       # Royal female
    'king': "en-GB-RyanNeural",         # Royal male
    'soldier': "en-US-ChristopherNeural", # Military
    'navigator': "en-GB-RyanNeural",    # Ship navigator
    'oracle': "en-GB-RyanNeural",       # All-knowing
    'sage': "en-GB-RyanNeural",         # Wise elder
    'scholar': "en-GB-RyanNeural",      # Learned academic
    'poet': "en-GB-RyanNeural",         # Artistic, flowing
    'bard': "en-IE-ConnorNeural",       # Irish storyteller
    'guardian': "en-GB-RyanNeural",     # Protective figure
    'sensei': "en-GB-RyanNeural",       # Martial arts master
    'hacker': "en-US-GuyNeural",        # Cyberpunk hacker
    'gamer': "en-US-TonyNeural",        # Gaming buddy
    'streamer': "en-US-DavisNeural",    # Content creator
    'dj': "en-US-TonyNeural",           # Radio DJ energy
    
    # ===== CUTE / ANIME / EGIRL STYLE =====
    'egirl': "en-US-AriaNeural",        # Cute, expressive egirl uwu~
    'eboy': "en-US-TonyNeural",         # Chill eboy energy
    'anime': "en-US-AriaNeural",        # Anime girl style
    'kawaii': "en-US-AriaNeural",       # Super cute Japanese style
    'uwu': "en-US-AriaNeural",          # uwu energy
    'cute': "en-US-AriaNeural",         # Cutesy voice
    'bubbly': "en-US-JennyNeural",      # Bubbly, happy
    'sweet': "en-US-EmmaNeural",        # Sweet and soft
    'soft': "en-US-EmmaNeural",         # Soft spoken
    'girly': "en-US-AriaNeural",        # Girly voice
    'sassy': "en-US-AriaNeural",        # Sassy attitude
    'tsundere': "en-US-AriaNeural",     # It's not like I wanted to help you or anything!
    'yandere': "en-US-AriaNeural",      # Obsessively sweet
    'waifu': "en-US-AriaNeural",        # Waifu material
    'gamer girl': "en-US-AriaNeural",   # Gamer girl
    'vtuber': "en-US-AriaNeural",       # VTuber style
    
    # ===== LEGACY / ALIASES =====
    'english': "en-US-GuyNeural",
    'us': "en-US-GuyNeural",
    'male': "en-US-GuyNeural",
    'default': "en-GB-RyanNeural",      # Butler is now default
}

# Default Active Voice - Butler for that refined AI assistant feel
current_voice = VOICE_MAP['butler']

# Global flags for interruption handling
is_speaking = False
interrupt_flag = False
interrupted_text = None

# Voice mode flag (True = speak responses, False = text only)
voice_mode = True

# Awake state (True = listening to all commands, False = Waiting for wake word)
is_awake = True

# Current detected language from user speech
current_language = 'en'  # 'en' for English, 'ur' for Urdu

# Urdu mode flag - when True, accepts Roman Urdu input and speaks Urdu
urdu_mode = False

# Type input mode - when True, accepts typed commands instead of voice
type_input_mode = False

# Antigravity self-update state
pending_antigravity_request = None  # Stores the feature request waiting for confirmation
awaiting_confirmation = False  # True when waiting for user to confirm
last_antigravity_prompt = None  # Last prompt sent to Antigravity

# Context tracking for pronoun resolution ("it", "that", etc.)
last_context = None  # Stores the last meaningful context (screenshot path, file name, etc.)

# Ollama AI toggle - when False, CHAOS won't consult AI brain
ollama_enabled = True

# Conversation context for follow-up questions (remembers last few exchanges)
conversation_context = []  # List of {"role": "user"/"assistant", "content": "..."}
MAX_CONTEXT_MESSAGES = 10  # Remember last 10 messages for context

# Performance optimization: cached recognizer and energy threshold
cached_energy_threshold = None  # Calibrated at startup, reused throughout session

# ==================== SCREEN WATCHER (Proactive Mode) ====================
# When enabled, CHAOS monitors your screen and gives proactive feedback
screen_watcher_enabled = False  # Toggle with "enable screen watcher" / "disable screen watcher"
screen_watcher_thread = None  # Background thread for screen monitoring
last_screen_hash = None  # To detect when screen actually changes
last_screen_context = ""  # What CHAOS understood from the last scan
screen_watcher_interval = 10  # Seconds between scans (adjustable)
last_proactive_alert_time = 0  # Prevent spam - minimum gap between alerts
proactive_alert_cooldown = 30  # Minimum seconds between proactive alerts

# ==================== GESTURE CONTROL ====================
gesture_control_enabled = False  # Toggle with "enable gesture control" / "disable gesture control"


async def generate_speech_streaming(text, voice, output_file):
    """Generate speech using Edge TTS with streaming - starts faster"""
    communicate = edge_tts.Communicate(text, voice)
    
    # Collect audio chunks
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    
    # Write to file
    with open(output_file, 'wb') as f:
        f.write(audio_data)

def speak_edge_tts(text, lang='en'):
    """Speak using Edge TTS - OPTIMIZED with faster interrupt checking"""
    global is_speaking, interrupt_flag
    
    try:
        # Create temp file for audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
            temp_file = f.name
        
        # Select voice based on language
        if lang == 'hi':
            voice = "hi-IN-MadhurNeural"  # Hindi voice
        elif lang == 'ur':
            voice = "ur-PK-AsadNeural"    # Urdu voice
        else:
            voice = current_voice  # Use the currently selected global voice
        
        # Generate speech using Edge TTS (streaming for faster generation)
        asyncio.run(generate_speech_streaming(text, voice, temp_file))
        
        # Play audio
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Wait for audio to finish (with faster interrupt check)
        while pygame.mixer.music.get_busy():
            if interrupt_flag:
                pygame.mixer.music.stop()
                break
            time.sleep(0.05)  # Faster polling (was 0.1) for quicker interrupt response
        
        # Cleanup
        pygame.mixer.music.unload()
        try:
            os.remove(temp_file)
        except:
            pass  # Don't fail if cleanup fails
        return True
    except Exception as e:
        print(f"[Edge TTS error: {e}]")
        return False

def speak(text, allow_interrupt=True, force_voice=False):
    """Speak text with multi-language support"""
    global is_speaking, interrupt_flag, interrupted_text, voice_mode
    
    print(f"CHAOS: {text}")
    
    # If voice mode is off and not forcing voice, just print (no speech)
    if not voice_mode and not force_voice:
        return False, None
    
    if allow_interrupt and voice_mode:
        # Start interruption detection thread
        is_speaking = True
        interrupt_flag = False
        interrupted_text = None
        interrupt_thread = threading.Thread(target=check_for_interruption, daemon=True)
        interrupt_thread.start()
    
    # Detect if text contains non-ASCII (Hindi, Urdu, etc.)
    is_non_ascii = not text.isascii()
    
    # Choose appropriate voice based on text content
    if urdu_mode:
        speak_lang = 'ur'
    elif is_non_ascii:
        # Auto-detect: if it has Devanagari, use Hindi voice
        # Check for Hindi/Devanagari script (Unicode range: 0x0900-0x097F)
        has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
        if has_devanagari:
            speak_lang = 'hi'
        else:
            speak_lang = current_language
    else:
        speak_lang = current_language
    
    success = speak_edge_tts(text, speak_lang)
    
    # Fallback to pyttsx3 if Edge TTS fails
    if not success:
        try:
            # Try to speak with pyttsx3, but only ASCII characters
            clean_text = text.encode('ascii', 'ignore').decode('ascii')
            if clean_text.strip():  # Only if there's something left after cleaning
                engine.say(clean_text)
                engine.runAndWait()
            else:
                print("[Could not speak non-English text - displayed above]")
        except Exception as e:
            print(f"[pyttsx3 fallback failed: {e}]")
    
    is_speaking = False
    
    # Return whether we were interrupted and what was said
    return interrupt_flag, interrupted_text

def check_for_interruption():
    """Background thread to detect if user speaks while CHAOS talks - OPTIMIZED for real-time response"""
    global interrupt_flag, interrupted_text
    
    try:
        import pyaudio
        import struct
        import math
        
        CHUNK = 512  # Smaller chunk for faster response (was 1024)
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        THRESHOLD = 800  # Lower = more sensitive (was 1500)
        CONSECUTIVE_FRAMES = 2  # Need 2 consecutive loud frames to trigger (reduces false positives)
        
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, 
                       input=True, frames_per_buffer=CHUNK)
        
        loud_frames = 0
        
        while is_speaking and not interrupt_flag:
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                # Calculate sound level
                count = len(data) // 2
                shorts = struct.unpack('<%dh' % count, data)
                sum_squares = sum(s**2 for s in shorts)
                rms = math.sqrt(sum_squares / count) if count > 0 else 0
                
                if rms > THRESHOLD:
                    loud_frames += 1
                    if loud_frames >= CONSECUTIVE_FRAMES:
                        print(f"\n[Voice detected (RMS: {rms:.0f}) - stopping speech...]")
                        interrupt_flag = True
                        pygame.mixer.music.stop()
                        break
                else:
                    loud_frames = 0
            except:
                pass
            time.sleep(0.02)  # 20ms polling for faster response (was 50ms)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
    except Exception as e:
        # Fallback: if pyaudio direct access fails, just monitor for any key/signal
        pass

def listen():
    """Listen for voice command - BALANCED mode: responsive but allows natural pauses"""
    global cached_energy_threshold
    
    r = sr.Recognizer()
    
    # BALANCED settings - responsive but natural
    # Lower energy threshold for better detection
    base_threshold = cached_energy_threshold if cached_energy_threshold else 1500
    r.energy_threshold = min(base_threshold, 2000)  # Cap at 2000 to ensure responsiveness
    r.dynamic_energy_threshold = True  # Let it adapt to ambient noise
    r.pause_threshold = 1.5  # 1.5 seconds of silence = end of phrase (balanced)
    r.phrase_threshold = 0.2  # Quick phrase detection
    r.non_speaking_duration = 0.8  # 0.8 seconds silence tolerance within phrase
    r.operation_timeout = None  # No operation timeout
    
    max_retries = 3  # Don't loop forever if there's a problem
    retry_count = 0
    
    while retry_count < max_retries:
        with sr.Microphone() as source:
            print("\n[Listening...]")
            
            # Quick ambient noise adjustment if needed
            if retry_count == 0:
                r.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen with reasonable limits
                audio = r.listen(source, timeout=10, phrase_time_limit=30)
                print("[Processing...]")
            except sr.WaitTimeoutError:
                print("[No speech detected - say something!]")
                retry_count += 1
                continue
        
        # Try to recognize - English first for speed
        recognized = False
        query = None
        lang = 'en'
        
        # In urdu_mode, only use English recognition (for Roman Urdu input)
        if urdu_mode:
            try:
                query = r.recognize_google(audio, language='en-US')
                recognized = True
                lang = 'ur'
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                print(f"[Speech API error: {e}]")
                retry_count += 1
                continue
        else:
            # Try English first (fastest), only try others if explicitly in language mode
            try:
                query = r.recognize_google(audio, language='en-US')
                recognized = True
                lang = 'en'
            except sr.UnknownValueError:
                # If English fails, try Urdu as fallback
                try:
                    query = r.recognize_google(audio, language='ur-PK')
                    recognized = True
                    lang = 'ur'
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    pass
            except sr.RequestError as e:
                print(f"[Speech API error: {e}]")
                retry_count += 1
                continue
        
        if recognized and query:
            query_lower = query.lower()
            print(f"You said: {query}")
            return query_lower, lang
        else:
            # Could not understand
            print("[Didn't catch that - try again]")
            retry_count += 1
            continue
    
    # Max retries reached
    print("[Couldn't hear you - please try again]")
    return None, 'en'

def calibrate_microphone():
    """Calibrate microphone once at startup - saves time on each listen cycle"""
    global cached_energy_threshold
    
    print("[Calibrating microphone...]")
    r = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1.0)  # Thorough calibration once
            # Force lower threshold for better sensitivity if auto-calibrated value is too low/high
            if r.energy_threshold < 100:
                r.energy_threshold = 300 # Minimum safe floor
            cached_energy_threshold = r.energy_threshold
            print(f"[Microphone calibrated - threshold: {cached_energy_threshold:.0f}]")
    except Exception as e:
        print(f"[Calibration failed, using default: {e}]")
        cached_energy_threshold = 2500

def load_history():
    try:
        with open('conversation_history.json', 'r') as f:
            return json.load(f)
    except:
        return []

def save_history(history):
    with open('conversation_history.json', 'w') as f:
        json.dump(history, f, indent=2)

# System prompts based on detected language
SYSTEM_PROMPT_URDU = """You are C.H.A.O.S., a helpful AI assistant. 
IMPORTANT: The user is speaking in Urdu. Respond in **Urdu Script (Nastaliq/Arabic letters)**.
For example, say 'میں ٹھیک ہوں، آپ بتاؤ؟' instead of 'Mai theek hun'.
Do NOT use Roman Urdu. Use proper Urdu characters.
Keep responses natural, friendly, and conversational like a Pakistani friend.
CAPABILITIES: You can control the PC. If user asks, reply with these EXACT command tags to trigger them:
- Play Music: [CMD:play_music]
- Stop Music: [CMD:stop_music]
- Next Song: [CMD:next_song]
- Weather: [CMD:weather]
- Open YouTube: [CMD:open_youtube]
- System Stats: [CMD:system_info]
- Scan Screen: [CMD:scan_screen] (Use this if user asks 'what is on my screen' or 'look at this')
- Antigravity: [CMD:antigravity] (Use this to write prompts to the developer/code editor, e.g., 'ask antigravity to...', 'fix this code')
Example: User: "Gana lagao" -> You: "Theek hai! [CMD:play_music]" """

SYSTEM_PROMPT_ENGLISH = """You are C.H.A.O.S., a helpful AI assistant.
The user is speaking in English. Respond in clear, natural English.
Be helpful, concise, and friendly.
CAPABILITIES: You can control the PC. If user asks, reply with these EXACT command tags to trigger them:
- Play Music: [CMD:play_music]
- Stop Music: [CMD:stop_music]
- Next Song: [CMD:next_song]
- Weather: [CMD:weather]
- Open YouTube: [CMD:open_youtube]
- Open Google: [CMD:open_google]
- System Stats: [CMD:system_info]
- Scan Screen: [CMD:scan_screen] (Use this if user asks 'what is on my screen', 'read screen', 'analyze screen')
- Antigravity: [CMD:antigravity] (Use this to write prompts to the developer/code editor, e.g., 'ask antigravity to...', 'write a prompt to...')
Example: User: "Can you play some tunes?" -> You: "Sure thing! [CMD:play_music]"
Example: User: "Write a prompt to Antigravity to fix the bug" -> You: "On it. [CMD:antigravity]" """

def warmup_ollama():
    """Send a dummy request to load the model into memory"""
    print(f"[Initializing AI Core ({ollama_model})...]")
    try:
        requests.post(
            ollama_api_url,
            json={"model": ollama_model, "messages": [{"role": "user", "content": "hi"}], "stream": False},
            headers={"Content-Type": "application/json"},
            timeout=120 # Long timeout for initial load
        )
        print("[AI Core Online]")
        return True
    except:
        print("[Warning] AI Core initialization failed - will retry on demand")
        return False

def ask_ollama(query, history, language='en'):
    global conversation_context
    
    # Choose system prompt based on detected language
    system_prompt = SYSTEM_PROMPT_URDU if language in ['ur', 'hi'] else SYSTEM_PROMPT_ENGLISH
    
    # Prepare messages for API call
    messages = []
    
    # 1. System Prompt
    messages.append({"role": "system", "content": system_prompt})
    
    # 2. Add recent conversation context (for follow-ups)
    if conversation_context:
        # Add last N messages from context list
        messages.extend(conversation_context[-MAX_CONTEXT_MESSAGES:])
    
    # 3. Add current query
    messages.append({"role": "user", "content": query})
    
    # Also update persistent history for file storage (optional, mostly for debugging/logging)
    if history and history[0].get('role') == 'system':
        history[0]['content'] = system_prompt
    else:
        history.insert(0, {"role": "system", "content": system_prompt})
    history.append({"role": "user", "content": query})
    
    try:
        # print(f"[DEBUG] Connecting to Ollama at {ollama_api_url}...")
        response = requests.post(
            ollama_api_url,
            json={"model": ollama_model, "messages": messages, "stream": False},  # Use context-aware messages
            headers={"Content-Type": "application/json"},
            timeout=60 # Restored standard timeout for production
        )
        # print(f"[DEBUG] Ollama response status: {response.status_code}")
        
        if response.status_code == 200:
            reply = response.json()["message"]["content"]
            history.append({"role": "assistant", "content": reply})
            save_history(history)
            return reply
        else:
            return f"Error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        if language in ['ur', 'hi']:
            return "Ollama chal nahi raha. Pehle Ollama start karo."
        return "Ollama is not running. Please start Ollama first."
    except Exception as e:
        return f"Error: {e}"

def scan_screen(prompt="Describe what you see on this screen in detail."):
    """Take a screenshot and analyze it using Ollama's vision model (llava)"""
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to base64
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Send to Ollama vision model
        response = requests.post(
            ollama_api_url,
            json={
                "model": ollama_vision_model,
                "messages": [{
                    "role": "user",
                    "content": prompt,
                    "images": [img_base64]
                }],
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=120  # Vision processing can take longer
        )
        
        if response.status_code == 200:
            return response.json()["message"]["content"]
        else:
            return f"Could not read response: {response.status_code}"
    except Exception as e:
        return f"Error reading response: {e}"

# ==================== SCREEN WATCHER FUNCTIONS ====================

def get_screen_hash():
    """Get a hash of the current screen to detect changes"""
    import hashlib
    try:
        screenshot = pyautogui.screenshot()
        # Resize to small thumbnail for faster hashing
        thumbnail = screenshot.resize((160, 90))
        buffered = BytesIO()
        thumbnail.save(buffered, format="PNG")
        return hashlib.md5(buffered.getvalue()).hexdigest()
    except:
        return None

def analyze_screen_for_issues():
    """Analyze the current screen for coding errors, typos, and issues"""
    global last_screen_context
    
    prompt = """You are a helpful coding assistant monitoring a developer's screen.
    
Look at this screenshot and analyze it for:
1. **Coding Errors**: Red underlines, error messages, syntax errors, undefined variables
2. **Typos**: Misspelled words in code or text
3. **Warnings**: Yellow underlines, warning messages
4. **Build/Compile Errors**: Error panels, terminal errors

RESPONSE FORMAT:
- If you see CRITICAL issues (errors, bugs), start with "ALERT:" followed by a brief description
- If you see MINOR issues (warnings, suggestions), start with "NOTE:" followed by a brief description
- If everything looks fine, respond with "OK" only

Keep responses very brief (1-2 sentences max). Focus only on visible problems.
Examples:
- "ALERT: Line 42 has a syntax error - missing closing parenthesis"
- "NOTE: Variable 'usrname' might be a typo for 'username'"
- "ALERT: Terminal shows ModuleNotFoundError for 'requests'"
- "OK"
"""
    
    try:
        screenshot = pyautogui.screenshot()
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        response = requests.post(
            ollama_api_url,
            json={
                "model": ollama_vision_model,
                "messages": [{
                    "role": "user",
                    "content": prompt,
                    "images": [img_base64]
                }],
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()["message"]["content"]
            last_screen_context = result
            return result
        return None
    except Exception as e:
        print(f"[Screen analysis error: {e}]")
        return None

def screen_watcher_loop():
    """Background thread that monitors the screen for issues"""
    global last_screen_hash, last_proactive_alert_time, screen_watcher_enabled
    
    print("[Screen Watcher] Started - I'm now watching your screen for issues")
    
    while screen_watcher_enabled:
        try:
            # Check if screen has changed
            current_hash = get_screen_hash()
            
            if current_hash and current_hash != last_screen_hash:
                last_screen_hash = current_hash
                
                # Wait a moment for user to finish typing/acting
                time.sleep(2)
                
                # Only analyze if not currently speaking
                if not is_speaking:
                    result = analyze_screen_for_issues()
                    
                    if result:
                        current_time = time.time()
                        
                        # Check for alerts (but respect cooldown)
                        if result.startswith("ALERT:") and (current_time - last_proactive_alert_time) > proactive_alert_cooldown:
                            alert_msg = result.replace("ALERT:", "").strip()
                            print(f"\n[Screen Watcher] {alert_msg}")
                            # Speak the alert
                            speak(f"Heads up! {alert_msg}", allow_interrupt=True)
                            last_proactive_alert_time = current_time
                        
                        elif result.startswith("NOTE:") and (current_time - last_proactive_alert_time) > (proactive_alert_cooldown * 2):
                            # Notes are less urgent, longer cooldown
                            note_msg = result.replace("NOTE:", "").strip()
                            print(f"\n[Screen Watcher] {note_msg}")
                            # Don't speak notes, just log them (too annoying otherwise)
                        
                        # "OK" responses are ignored - everything is fine
            
            # Wait before next check
            time.sleep(screen_watcher_interval)
            
        except Exception as e:
            print(f"[Screen Watcher Error: {e}]")
            time.sleep(screen_watcher_interval)
    
    print("[Screen Watcher] Stopped")

def start_screen_watcher():
    """Start the background screen watcher"""
    global screen_watcher_enabled, screen_watcher_thread
    
    if screen_watcher_enabled:
        return "Screen watcher is already running."
    
    screen_watcher_enabled = True
    screen_watcher_thread = threading.Thread(target=screen_watcher_loop, daemon=True)
    screen_watcher_thread.start()
    
    return "Screen watcher activated. I'll now monitor your screen and alert you to any coding errors or issues I notice."

def stop_screen_watcher():
    """Stop the background screen watcher"""
    global screen_watcher_enabled
    
    if not screen_watcher_enabled:
        return "Screen watcher is not running."
    
    screen_watcher_enabled = False
    return "Screen watcher deactivated. I'll stop monitoring your screen."

def get_screen_watcher_status():
    """Get current screen watcher status and last context"""
    if screen_watcher_enabled:
        return f"Screen watcher is ACTIVE. Last observation: {last_screen_context[:200] if last_screen_context else 'Nothing analyzed yet'}"
    else:
        return "Screen watcher is OFF. Say 'enable screen watcher' to start proactive monitoring."




# ==================== PHASE 1 FEATURE FUNCTIONS ====================

def get_volume_interface():
    """Get Windows audio interface for volume control"""
    if not VOLUME_CONTROL_AVAILABLE:
        return None
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        return cast(interface, POINTER(IAudioEndpointVolume))
    except:
        return None

def set_volume(level):
    """Set system volume (0-100)"""
    volume = get_volume_interface()
    if volume:
        # Convert 0-100 to 0.0-1.0
        level = max(0, min(100, level)) / 100.0
        volume.SetMasterVolumeLevelScalar(level, None)
        return True
    return False

def get_volume():
    """Get current system volume (0-100)"""
    volume = get_volume_interface()
    if volume:
        return int(volume.GetMasterVolumeLevelScalar() * 100)
    return -1

def toggle_mute():
    """Toggle system mute"""
    volume = get_volume_interface()
    if volume:
        current_mute = volume.GetMute()
        volume.SetMute(not current_mute, None)
        return not current_mute  # Return new mute state
    return None

def take_screenshot(workspace_path):
    """Take a screenshot and save to workspace/screenshots"""
    try:
        screenshot_dir = os.path.join(workspace_path, "screenshots")
        if not os.path.exists(screenshot_dir):
            os.makedirs(screenshot_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(screenshot_dir, filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        return True, filename, filepath
    except Exception as e:
        return False, str(e), None

def launch_app(app_name):
    """Launch an application by name (case-insensitive)"""
    import glob
    
    # Get user's local app data path
    local_appdata = os.environ.get('LOCALAPPDATA', '')
    appdata = os.environ.get('APPDATA', '')
    
    # Specific app launch commands (for apps that need special handling)
    special_apps = {
        'discord': f'{local_appdata}\\Discord\\Update.exe --processStart Discord.exe',
        'spotify': f'{appdata}\\Spotify\\Spotify.exe',
        'slack': f'{local_appdata}\\slack\\slack.exe',
        'teams': f'{local_appdata}\\Microsoft\\Teams\\Update.exe --processStart Teams.exe',
        'telegram': f'{appdata}\\Telegram Desktop\\Telegram.exe',
    }
    
    # Common app mappings (for apps that work with 'start' command)
    app_mappings = {
        'chrome': 'chrome',
        'google chrome': 'chrome',
        'firefox': 'firefox',
        'edge': 'msedge',
        'microsoft edge': 'msedge',
        'notepad': 'notepad',
        'calculator': 'calc',
        'calc': 'calc',
        'vscode': 'code',
        'vs code': 'code',
        'visual studio code': 'code',
        'word': 'winword',
        'excel': 'excel',
        'powerpoint': 'powerpnt',
        'file explorer': 'explorer',
        'explorer': 'explorer',
        'files': 'explorer',
        'settings': 'ms-settings:',
        'control panel': 'control',
        'task manager': 'taskmgr',
        'paint': 'mspaint',
        'cmd': 'cmd',
        'command prompt': 'cmd',
        'terminal': 'wt',
        'powershell': 'powershell',
        'whatsapp': 'WhatsApp',  # Microsoft Store app
        'zoom': 'Zoom',
        'obs': 'obs64',
        'steam': 'steam',
    }
    
    app_lower = app_name.lower().strip()
    
    try:
        # 1. Check special apps that need full paths
        if app_lower in special_apps:
            exe_path = special_apps[app_lower]
            if os.path.exists(exe_path.split(' ')[0]):  # Check if exe exists
                subprocess.Popen(exe_path, shell=True)
                return True, app_lower.title()
        
        # 2. Check standard app mappings
        if app_lower in app_mappings:
            actual_app = app_mappings[app_lower]
            if actual_app.startswith('ms-'):
                os.startfile(actual_app)
            else:
                subprocess.Popen(f'start "" "{actual_app}"', shell=True)
            return True, actual_app
        
        # 3. Fallback: Try Title Case with start command
        actual_app = app_name.strip().title()
        subprocess.Popen(f'start "" "{actual_app}"', shell=True)
        return True, actual_app
        
    except Exception as e:
        return False, str(e)

# ==================== MEDIA CONTROL ====================

def media_control(action):
    """Control media playback using keyboard shortcuts"""
    try:
        if action == 'play' or action == 'pause' or action == 'playpause':
            pyautogui.press('playpause')
            return True, "play/pause"
        elif action == 'next' or action == 'skip':
            pyautogui.press('nexttrack')
            return True, "next track"
        elif action == 'previous' or action == 'prev' or action == 'back':
            pyautogui.press('prevtrack')
            return True, "previous track"
        elif action == 'stop':
            pyautogui.press('stop')
            return True, "stopped"
        elif action == 'volumeup' or action == 'volume up':
            for _ in range(5):  # Increase by 5 notches
                pyautogui.press('volumeup')
            return True, "volume up"
        elif action == 'volumedown' or action == 'volume down':
            for _ in range(5):  # Decrease by 5 notches
                pyautogui.press('volumedown')
            return True, "volume down"
        elif action == 'mute':
            pyautogui.press('volumemute')
            return True, "muted/unmuted"
        else:
            return False, f"Unknown action: {action}"
    except Exception as e:
        return False, str(e)

# ==================== CLOSE/KILL APP ====================

def close_app(app_name):
    """Close an application by name using taskkill"""
    # Common app process names
    app_processes = {
        'spotify': 'Spotify.exe',
        'chrome': 'chrome.exe',
        'google chrome': 'chrome.exe',
        'firefox': 'firefox.exe',
        'edge': 'msedge.exe',
        'microsoft edge': 'msedge.exe',
        'discord': 'Discord.exe',
        'slack': 'slack.exe',
        'teams': 'Teams.exe',
        'telegram': 'Telegram.exe',
        'notepad': 'notepad.exe',
        'word': 'WINWORD.EXE',
        'excel': 'EXCEL.EXE',
        'powerpoint': 'POWERPNT.EXE',
        'vscode': 'Code.exe',
        'vs code': 'Code.exe',
        'visual studio code': 'Code.exe',
        'zoom': 'Zoom.exe',
        'obs': 'obs64.exe',
        'vlc': 'vlc.exe',
        'steam': 'steam.exe',
        'whatsapp': 'WhatsApp.exe',
    }
    
    app_lower = app_name.lower().strip()
    
    # Find process name
    process_name = app_processes.get(app_lower, None)
    if not process_name:
        # Try adding .exe to the app name
        process_name = app_name.strip() + '.exe'
    
    try:
        # Use taskkill to close the app
        result = subprocess.run(
            ['taskkill', '/F', '/IM', process_name],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, app_name
        else:
            # Try case-insensitive search with tasklist
            tasklist = subprocess.run(['tasklist'], capture_output=True, text=True)
            for line in tasklist.stdout.split('\n'):
                if app_lower in line.lower():
                    # Found a matching process
                    actual_process = line.split()[0]
                    result = subprocess.run(
                        ['taskkill', '/F', '/IM', actual_process],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        return True, actual_process
            
            return False, f"Could not find {app_name}"
    except Exception as e:
        return False, str(e)

# ==================== SOUNDBOARD ====================

def play_sound_effect(effect_name):
    """Play a sound effect from the soundboard"""
    # Soundboard folder
    soundboard_folder = os.path.join(os.path.dirname(__file__), "soundboard")
    
    if not os.path.exists(soundboard_folder):
        os.makedirs(soundboard_folder, exist_ok=True)
        return False, f"Soundboard folder created at {soundboard_folder}. Add .mp3 or .wav files there."
    
    # Find matching sound file
    effect_lower = effect_name.lower().strip()
    sound_files = [f for f in os.listdir(soundboard_folder) if f.endswith(('.mp3', '.wav', '.ogg'))]
    
    # Search for best match
    matched_file = None
    for f in sound_files:
        if effect_lower in f.lower():
            matched_file = os.path.join(soundboard_folder, f)
            break
    
    if not matched_file:
        available = ", ".join([os.path.splitext(f)[0] for f in sound_files[:5]])
        return False, f"Sound '{effect_name}' not found. Available: {available or 'None'}"
    
    try:
        pygame.mixer.music.load(matched_file)
        pygame.mixer.music.play()
        return True, os.path.basename(matched_file)
    except Exception as e:
        return False, str(e)

def stop_sound_effect():
    """Stop currently playing sound effect"""
    pygame.mixer.music.stop()
    return True

# ==================== WHATSAPP MESSAGING ====================

def send_whatsapp_message(phone_number, message):
    """Send a WhatsApp message using WhatsApp Web automation"""
    try:
        # Clean up phone number
        phone = phone_number.replace(" ", "").replace("-", "").replace("+", "")
        if not phone.startswith("92"):  # Pakistan country code
            phone = "92" + phone.lstrip("0")
        
        # URL encode message
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        
        # Open WhatsApp Web with pre-filled message
        whatsapp_url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"
        webbrowser.open(whatsapp_url)
        
        # Wait for page to load, then send
        time.sleep(5)  # Give user time to scan QR if needed
        
        # Press Enter to send (user needs to have WhatsApp Web already logged in)
        pyautogui.press('enter')
        
        return True, "Message sent via WhatsApp Web"
    except Exception as e:
        return False, str(e)

def save_note(note_content, workspace_path):
    """Save a voice note to workspace/notes.txt"""
    try:
        notes_file = os.path.join(workspace_path, "notes.txt")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(notes_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {note_content}\n")
        
        return True
    except Exception as e:
        return False

def calculate(expression):
    """Safely evaluate a math expression"""
    try:
        # Clean the expression - convert words to operators
        expr = expression.lower()
        expr = expr.replace('plus', '+').replace('add', '+')
        expr = expr.replace('minus', '-').replace('subtract', '-')
        expr = expr.replace('times', '*').replace('multiplied by', '*').replace('x', '*')
        expr = expr.replace('divided by', '/').replace('over', '/')
        expr = expr.replace('power', '**').replace('to the power of', '**')
        expr = expr.replace('percent', '/100')
        
        # Remove non-math characters for safety
        allowed = set('0123456789+-*/.() ')
        expr = ''.join(c for c in expr if c in allowed)
        expr = expr.strip()
        
        if not expr:
            return None, "I couldn't understand the math expression"
        
        # Safely evaluate
        result = eval(expr)
        return result, None
    except Exception as e:
        return None, str(e)

# ==================== END PHASE 1 FUNCTIONS ====================

# ==================== PHASE 2 FEATURE FUNCTIONS ====================

def get_system_info():
    """Get system information: battery, CPU, RAM"""
    try:
        import psutil
        info = {}
        
        # Battery
        battery = psutil.sensors_battery()
        if battery:
            info['battery'] = battery.percent
            info['plugged'] = battery.power_plugged
        else:
            info['battery'] = None
        
        # CPU
        info['cpu'] = psutil.cpu_percent(interval=0.5)
        
        # RAM
        ram = psutil.virtual_memory()
        info['ram_used'] = ram.percent
        info['ram_available'] = round(ram.available / (1024**3), 1)  # GB
        
        return info
    except Exception as e:
        return {'error': str(e)}

def lock_pc():
    """Lock the PC"""
    try:
        ctypes.windll.user32.LockWorkStation()
        return True
    except:
        return False

def shutdown_pc(action='shutdown', delay=0):
    """Shutdown, restart, or sleep the PC"""
    try:
        if action == 'shutdown':
            os.system(f'shutdown /s /t {delay}')
        elif action == 'restart':
            os.system(f'shutdown /r /t {delay}')
        elif action == 'cancel':
            os.system('shutdown /a')
        elif action == 'sleep':
            os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        return True
    except:
        return False

def manage_window(action):
    """Manage windows: minimize, maximize, close"""
    try:
        if action == 'minimize_all':
            pyautogui.hotkey('win', 'd')
        elif action == 'maximize':
            pyautogui.hotkey('win', 'up')
        elif action == 'minimize':
            pyautogui.hotkey('win', 'down')
        elif action == 'close':
            pyautogui.hotkey('alt', 'f4')
        elif action == 'switch':
            pyautogui.hotkey('alt', 'tab')
        return True
    except:
        return False

def read_clipboard():
    """Read text from clipboard"""
    try:
        import pyperclip
        return pyperclip.paste()
    except:
        return None

def write_clipboard(text):
    """Write text to clipboard"""
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except:
        return False

# Timer storage (in-memory, resets when CHAOS restarts)
active_timers = []

def set_timer(seconds, message="Timer complete!"):
    """Set a timer that will trigger a notification"""
    def timer_callback():
        speak(message, allow_interrupt=False)
        print(f"[Timer: {message}]")
    
    timer = threading.Timer(seconds, timer_callback)
    timer.start()
    active_timers.append(timer)
    return True

def parse_time_duration(text):
    """Parse time duration from text like '5 minutes' or '30 seconds'"""
    import re
    
    # Find numbers
    numbers = re.findall(r'\d+', text)
    if not numbers:
        return None
    
    amount = int(numbers[0])
    
    # Determine unit
    text_lower = text.lower()
    if 'hour' in text_lower:
        return amount * 3600
    elif 'minute' in text_lower or 'min' in text_lower:
        return amount * 60
    elif 'second' in text_lower or 'sec' in text_lower:
        return amount
    else:
        # Default to minutes if not specified
        return amount * 60

# ==================== END PHASE 2 FUNCTIONS ====================

# ==================== PHASE 3 FEATURE FUNCTIONS ====================

def get_weather(city="Lahore"):
    """Get weather using wttr.in (no API key needed)"""
    try:
        # Use wttr.in for simple weather
        url = f"https://wttr.in/{city}?format=%C+%t+%h+%w"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text.strip()
        return None
    except:
        return None

def get_news():
    """Get top news headlines using Google News RSS"""
    try:
        import xml.etree.ElementTree as ET
        url = "https://news.google.com/rss?hl=en-PK&gl=PK&ceid=PK:en"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            items = root.findall('.//item')[:5]  # Top 5 headlines
            headlines = [item.find('title').text for item in items if item.find('title') is not None]
            return headlines
        return None
    except:
        return None

def translate_text(text, target_language="Urdu"):
    """Translate text using Ollama"""
    try:
        prompt = f"Translate the following text to {target_language}. Only respond with the translation, nothing else: {text}"
        response = requests.post(
            ollama_api_url,
            json={
                "model": ollama_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["message"]["content"].strip()
        return None
    except:
        return None

def define_word(word):
    """Get word definition using Ollama"""
    try:
        prompt = f"Define the word '{word}' in a simple, concise way. Give the definition in 1-2 sentences."
        response = requests.post(
            ollama_api_url,
            json={
                "model": ollama_model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["message"]["content"].strip()
        return None
    except:
        return None

def get_daily_briefing():
    """Get a morning briefing with time, weather, and summary"""
    parts = []
    
    # Time
    now = datetime.datetime.now()
    hour = now.hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    
    parts.append(f"{greeting}, Sir.")
    parts.append(f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d')}.")
    
    # Weather
    weather = get_weather()
    if weather:
        parts.append(f"Weather in Lahore: {weather}.")
    
    # System status
    info = get_system_info()
    if info.get('battery') is not None:
        status = "charging" if info['plugged'] else "on battery"
        parts.append(f"Your battery is at {info['battery']} percent, {status}.")
    
    return " ".join(parts)

# ==================== END PHASE 3 FUNCTIONS ====================

# ==================== PHASE 4 FEATURE FUNCTIONS ====================

# Custom macros - predefined automation sequences
custom_macros = {
    'morning routine': [
        ('speak', 'Starting your morning routine.'),
        ('app', 'chrome'),
        ('wait', 2),
        ('briefing', None),
    ],
    'work mode': [
        ('speak', 'Entering work mode.'),
        ('app', 'code'),
        ('wait', 1),
        ('app', 'chrome'),
        ('volume', 30),
    ],
    'relax mode': [
        ('speak', 'Entering relax mode. Playing some music.'),
        ('app', 'spotify'),
        ('wait', 2),
        ('media', 'play'),
    ],
    'night mode': [
        ('speak', 'Activating night mode.'),
        ('volume', 20),
        ('window', 'minimize_all'),
    ],
}

def run_macro(macro_name):
    """Execute a predefined macro sequence"""
    if macro_name not in custom_macros:
        return False, f"Unknown macro: {macro_name}"
    
    steps = custom_macros[macro_name]
    for action, param in steps:
        try:
            if action == 'speak':
                speak(param, allow_interrupt=False)
            elif action == 'app':
                launch_app(param)
            elif action == 'wait':
                time.sleep(param)
            elif action == 'briefing':
                briefing = get_daily_briefing()
                speak(briefing)
            elif action == 'volume':
                set_volume(param)
            elif action == 'media':
                media_control(param)
            elif action == 'window':
                manage_window(param)
        except Exception as e:
            print(f"[Macro step failed: {action} - {e}]")
    
    return True, None

# ==================== END PHASE 4 FUNCTIONS ====================

# ==================== PHASE 5 FEATURE FUNCTIONS (NEW!) ====================

# --- SMART CLIPBOARD ---
def get_clipboard_text():
    """Get text from clipboard"""
    try:
        import pyperclip
        return pyperclip.paste()
    except:
        try:
            # Fallback: use tkinter
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            text = root.clipboard_get()
            root.destroy()
            return text
        except:
            return None

def summarize_clipboard():
    """Summarize text in clipboard using Ollama"""
    text = get_clipboard_text()
    if not text:
        return "Clipboard is empty or contains no text."
    
    try:
        prompt = f"Summarize this text concisely in 2-3 sentences:\n\n{text[:2000]}"
        response = requests.post(
            ollama_api_url,
            json={"model": ollama_model, "messages": [{"role": "user", "content": prompt}], "stream": False},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return "Could not summarize the text."
    except:
        return "Error summarizing clipboard."

def translate_clipboard(target_lang="Urdu"):
    """Translate clipboard text using Ollama"""
    text = get_clipboard_text()
    if not text:
        return "Clipboard is empty."
    
    try:
        prompt = f"Translate to {target_lang}. Only respond with translation:\n\n{text[:1500]}"
        response = requests.post(
            ollama_api_url,
            json={"model": ollama_model, "messages": [{"role": "user", "content": prompt}], "stream": False},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return "Could not translate."
    except:
        return "Error translating clipboard."

def explain_clipboard_code():
    """Explain code in clipboard using Ollama"""
    text = get_clipboard_text()
    if not text:
        return "Clipboard is empty."
    
    try:
        prompt = f"Explain this code simply and concisely:\n\n```\n{text[:2000]}\n```"
        response = requests.post(
            ollama_api_url,
            json={"model": ollama_model, "messages": [{"role": "user", "content": prompt}], "stream": False},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()["message"]["content"]
        return "Could not explain the code."
    except:
        return "Error explaining clipboard code."

# --- QUICK MATH & CONVERSIONS ---
def quick_math(expression):
    """Calculate math expression or do conversions"""
    try:
        # Currency conversion rates (approximate)
        currency_rates = {
            'usd_to_pkr': 278, 'pkr_to_usd': 1/278,
            'usd_to_inr': 83, 'inr_to_usd': 1/83,
            'usd_to_eur': 0.92, 'eur_to_usd': 1/0.92,
            'usd_to_gbp': 0.79, 'gbp_to_usd': 1/0.79,
        }
        
        expr = expression.lower()
        
        # Currency conversion
        import re
        currency_match = re.search(r'(\d+(?:\.\d+)?)\s*(usd|pkr|inr|eur|gbp)\s*(?:to|in)\s*(usd|pkr|inr|eur|gbp)', expr)
        if currency_match:
            amount = float(currency_match.group(1))
            from_curr = currency_match.group(2)
            to_curr = currency_match.group(3)
            
            # Convert via USD
            if from_curr == 'usd':
                usd_amount = amount
            else:
                usd_amount = amount * currency_rates.get(f'{from_curr}_to_usd', 1)
            
            if to_curr == 'usd':
                result = usd_amount
            else:
                result = usd_amount * currency_rates.get(f'usd_to_{to_curr}', 1)
            
            return f"{amount} {from_curr.upper()} = {result:.2f} {to_curr.upper()}"
        
        # Percentage calculation
        percent_match = re.search(r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)', expr)
        if percent_match:
            percent = float(percent_match.group(1))
            value = float(percent_match.group(2))
            result = (percent / 100) * value
            return f"{percent}% of {value} = {result}"
        
        # Unit conversions
        if 'km to mile' in expr or 'kilometers to miles' in expr:
            num = float(re.search(r'(\d+(?:\.\d+)?)', expr).group(1))
            return f"{num} km = {num * 0.621371:.2f} miles"
        if 'mile to km' in expr or 'miles to km' in expr:
            num = float(re.search(r'(\d+(?:\.\d+)?)', expr).group(1))
            return f"{num} miles = {num * 1.60934:.2f} km"
        if 'celsius to fahrenheit' in expr or 'c to f' in expr:
            num = float(re.search(r'(\d+(?:\.\d+)?)', expr).group(1))
            return f"{num}°C = {(num * 9/5) + 32:.1f}°F"
        if 'fahrenheit to celsius' in expr or 'f to c' in expr:
            num = float(re.search(r'(\d+(?:\.\d+)?)', expr).group(1))
            return f"{num}°F = {(num - 32) * 5/9:.1f}°C"
        
        # Basic math
        safe_expr = re.sub(r'[^\d\+\-\*\/\.\(\)\s]', '', expression)
        if safe_expr.strip():
            result = eval(safe_expr)
            return f"{expression} = {result}"
        
        return "I couldn't understand that calculation."
    except Exception as e:
        return f"Calculation error: {e}"

# --- PASSWORD GENERATOR ---
def generate_password(length=16, include_symbols=True):
    """Generate a strong password"""
    import random
    import string
    
    chars = string.ascii_letters + string.digits
    if include_symbols:
        chars += "!@#$%^&*()_+-=[]{}|"
    
    # Ensure at least one of each type
    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
    ]
    if include_symbols:
        password.append(random.choice("!@#$%^&*"))
    
    # Fill the rest
    password.extend(random.choice(chars) for _ in range(length - len(password)))
    random.shuffle(password)
    
    return ''.join(password)

# --- POMODORO TIMER ---
pomodoro_active = False
pomodoro_thread = None

def start_pomodoro(work_minutes=25, break_minutes=5):
    """Start a pomodoro focus timer"""
    global pomodoro_active, pomodoro_thread
    
    if pomodoro_active:
        return "Pomodoro is already running. Say 'stop pomodoro' to cancel."
    
    def pomodoro_cycle():
        global pomodoro_active
        pomodoro_active = True
        
        # Work phase
        print(f"[Pomodoro] Work phase started - {work_minutes} minutes")
        for i in range(work_minutes * 60):
            if not pomodoro_active:
                return
            time.sleep(1)
        
        if pomodoro_active:
            speak("Work phase complete! Time for a break.", force_voice=True)
            print(f"[Pomodoro] Break phase - {break_minutes} minutes")
            
            # Break phase
            for i in range(break_minutes * 60):
                if not pomodoro_active:
                    return
                time.sleep(1)
            
            if pomodoro_active:
                speak("Break over! Ready to focus again?", force_voice=True)
                pomodoro_active = False
    
    pomodoro_thread = threading.Thread(target=pomodoro_cycle, daemon=True)
    pomodoro_thread.start()
    
    return f"Pomodoro started! {work_minutes} minutes of focus, then {break_minutes} minute break."

def stop_pomodoro():
    """Stop the pomodoro timer"""
    global pomodoro_active
    if pomodoro_active:
        pomodoro_active = False
        return "Pomodoro timer stopped."
    return "No pomodoro timer running."

# --- DICTATION MODE ---
dictation_mode = False

def start_dictation():
    """Start dictation mode - types everything spoken"""
    global dictation_mode
    dictation_mode = True
    return "Dictation mode started. I'll type everything you say. Say 'stop dictation' to end."

def stop_dictation():
    """Stop dictation mode"""
    global dictation_mode
    dictation_mode = False
    return "Dictation mode stopped."

def type_text(text):
    """Type text using pyautogui"""
    try:
        import pyperclip
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        return True
    except:
        try:
            pyautogui.typewrite(text, interval=0.02)
            return True
        except:
            return False

# --- PROCESS MONITOR ---
def get_running_processes():
    """Get list of running processes by memory usage"""
    try:
        import psutil
        processes = []
        for proc in psutil.process_iter(['name', 'memory_percent', 'cpu_percent']):
            try:
                info = proc.info
                if info['memory_percent'] and info['memory_percent'] > 0.1:
                    processes.append({
                        'name': info['name'],
                        'memory': info['memory_percent'],
                        'cpu': info['cpu_percent']
                    })
            except:
                pass
        
        # Sort by memory usage
        processes.sort(key=lambda x: x['memory'], reverse=True)
        return processes[:10]  # Top 10
    except ImportError:
        return None

def kill_process(process_name):
    """Kill a process by name"""
    try:
        import psutil
        killed = False
        for proc in psutil.process_iter(['name']):
            if process_name.lower() in proc.info['name'].lower():
                proc.kill()
                killed = True
        return killed
    except:
        return False

def get_system_health():
    """Get comprehensive system health info"""
    try:
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory
        mem = psutil.virtual_memory()
        mem_used = mem.used / (1024**3)
        mem_total = mem.total / (1024**3)
        mem_percent = mem.percent
        
        # Disk
        disk = psutil.disk_usage('C:')
        disk_free = disk.free / (1024**3)
        disk_total = disk.total / (1024**3)
        disk_percent = disk.percent
        
        # Battery
        battery = psutil.sensors_battery()
        battery_info = ""
        if battery:
            battery_info = f"Battery: {battery.percent}%{'charging' if battery.power_plugged else ''}. "
        
        return f"{battery_info}CPU: {cpu_percent}%. RAM: {mem_percent}% ({mem_used:.1f}/{mem_total:.1f} GB). Disk C: {disk_percent}% used ({disk_free:.0f} GB free)."
    except ImportError:
        return "Install psutil for system health: pip install psutil"
    except Exception as e:
        return f"Error getting system health: {e}"

# --- MEMORY SYSTEM (Knowledge Base) ---
MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chaos_memory.json")

def load_memory():
    """Load memory from file"""
    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory):
    """Save memory to file"""
    try:
        with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(memory, f, indent=2)
        return True
    except:
        return False

def remember_fact(key, value):
    """Remember a fact"""
    memory = load_memory()
    memory[key.lower()] = {
        'value': value,
        'timestamp': datetime.datetime.now().isoformat()
    }
    save_memory(memory)
    return f"I'll remember that {key} is {value}."

def recall_fact(key):
    """Recall a remembered fact"""
    memory = load_memory()
    if key.lower() in memory:
        return memory[key.lower()]['value']
    return None

def forget_fact(key):
    """Forget a fact"""
    memory = load_memory()
    if key.lower() in memory:
        del memory[key.lower()]
        save_memory(memory)
        return f"I've forgotten about {key}."
    return f"I don't have anything stored about {key}."

def list_memories():
    """List all remembered facts"""
    memory = load_memory()
    if not memory:
        return "I don't have any memories stored yet."
    
    facts = [f"- {k}: {v['value']}" for k, v in memory.items()]
    return "Here's what I remember:\n" + "\n".join(facts[:20])

# --- CLIPBOARD HISTORY ---
clipboard_history = []
MAX_CLIPBOARD_HISTORY = 50

def add_to_clipboard_history(text):
    """Add text to clipboard history"""
    global clipboard_history
    if text and text not in [h['text'] for h in clipboard_history[-5:]]:
        clipboard_history.append({
            'text': text[:500],  # Limit size
            'timestamp': datetime.datetime.now().isoformat()
        })
        # Keep only last MAX entries
        clipboard_history = clipboard_history[-MAX_CLIPBOARD_HISTORY:]

def get_clipboard_history():
    """Get recent clipboard history"""
    if not clipboard_history:
        return "No clipboard history yet."
    
    recent = clipboard_history[-10:]
    result = "Recent clipboard items:\n"
    for i, item in enumerate(reversed(recent), 1):
        preview = item['text'][:50] + "..." if len(item['text']) > 50 else item['text']
        result += f"{i}. {preview}\n"
    return result

# --- FILE SEARCH ---
def search_files(query, search_dirs=None):
    """Search for files by name"""
    if search_dirs is None:
        search_dirs = [
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Downloads"),
        ]
    
    results = []
    query_lower = query.lower()
    
    for search_dir in search_dirs:
        if not os.path.exists(search_dir):
            continue
        try:
            for root, dirs, files in os.walk(search_dir):
                # Skip hidden and system folders
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if query_lower in file.lower():
                        results.append(os.path.join(root, file))
                        if len(results) >= 10:
                            return results
        except:
            pass
    
    return results

# --- CONVERSATION EXPORT ---
def export_conversation(workspace_path):
    """Export conversation history to markdown"""
    history = load_history()
    if not history:
        return False, "No conversation history to export."
    
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.md"
        filepath = os.path.join(workspace_path, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# CHAOS Conversation Export\n\n")
            f.write(f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for msg in history:
                if msg['role'] == 'system':
                    continue
                role = "**You**" if msg['role'] == 'user' else "**CHAOS**"
                f.write(f"{role}: {msg['content']}\n\n")
        
        return True, filename
    except Exception as e:
        return False, str(e)

# --- GLOBAL HOTKEY ---
hotkey_listener = None

def setup_global_hotkey():
    """Setup global hotkey (Win+Shift+C) to activate CHAOS"""
    try:
        import keyboard
        
        def on_hotkey():
            print("\n[Hotkey activated! Listening...]")
            # Play a sound or visual indicator
            speak("Yes?", allow_interrupt=False)
        
        keyboard.add_hotkey('win+shift+c', on_hotkey)
        print("[Global hotkey registered: Win+Shift+C]")
        return True
    except ImportError:
        print("[Hotkey not available - install 'keyboard' package]")
        return False
    except Exception as e:
        print(f"[Hotkey setup failed: {e}]")
        return False

# --- SCREEN RECORDING ---
screen_recording = False
screen_recording_thread = None
screen_recording_path = None

def start_screen_recording(workspace_path, duration=None):
    """Start recording the screen"""
    global screen_recording, screen_recording_thread, screen_recording_path
    
    if screen_recording:
        return "Already recording. Say 'stop recording' to stop."
    
    def record_screen():
        global screen_recording, screen_recording_path
        
        try:
            import cv2
            import numpy as np
            
            # Try mss for faster capture, fallback to pyautogui
            try:
                import mss
                use_mss = True
            except ImportError:
                use_mss = False
            
            # Setup output file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.mp4"
            recordings_dir = os.path.join(workspace_path, "recordings")
            os.makedirs(recordings_dir, exist_ok=True)
            screen_recording_path = os.path.join(recordings_dir, filename)
            
            # Get screen size
            if use_mss:
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    width = monitor["width"]
                    height = monitor["height"]
            else:
                screen = pyautogui.screenshot()
                width, height = screen.size
            
            # Setup video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 10  # Lower FPS for smaller files and less CPU usage
            out = cv2.VideoWriter(screen_recording_path, fourcc, fps, (width, height))
            
            print(f"[Recording started: {screen_recording_path}]")
            start_time = time.time()
            frame_duration = 1.0 / fps
            
            while screen_recording:
                frame_start = time.time()
                
                # Capture screen
                if use_mss:
                    with mss.mss() as sct:
                        img = sct.grab(sct.monitors[1])
                        frame = np.array(img)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                else:
                    screenshot = pyautogui.screenshot()
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                out.write(frame)
                
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    break
                
                # Maintain FPS
                elapsed = time.time() - frame_start
                if elapsed < frame_duration:
                    time.sleep(frame_duration - elapsed)
            
            out.release()
            recording_duration = time.time() - start_time
            print(f"[Recording stopped: {recording_duration:.1f} seconds saved to {filename}]")
            screen_recording = False
            
            # Announce completion
            speak(f"Recording saved. {recording_duration:.0f} seconds captured.", force_voice=True)
            
        except ImportError as e:
            print(f"[Recording requires opencv-python: pip install opencv-python]")
            screen_recording = False
        except Exception as e:
            print(f"[Recording error: {e}]")
            screen_recording = False
    
    screen_recording = True
    screen_recording_thread = threading.Thread(target=record_screen, daemon=True)
    screen_recording_thread.start()
    
    if duration:
        return f"Recording screen for {duration} seconds..."
    return "Recording screen. Say 'stop recording' when done."

def stop_screen_recording():
    """Stop screen recording"""
    global screen_recording
    
    if not screen_recording:
        return "Not currently recording."
    
    screen_recording = False
    return "Stopping recording..."

# --- WAKE WORD DETECTION ---
wake_word_active = False
wake_word_thread = None
WAKE_WORDS = ['hey chaos', 'chaos', 'hey kaos', 'kaos', 'chaos activate', 'hey chaos activate']

def wake_word_listener():
    """Background thread that listens for wake word"""
    global wake_word_active, is_awake
    
    print("[Wake Word] Listening for 'Hey CHAOS'...")
    
    r = sr.Recognizer()
    r.energy_threshold = cached_energy_threshold if cached_energy_threshold else 2500
    r.dynamic_energy_threshold = False
    r.pause_threshold = 0.5  # Quick detection
    r.phrase_threshold = 0.1
    
    while wake_word_active:
        try:
            with sr.Microphone() as source:
                # Listen for short phrases (wake word detection)
                try:
                    audio = r.listen(source, timeout=2, phrase_time_limit=3)
                except sr.WaitTimeoutError:
                    continue
                
                # Try to recognize
                try:
                    text = r.recognize_google(audio, language='en-US').lower()
                    
                    # Check for wake word
                    if any(wake in text for wake in WAKE_WORDS):
                        print(f"[Wake Word] Detected: '{text}'")
                        is_awake = True
                        speak("Yes, I'm here.", allow_interrupt=False, force_voice=True)
                        # Brief pause before main loop takes over
                        time.sleep(0.5)
                        
                except sr.UnknownValueError:
                    pass
                except sr.RequestError:
                    time.sleep(1)  # API error, wait before retry
                    
        except Exception as e:
            time.sleep(0.5)
    
    print("[Wake Word] Listener stopped.")

def start_wake_word_detection():
    """Start always-listening wake word detection"""
    global wake_word_active, wake_word_thread
    
    if wake_word_active:
        return "Wake word detection is already active."
    
    wake_word_active = True
    wake_word_thread = threading.Thread(target=wake_word_listener, daemon=True)
    wake_word_thread.start()
    
    return "Wake word detection enabled. Say 'Hey CHAOS' anytime to wake me up."

def stop_wake_word_detection():
    """Stop wake word detection"""
    global wake_word_active
    
    if not wake_word_active:
        return "Wake word detection is not active."
    
    wake_word_active = False
    return "Wake word detection disabled."

# ==================== PHASE 6 FEATURE FUNCTIONS (EVEN MORE!) ====================

# --- JOKES & FUN ---
JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "A SQL query walks into a bar, walks up to two tables and asks, 'Can I join you?'",
    "Why do Java developers wear glasses? Because they don't C#!",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
    "A programmer's wife tells him: 'Go to the store and buy a loaf of bread. If they have eggs, buy a dozen.' He returns with 12 loaves of bread.",
    "Why did the developer go broke? Because he used up all his cache!",
    "I would tell you a UDP joke, but you might not get it.",
    "Why do programmers hate nature? It has too many bugs!",
    "['hip', 'hip'] - a hip hop array!",
    "I'm not lazy, I'm just on energy-saving mode.",
    "Why was the computer cold? It left its Windows open!",
    "There's no place like 127.0.0.1",
    "Console.log('Hello World') - the programmer's first words",
    "I don't always test my code, but when I do, I do it in production.",
    "99 little bugs in the code, 99 little bugs... Take one down, patch it around... 127 little bugs in the code.",
]

def tell_joke():
    """Tell a random joke"""
    import random
    return random.choice(JOKES)

# --- WIKIPEDIA QUICK LOOKUP ---
def wikipedia_summary(topic):
    """Get a quick summary from Wikipedia"""
    try:
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic.replace(' ', '_')}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('extract', 'No summary found.')[:500]
        return f"Couldn't find information about {topic}."
    except:
        return f"Error looking up {topic}."

# --- REMINDER SYSTEM ---
REMINDERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chaos_reminders.json")

def load_reminders():
    try:
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_reminders(reminders):
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f, indent=2)

def set_reminder(message, minutes):
    """Set a reminder that triggers after X minutes"""
    remind_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
    
    reminders = load_reminders()
    reminders.append({
        'message': message,
        'time': remind_time.isoformat(),
        'triggered': False
    })
    save_reminders(reminders)
    
    # Start reminder thread
    def reminder_thread():
        time.sleep(minutes * 60)
        speak(f"Reminder: {message}", force_voice=True)
        print(f"\n[REMINDER] {message}")
    
    threading.Thread(target=reminder_thread, daemon=True).start()
    
    return f"Reminder set for {minutes} minutes from now: {message}"

def list_reminders():
    """List all active reminders"""
    reminders = load_reminders()
    if not reminders:
        return "No reminders set."
    
    result = "Your reminders:\n"
    for i, r in enumerate(reminders, 1):
        result += f"{i}. {r['message']} (at {r['time'][:16]})\n"
    return result

# --- TODO LIST ---
TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chaos_todo.json")

def load_todos():
    try:
        with open(TODO_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_todos(todos):
    with open(TODO_FILE, 'w') as f:
        json.dump(todos, f, indent=2)

def add_todo(task):
    """Add a new todo item"""
    todos = load_todos()
    todos.append({
        'task': task,
        'done': False,
        'created': datetime.datetime.now().isoformat()
    })
    save_todos(todos)
    return f"Added to your list: {task}"

def list_todos():
    """List all todos"""
    todos = load_todos()
    if not todos:
        return "Your todo list is empty!"
    
    result = "Your todo list:\n"
    for i, t in enumerate(todos, 1):
        status = "✓" if t['done'] else "○"
        result += f"{status} {i}. {t['task']}\n"
    return result

def complete_todo(index):
    """Mark a todo as complete"""
    todos = load_todos()
    if 0 < index <= len(todos):
        todos[index-1]['done'] = True
        save_todos(todos)
        return f"Completed: {todos[index-1]['task']}"
    return "Invalid todo number."

def clear_todos():
    """Clear completed todos"""
    todos = load_todos()
    todos = [t for t in todos if not t['done']]
    save_todos(todos)
    return "Cleared completed tasks."

# --- QR CODE GENERATOR ---
def generate_qr_code(text, workspace_path):
    """Generate a QR code from text"""
    try:
        import qrcode
        
        qr_dir = os.path.join(workspace_path, "qrcodes")
        os.makedirs(qr_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"qr_{timestamp}.png"
        filepath = os.path.join(qr_dir, filename)
        
        qr = qrcode.make(text)
        qr.save(filepath)
        
        return True, filename, filepath
    except ImportError:
        return False, "Install qrcode: pip install qrcode", None
    except Exception as e:
        return False, str(e), None

# --- INTERNET SPEED TEST ---
def internet_speed_test():
    """Quick internet speed test using a download test"""
    try:
        import urllib.request
        
        # Download a small file to test speed
        url = "http://speedtest.tele2.net/1MB.zip"
        start_time = time.time()
        
        response = urllib.request.urlopen(url, timeout=30)
        data = response.read()
        
        end_time = time.time()
        duration = end_time - start_time
        size_mb = len(data) / (1024 * 1024)
        speed_mbps = (size_mb * 8) / duration
        
        return f"Download speed: approximately {speed_mbps:.1f} Mbps"
    except Exception as e:
        return f"Speed test failed: {e}"

# --- MOTIVATION & QUOTES ---
MOTIVATIONAL_QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Code is like humor. When you have to explain it, it's bad. - Cory House",
    "First, solve the problem. Then, write the code. - John Johnson",
    "The best error message is the one that never shows up. - Thomas Fuchs",
    "Make it work, make it right, make it fast. - Kent Beck",
    "Any fool can write code that a computer can understand. Good programmers write code that humans can understand. - Martin Fowler",
    "The only way to learn a new programming language is by writing programs in it. - Dennis Ritchie",
    "Believe you can and you're halfway there. - Theodore Roosevelt",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "Don't watch the clock; do what it does. Keep going. - Sam Levenson",
    "The secret of getting ahead is getting started. - Mark Twain",
    "You are never too old to set another goal or to dream a new dream. - C.S. Lewis",
]

def get_motivation():
    """Get a random motivational quote"""
    import random
    return random.choice(MOTIVATIONAL_QUOTES)

# --- RANDOM PICKER ---
def random_pick(options):
    """Pick a random option from a list"""
    import random
    items = [x.strip() for x in options.split(',') if x.strip()]
    if not items:
        return "Give me some options separated by commas!"
    return f"I choose: {random.choice(items)}"

def random_number(min_val=1, max_val=100):
    """Generate a random number"""
    import random
    return f"Random number: {random.randint(min_val, max_val)}"

def flip_coin():
    """Flip a coin"""
    import random
    return "Heads!" if random.choice([True, False]) else "Tails!"

def roll_dice(sides=6):
    """Roll a dice"""
    import random
    return f"You rolled a {random.randint(1, sides)}!"

# --- WINDOW SNAPPING ---
def snap_window(direction):
    """Snap the active window to a position"""
    try:
        if direction == 'left':
            pyautogui.hotkey('win', 'left')
            return "Window snapped left."
        elif direction == 'right':
            pyautogui.hotkey('win', 'right')
            return "Window snapped right."
        elif direction == 'maximize' or direction == 'up':
            pyautogui.hotkey('win', 'up')
            return "Window maximized."
        elif direction == 'minimize' or direction == 'down':
            pyautogui.hotkey('win', 'down')
            return "Window minimized."
        elif direction == 'center':
            pyautogui.hotkey('win', 'up')
            pyautogui.hotkey('win', 'down')
            return "Window centered."
        return "Unknown direction. Use left, right, up, or down."
    except:
        return "Couldn't snap window."

# --- DARK MODE TOGGLE ---
def toggle_dark_mode():
    """Toggle Windows dark mode"""
    try:
        import winreg
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        
        # Get current value
        apps_theme = winreg.QueryValueEx(key, "AppsUseLightTheme")[0]
        
        # Toggle
        new_value = 0 if apps_theme == 1 else 1
        winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, new_value)
        winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, new_value)
        winreg.CloseKey(key)
        
        return "Dark mode enabled." if new_value == 0 else "Light mode enabled."
    except:
        return "Couldn't toggle dark mode."

# --- SYSTEM CLEANUP ---
def empty_recycle_bin():
    """Empty the recycle bin"""
    try:
        from ctypes import windll
        windll.shell32.SHEmptyRecycleBinW(None, None, 0x0007)
        return "Recycle bin emptied."
    except:
        return "Couldn't empty recycle bin."

def clear_temp_files():
    """Clear temporary files"""
    try:
        import shutil
        temp_path = os.environ.get('TEMP', 'C:\\Windows\\Temp')
        count = 0
        for item in os.listdir(temp_path):
            try:
                item_path = os.path.join(temp_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    count += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    count += 1
            except:
                pass
        return f"Cleared {count} temporary items."
    except:
        return "Couldn't clear temp files."

# --- IP ADDRESS ---
def get_ip_address():
    """Get public and local IP addresses"""
    try:
        # Public IP
        public_ip = requests.get('https://api.ipify.org', timeout=5).text
        
        # Local IP
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        return f"Public IP: {public_ip}, Local IP: {local_ip}"
    except:
        return "Couldn't get IP address."

# --- STOPWATCH ---
stopwatch_start = None
stopwatch_running = False

def start_stopwatch():
    """Start a stopwatch"""
    global stopwatch_start, stopwatch_running
    stopwatch_start = time.time()
    stopwatch_running = True
    return "Stopwatch started!"

def stop_stopwatch():
    """Stop the stopwatch and get elapsed time"""
    global stopwatch_running
    if not stopwatch_running:
        return "Stopwatch not running."
    
    elapsed = time.time() - stopwatch_start
    stopwatch_running = False
    
    minutes = int(elapsed // 60)
    seconds = elapsed % 60
    
    if minutes > 0:
        return f"Time: {minutes} minutes and {seconds:.1f} seconds"
    return f"Time: {seconds:.1f} seconds"

# --- HABIT TRACKER ---
HABITS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chaos_habits.json")

def load_habits():
    try:
        with open(HABITS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_habits(habits):
    with open(HABITS_FILE, 'w') as f:
        json.dump(habits, f, indent=2)

def track_habit(habit_name):
    """Mark a habit as done for today"""
    habits = load_habits()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if habit_name not in habits:
        habits[habit_name] = {'streak': 0, 'dates': []}
    
    if today not in habits[habit_name]['dates']:
        habits[habit_name]['dates'].append(today)
        habits[habit_name]['streak'] = len(habits[habit_name]['dates'])
        save_habits(habits)
        return f"Habit '{habit_name}' tracked! Streak: {habits[habit_name]['streak']} days!"
    
    return f"You already tracked '{habit_name}' today! Streak: {habits[habit_name]['streak']} days."

def get_habit_stats():
    """Get all habit statistics"""
    habits = load_habits()
    if not habits:
        return "No habits tracked yet. Say 'track habit [name]' to start!"
    
    result = "Your habits:\n"
    for name, data in habits.items():
        result += f"- {name}: {data['streak']} day streak\n"
    return result

# ==================== END PHASE 6 FUNCTIONS ====================

# ==================== INTERACTIVE MENU & TYPE MODE ====================

PERSONALITY_OPTIONS = [
    ("butler", "British Butler - Formal and sophisticated"),
    ("jarvis", "JARVIS - American AI assistant style"),
    ("friday", "FRIDAY - Female AI assistant"),
    ("egirl", "E-Girl - Cute and playful"),
    ("wizard", "Wizard - Mysterious and wise"),
    ("narrator", "Narrator - Storytelling voice"),
    ("professional", "Professional - Business formal"),
    ("casual", "Casual - Friendly and relaxed"),
    ("pirate", "Pirate - Yarr matey!"),
    ("robot", "Robot - Cold and mechanical"),
]

def show_settings_menu():
    """Display interactive settings menu"""
    global current_voice, type_input_mode, voice_mode, ollama_enabled
    
    while True:
        print("\n" + "=" * 60)
        print("  🎛️  CHAOS SETTINGS MENU")
        print("=" * 60)
        print("  1. Change Voice/Personality")
        print("  2. Toggle Input Mode (Voice/Type)")
        print("  3. Toggle Output Mode (Voice/Text)")
        print(f"  4. Toggle AI Brain (Ollama) [{'ON' if ollama_enabled else 'OFF'}]")
        print("  5. View All Available Voices")
        print("  6. View All CHAOS Features")
        print("  7. Edit Conversation History")
        print("  8. Clear Conversation History")
        print("  9. Back to CHAOS")
        print("=" * 60)
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == '1':
            # Voice personality submenu
            print("\n" + "-" * 40)
            print("  🎤 SELECT PERSONALITY")
            print("-" * 40)
            for i, (key, desc) in enumerate(PERSONALITY_OPTIONS, 1):
                print(f"  {i}. {desc}")
            print("-" * 40)
            
            voice_choice = input("Enter number (1-10): ").strip()
            try:
                idx = int(voice_choice) - 1
                if 0 <= idx < len(PERSONALITY_OPTIONS):
                    voice_key = PERSONALITY_OPTIONS[idx][0]
                    current_voice = VOICE_MAP[voice_key]
                    print(f"✓ Voice changed to {PERSONALITY_OPTIONS[idx][1]}")
                    speak("Voice updated. How do I sound now?", force_voice=True)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")
        
        elif choice == '2':
            # Toggle input mode
            type_input_mode = not type_input_mode
            mode = "TYPE MODE" if type_input_mode else "VOICE MODE"
            print(f"✓ Input mode set to: {mode}")
            if type_input_mode:
                print("  (Type your commands, press Enter to submit)")
            else:
                print("  (Speak your commands)")
        
        elif choice == '3':
            # Toggle output mode
            voice_mode = not voice_mode
            mode = "VOICE" if voice_mode else "TEXT ONLY"
            print(f"✓ Output mode set to: {mode}")

        elif choice == '4':
            # Toggle Ollama
            ollama_enabled = not ollama_enabled
            status = "ENABLED" if ollama_enabled else "DISABLED"
            print(f"✓ AI Brain (Ollama) is now {status}")
            if ollama_enabled:
                print("  (CHAOS will consult AI for complex questions)")
                speak("AI brain connected. I can now answer complex questions.", force_voice=True)
            else:
                print("  (CHAOS will only respond to basic commands)")
                speak("AI brain disconnected. I will only perform system commands now.", force_voice=True)
        
        elif choice == '5':
            # List all voices
            print("\n" + "-" * 40)
            print("  📢 ALL AVAILABLE VOICES")
            print("-" * 40)
            voice_list = list(VOICE_MAP.keys())
            for i in range(0, len(voice_list), 5):
                row = voice_list[i:i+5]
                print("  " + ", ".join(row))
            print("-" * 40)
            input("Press Enter to continue...")
        
        elif choice == '6':
            # Show all features
            print("\n" + "=" * 60)
            print("  📋 ALL CHAOS FEATURES")
            print("=" * 60)
            print("\n  🎤 VOICE & INPUT:")
            print("    • 'type mode' / 'voice mode' - Switch input method")
            print("    • 'text mode' - Disable voice output")
            print("    • 'switch to [voice]' - Change personality (butler, jarvis, egirl...)")
            print("    • 'enable wake word' - 'Hey CHAOS' always listening")
            print("\n  🧠 SMART CLIPBOARD:")
            print("    • 'summarize clipboard' - AI summary of copied text")
            print("    • 'translate clipboard to [language]' - Translate copied text")
            print("    • 'explain this code' - Explain copied code")
            print("\n  💡 KNOWLEDGE & MEMORY:")
            print("    • 'remember my [X] is [Y]' - Store facts")
            print("    • 'what is my [X]?' - Recall stored facts")
            print("    • 'wikipedia [topic]' - Quick wiki lookup")
            print("    • Ask any question - AI-powered answers")
            print("\n  ⏰ PRODUCTIVITY:")
            print("    • 'start pomodoro' - 25 min focus timer")
            print("    • 'remind me to [X] in [Y] minutes' - Set reminder")
            print("    • 'add task [X]' / 'show todos' - Todo list")
            print("    • 'start dictation' - Voice-to-typing")
            print("    • 'start stopwatch' / 'stop stopwatch' - Timer")
            print("\n  🎲 FUN & RANDOM:")
            print("    • 'tell me a joke' - Programmer jokes")
            print("    • 'motivate me' - Inspirational quotes")
            print("    • 'flip a coin' / 'roll a dice' - Random picks")
            print("    • 'pick one from [X, Y, Z]' - Random choice")
            print("\n  🖥️ SYSTEM CONTROL:")
            print("    • 'system health' - CPU, RAM, disk status")
            print("    • 'running processes' / 'kill [app]' - Process manager")
            print("    • 'generate password' - Strong password")
            print("    • 'my ip' - Show IP address")
            print("    • 'speed test' - Internet speed")
            print("    • 'dark mode' / 'light mode' - Toggle theme")
            print("    • 'empty recycle bin' / 'clear temp files' - Cleanup")
            print("\n  📹 SCREEN & FILES:")
            print("    • 'scan screen' / 'enable true sight' - Screen analysis")
            print("    • 'screenshot' - Take screenshot")
            print("    • 'record my screen' - Screen recording (MP4)")
            print("    • 'find file [name]' - Search files")
            print("    • 'generate qr code for [text]' - Create QR")
            print("\n  💬 APPS & WEB:")
            print("    • 'open [app]' - Launch applications")
            print("    • 'open youtube/google' - Open websites")
            print("    • 'search [query]' - Google search")
            print("    • 'play/pause/next song' - Media control")
            print("\n  📊 HABITS & TRACKING:")
            print("    • 'track habit [name]' - Log daily habit")
            print("    • 'my habits' - View habit streaks")
            print("    • 'export conversation' - Save chat to file")
            print("-" * 60)
            input("Press Enter to continue...")
        
        elif choice == '7':
            # Edit conversation history
            history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversation_history.json")
            if os.path.exists(history_file):
                print(f"\n📂 Opening conversation history: {history_file}")
                try:
                    os.startfile(history_file)
                    print("✓ File opened in default JSON editor")
                except:
                    print(f"Could not auto-open. File location:\n  {history_file}")
            else:
                print("No conversation history file found yet.")
            input("Press Enter to continue...")
        
        elif choice == '8':
            # Clear conversation history
            history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversation_history.json")
            confirm = input("⚠️  Clear ALL conversation history? (yes/no): ").strip().lower()
            if confirm == 'yes':
                try:
                    with open(history_file, 'w') as f:
                        json.dump([], f)
                    print("✓ Conversation history cleared!")
                except:
                    print("Could not clear history.")
            else:
                print("Cancelled.")
        
        elif choice == '9':
            return
        
        else:
            print("Invalid choice. Enter 1-9.")

def get_typed_input():
    """Get input from keyboard instead of microphone"""
    print("\n[Type your command (or 'menu' for settings, 'voice mode' to switch back)]")
    try:
        user_input = input("You: ").strip()
        if user_input:
            return user_input.lower(), 'en'
        return None, 'en'
    except KeyboardInterrupt:
        return None, 'en'

# ==================== END INTERACTIVE MENU ====================

# ==================== END PHASE 5 FUNCTIONS ====================


def extract_feature_request(query):
    """Extract the actual feature request from the command and resolve pronouns"""
    triggers = [
        'self update', 'upgrade yourself', 'enhance yourself', 'improve yourself',
        'update yourself', 'add feature', 'implement', 'give yourself',
        'ask antigravity to', 'tell antigravity to', 'ask anti gravity to', 'tell anti gravity to',
        'ask antigravity', 'tell antigravity', 'ask anti gravity', 'tell anti gravity',
        'antigravity', 'anti gravity',
        'make yourself', 'learn to', 'learn how to'
    ]
    
    # Sort triggers by length (descending) to match longest first
    triggers.sort(key=len, reverse=True)
    
    request = query
    for trigger in triggers:
        if trigger in query:
            # removing trigger
            request = query.split(trigger, 1)[-1].strip()
            # remove leading 'to ' if present (e.g. "learn how to [to] fly")
            if request.startswith('to '):
                 request = request[3:].strip()
            if request:
                break
    
    # Pronoun resolution - replace "you/yourself" with "CHAOS"
    pronoun_map = {
        ' into you': ' into CHAOS',
        ' to you': ' to CHAOS',
        ' for you': ' for CHAOS',
        'yourself': 'CHAOS',
        ' you ': ' CHAOS ',
        'your ': "CHAOS's ",
    }
    
    for pronoun, replacement in pronoun_map.items():
        request = request.replace(pronoun, replacement)
    
    # Clean up trailing "you" at end of sentence
    if request.endswith(' you'):
        request = request[:-4] + ' CHAOS'
                
    return request if request else None

def type_to_antigravity(prompt):
    """Type the prompt into Antigravity (VS Code)"""
    try:
        # 1. Find VS Code window - try multiple title patterns
        all_windows = gw.getAllWindows()
        vscode_window = None
        
        # Priority order: Antigravity, Visual Studio Code, Code, .py
        for pattern in ['Antigravity', 'Visual Studio Code', 'VS Code', 'Code', '.py']:
            for w in all_windows:
                if pattern.lower() in w.title.lower() and w.title.strip():
                    vscode_window = w
                    break
            if vscode_window:
                break
            
        if not vscode_window:
            print("[Error: VS Code window not found]")
            return False
            
        print(f"[Found window: {vscode_window.title}]")
        
        # 2. Focus the window
        if not vscode_window.isActive:
            try:
                vscode_window.activate()
                time.sleep(0.5) 
            except:
                try:
                    vscode_window.minimize()
                    vscode_window.restore()
                except:
                    pass
                time.sleep(0.5)
        
        # 3. Type text using clipboard for speed and special character support
        import pyperclip
        full_command = f"Antigravity, please {prompt}"
        pyperclip.copy(full_command)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.2)
        pyautogui.press('enter')
        
        return True
    except Exception as e:
        print(f"[Error typing to Antigravity: {e}]")
        return False

def analyze_own_code(feature_request):
    """Analyze CHAOS.py and create a smart prompt for Antigravity"""
    try:
        # Read own source code
        script_path = os.path.abspath(__file__)
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Extract function names for context
        import ast
        tree = ast.parse(code)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Create a smart prompt
        prompt = f"""Please implement the following feature in CHAOS.py:

**Feature Request:** {feature_request}

**Current Functions:** {', '.join(functions[:20])}... (and more)

**Guidelines:**
- Maintain existing code style
- Add new command triggers in process_command()
- Use existing helper functions where possible
- Keep responses short and natural

Please implement this feature."""
        
        return prompt
    except Exception as e:
        return f"Please implement: {feature_request}. (Error analyzing code: {e})"

def read_antigravity_response():
    """Scan the screen and read Antigravity's response"""
    try:
        # Take screenshot and use vision model
        screenshot = pyautogui.screenshot()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
            screenshot.save(f.name)
            temp_file = f.name
        
        # Use vision model to read screen
        with open(temp_file, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            ollama_api_url,
            json={
                "model": ollama_vision_model,
                "messages": [{
                    "role": "user",
                    "content": "Read the text in the VS Code chat panel on the right side of the screen. Summarize what Antigravity is saying.",
                    "images": [image_data]
                }],
                "stream": False
            },
            timeout=60
        )
        
        os.remove(temp_file)
        
        if response.status_code == 200:
            return response.json()['message']['content']
        else:
            return "Could not read the response."
    except Exception as e:
        return f"Error reading response: {e}"

def find_antigravity_window():
    """Find and focus the VS Code window with Antigravity"""
    try:
        all_windows = gw.getAllWindows()
        vscode_window = None
        
        for pattern in ['Antigravity', 'Visual Studio Code', 'VS Code', 'Code']:
            for w in all_windows:
                if pattern.lower() in w.title.lower() and w.title.strip():
                    vscode_window = w
                    break
            if vscode_window:
                break
        
        if vscode_window:
            try:
                vscode_window.activate()
            except:
                vscode_window.minimize()
                vscode_window.restore()
            return True
        return False
    except:
        return False

def process_command(query, history, language='en'):
    """Process a single command and return (response_text, should_exit, was_interrupted, interrupted_query)"""
    global voice_mode, current_language, urdu_mode, current_voice, awaiting_confirmation, pending_antigravity_request, last_context
    import re  # Import here to ensure it's available throughout the function
    
    # Set current language for TTS
    current_language = language
    
    # Resolve "it" / "that" to last_context if applicable
    if last_context and any(x in query for x in ['open it', 'show it', 'view it', 'open that', 'show that']):
        # Replace the pronoun with actual path/name
        if os.path.exists(last_context):
            os.startfile(last_context)
            was_interrupted, int_text = speak(f"Opening {os.path.basename(last_context)}")
            return None, False, was_interrupted, int_text
        else:
            was_interrupted, int_text = speak(f"I can't find what you're referring to.")
            return None, False, was_interrupted, int_text
    
    # SECURITY: All file operations restricted to workspace folder only
    WORKSPACE = r"c:\Users\User\OneDrive\Documents\STUDY\PROJECT C.H.A.O.S\workspace"
    
    # Ensure workspace exists
    if not os.path.exists(WORKSPACE):
        os.makedirs(WORKSPACE, exist_ok=True)
    
    def is_safe_path(filepath):
        """Check if a path is within the safe workspace"""
        try:
            # Resolve to absolute path and check if it starts with workspace
            real_path = os.path.realpath(filepath)
            workspace_path = os.path.realpath(WORKSPACE)
            return real_path.startswith(workspace_path)
        except:
            return False
    
    # DEACTIVATE / SLEEP command
    if any(x in query for x in ['deactivate', 'sleep mode', 'standby', 'go to sleep']):
        global is_awake
        is_awake = False
        speak("Entering standby mode. Say 'CHAOS Activate' to wake me up.", allow_interrupt=False)
        print("\n[STANDBY MODE - Listening for 'CHAOS Activate']")
        return None, False, False, None
        
    # SHUTDOWN / EXIT command
    elif any(x in query for x in ['shutdown system', 'exit program', 'terminate']):
        speak("Shutting down completely. Goodbye, Sir.", allow_interrupt=False)
        return None, True, False, None
    
    # SCAN SCREEN command - analyze what's on screen
    elif any(x in query for x in ['scan screen', 'scan my screen', 'what do you see', 'analyze screen', 'look at my screen', 'whats on my screen', "what's on my screen"]):
        was_interrupted, int_text = speak("Scanning your screen, please wait...")
        if was_interrupted:
            return None, False, was_interrupted, int_text
        
        print("[Taking screenshot and analyzing...]")
        
        # Get custom prompt if specified
        custom_prompt = None
        if 'and tell me' in query:
            custom_prompt = query.split('and tell me')[-1].strip()
        elif 'and explain' in query:
            custom_prompt = "Explain " + query.split('and explain')[-1].strip()
        
        if custom_prompt:
            description = scan_screen(custom_prompt)
        else:
            description = scan_screen()
        
        was_interrupted, int_text = speak(description)
        return None, False, was_interrupted, int_text
    
    # VOICE CHANGE command - switch accent/personality
    elif any(x in query for x in ['switch to', 'change voice', 'use voice', 'change to', 'switch voice']):
        # Extract the voice name from the query
        voice_name = None
        for trigger in ['switch to', 'change voice to', 'use voice', 'change to', 'switch voice to']:
            if trigger in query:
                voice_name = query.split(trigger)[-1].strip()
                # Remove "voice" suffix if present
                voice_name = voice_name.replace(' voice', '').replace(' accent', '').strip()
                break
        
        if voice_name and voice_name.lower() in VOICE_MAP:
            current_voice = VOICE_MAP[voice_name.lower()]
            was_interrupted, int_text = speak(f"Voice changed to {voice_name}. How do I sound?")
            return None, False, was_interrupted, int_text
        else:
            # List some available voices
            available = "butler, jarvis, friday, egirl, wizard, professional, casual"
            was_interrupted, int_text = speak(f"I don't recognize that voice. Try: {available}")
            return None, False, was_interrupted, int_text
    
    # TRUE SIGHT commands - proactive screen monitoring (like Dota 2!)
    elif any(x in query for x in ['enable true sight', 'activate true sight', 'true sight on', 'true sight enable', 'start true sight']):
        start_screen_watcher()
        was_interrupted, int_text = speak("True Sight activated. I can now see all. Errors cannot hide from me.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['disable true sight', 'deactivate true sight', 'true sight off', 'true sight disable', 'stop true sight']):
        stop_screen_watcher()
        was_interrupted, int_text = speak("True Sight deactivated. Returning to normal vision.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['true sight status', 'is true sight on', 'is true sight active', 'true sight check']):
        if screen_watcher_enabled:
            was_interrupted, int_text = speak("True Sight is active. I am watching over your code.")
        else:
            was_interrupted, int_text = speak("True Sight is dormant. Say 'enable true sight' to awaken it.")
        return None, False, was_interrupted, int_text
    
    # ==================== PHASE 5 COMMANDS (NEW FEATURES) ====================
    
    # DICTATION MODE - must check first so we can type instead of process
    elif dictation_mode and not any(x in query for x in ['stop dictation', 'end dictation', 'dictation off']):
        # In dictation mode, type what was said
        type_text(query)
        print(f"[Typed: {query}]")
        return None, False, False, None
    
    # SMART CLIPBOARD commands
    elif any(x in query for x in ['summarize clipboard', 'summarize what i copied', 'summarize my clipboard', 'tldr clipboard']):
        was_interrupted, int_text = speak("Summarizing clipboard contents...")
        result = summarize_clipboard()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['translate clipboard', 'translate what i copied']):
        # Extract target language if specified
        target = "Urdu"
        if 'to ' in query:
            target = query.split('to ')[-1].strip().title()
        was_interrupted, int_text = speak(f"Translating clipboard to {target}...")
        result = translate_clipboard(target)
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['explain clipboard', 'explain this code', 'explain what i copied', 'what does this code do']):
        was_interrupted, int_text = speak("Analyzing the code...")
        result = explain_clipboard_code()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # QUICK MATH & CONVERSIONS
    elif any(x in query for x in ['calculate', 'convert', 'how much is', 'what is']) and any(x in query for x in ['%', 'usd', 'pkr', 'eur', 'gbp', 'inr', 'km', 'mile', 'celsius', 'fahrenheit', '+', '-', '*', '/']):
        result = quick_math(query)
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # PASSWORD GENERATOR
    elif any(x in query for x in ['generate password', 'create password', 'make password', 'random password', 'strong password']):
        # Extract length if specified
        length = 16
        import re
        length_match = re.search(r'(\d+)\s*character', query)
        if length_match:
            length = int(length_match.group(1))
        
        password = generate_password(length)
        # Copy to clipboard
        try:
            import pyperclip
            pyperclip.copy(password)
            was_interrupted, int_text = speak(f"Generated a {length} character password and copied it to clipboard.")
            print(f"[Password: {password}]")
        except:
            was_interrupted, int_text = speak(f"Here's your password: {password}")
            print(f"[Password: {password}]")
        return None, False, was_interrupted, int_text
    
    # POMODORO TIMER
    elif any(x in query for x in ['start pomodoro', 'begin pomodoro', 'pomodoro start', 'focus mode', 'start focus']):
        result = start_pomodoro()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['stop pomodoro', 'end pomodoro', 'cancel pomodoro', 'stop focus']):
        result = stop_pomodoro()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # DICTATION MODE
    elif any(x in query for x in ['start dictation', 'begin dictation', 'dictation mode', 'type what i say']):
        result = start_dictation()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['stop dictation', 'end dictation', 'dictation off']):
        result = stop_dictation()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # PROCESS MONITOR
    elif any(x in query for x in ['running processes', 'what is using ram', 'what is using memory', 'show processes', 'top processes']):
        processes = get_running_processes()
        if processes:
            top3 = ", ".join([f"{p['name']} at {p['memory']:.1f}%" for p in processes[:3]])
            was_interrupted, int_text = speak(f"Top memory users: {top3}")
            print("[Top 10 processes by memory:]")
            for p in processes:
                print(f"  {p['name']}: {p['memory']:.1f}% RAM, {p['cpu']:.1f}% CPU")
        else:
            was_interrupted, int_text = speak("Couldn't get process list. Install psutil package.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['kill process', 'kill app', 'end task', 'close app', 'force close']):
        # Extract app name
        app_name = query.split('kill ')[-1].split('close ')[-1].split('end ')[-1].strip()
        if kill_process(app_name):
            was_interrupted, int_text = speak(f"Terminated {app_name}.")
        else:
            was_interrupted, int_text = speak(f"Couldn't find or kill {app_name}.")
        return None, False, was_interrupted, int_text
    
    # SYSTEM HEALTH
    elif any(x in query for x in ['system health', 'system status', 'how is my pc', 'pc status', 'computer health', 'check system']):
        health = get_system_health()
        was_interrupted, int_text = speak(health)
        return None, False, was_interrupted, int_text
    
    # MEMORY SYSTEM (Remember/Recall)
    elif 'remember that' in query or 'remember my' in query:
        # Extract key and value: "remember that my name is X" or "remember my birthday is X"
        import re
        match = re.search(r'remember (?:that )?(?:my )?(.+?) is (.+)', query)
        if match:
            key = match.group(1).strip()
            value = match.group(2).strip()
            result = remember_fact(key, value)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("What should I remember? Say 'remember that X is Y'.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['what is my', 'what was my', 'whats my', "what's my", 'recall my']):
        # Extract what to recall
        import re
        match = re.search(r'(?:what is|what was|whats|what\'s|recall) (?:my )?(.+?)(?:\?|$)', query)
        if match:
            key = match.group(1).strip()
            value = recall_fact(key)
            if value:
                was_interrupted, int_text = speak(f"Your {key} is {value}.")
            else:
                was_interrupted, int_text = speak(f"I don't have your {key} stored. Tell me by saying 'remember that my {key} is...'")
        else:
            was_interrupted, int_text = speak("What would you like me to recall?")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['forget my', 'forget about', 'delete memory']):
        import re
        match = re.search(r'forget (?:my |about )?(.+)', query)
        if match:
            key = match.group(1).strip()
            result = forget_fact(key)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("What should I forget?")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['list memories', 'what do you remember', 'show memories', 'all memories']):
        result = list_memories()
        was_interrupted, int_text = speak(result)
        print(result)
        return None, False, was_interrupted, int_text
    
    # CLIPBOARD HISTORY
    elif any(x in query for x in ['clipboard history', 'past clipboard', 'what did i copy', 'recent copies']):
        result = get_clipboard_history()
        was_interrupted, int_text = speak(result)
        print(result)
        return None, False, was_interrupted, int_text
    
    # FILE SEARCH
    elif any(x in query for x in ['find file', 'search for file', 'where is', 'locate file', 'find my']):
        # Extract search query
        import re
        match = re.search(r'(?:find|search for|where is|locate)(?: file| my)? (.+)', query)
        if match:
            search_query = match.group(1).strip()
            was_interrupted, int_text = speak(f"Searching for {search_query}...")
            files = search_files(search_query)
            if files:
                was_interrupted, int_text = speak(f"Found {len(files)} files. First result: {os.path.basename(files[0])}")
                print("[Search Results:]")
                for f in files:
                    print(f"  {f}")
            else:
                was_interrupted, int_text = speak(f"Couldn't find any files matching {search_query}.")
        else:
            was_interrupted, int_text = speak("What file should I search for?")
        return None, False, was_interrupted, int_text
    
    # CONVERSATION EXPORT
    elif any(x in query for x in ['save conversation', 'export conversation', 'export chat', 'save our chat']):
        success, result = export_conversation(WORKSPACE)
        if success:
            was_interrupted, int_text = speak(f"Conversation exported to {result}")
        else:
            was_interrupted, int_text = speak(f"Couldn't export: {result}")
        return None, False, was_interrupted, int_text
    
    # SCREEN RECORDING
    elif any(x in query for x in ['record screen', 'record my screen', 'start recording', 'screen record', 'capture video']):
        # Extract duration if specified
        duration = None
        import re
        duration_match = re.search(r'for (\d+)\s*(second|minute|min|sec)', query)
        if duration_match:
            amount = int(duration_match.group(1))
            unit = duration_match.group(2)
            if 'min' in unit:
                duration = amount * 60
            else:
                duration = amount
        
        result = start_screen_recording(WORKSPACE, duration)
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['stop recording', 'end recording', 'stop screen record']):
        result = stop_screen_recording()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # WAKE WORD DETECTION
    elif any(x in query for x in ['enable wake word', 'start wake word', 'always listen', 'enable hey chaos', 'listen for wake word']):
        result = start_wake_word_detection()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['disable wake word', 'stop wake word', 'stop always listening', 'disable hey chaos']):
        result = stop_wake_word_detection()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # ==================== PHASE 6 COMMANDS (FUN & MORE!) ====================
    
    # JOKES
    elif any(x in query for x in ['tell me a joke', 'tell joke', 'joke please', 'make me laugh', 'say something funny']):
        joke = tell_joke()
        was_interrupted, int_text = speak(joke)
        return None, False, was_interrupted, int_text
    
    # WIKIPEDIA
    elif any(x in query for x in ['wikipedia', 'wiki', 'look up', 'what is a', 'who is', 'tell me about']):
        import re
        match = re.search(r'(?:wikipedia|wiki|look up|what is a|what is|who is|tell me about)\s+(.+?)(?:\?|$)', query)
        if match:
            topic = match.group(1).strip()
            was_interrupted, int_text = speak(f"Looking up {topic}...")
            result = wikipedia_summary(topic)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("What would you like me to look up?")
        return None, False, was_interrupted, int_text
    
    # REMINDERS
    elif any(x in query for x in ['remind me', 'set reminder', 'reminder']):
        import re
        match = re.search(r'remind me (?:to |about )?(.+?) in (\d+)\s*(minute|min|hour)', query)
        if match:
            message = match.group(1).strip()
            amount = int(match.group(2))
            unit = match.group(3)
            minutes = amount * 60 if 'hour' in unit else amount
            result = set_reminder(message, minutes)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("Say 'remind me to [task] in [X] minutes'")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['list reminders', 'show reminders', 'my reminders']):
        result = list_reminders()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # TODO LIST
    elif any(x in query for x in ['add todo', 'add task', 'add to list', 'new task']):
        import re
        match = re.search(r'(?:add todo|add task|add to list|new task)\s+(.+)', query)
        if match:
            task = match.group(1).strip()
            result = add_todo(task)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("What task should I add?")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['show todo', 'list todo', 'my todos', 'my tasks', 'todo list', 'task list']):
        result = list_todos()
        was_interrupted, int_text = speak(result)
        print(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['complete task', 'done task', 'finish task', 'complete todo']):
        import re
        match = re.search(r'(\d+)', query)
        if match:
            index = int(match.group(1))
            result = complete_todo(index)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("Which task number?")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['clear completed', 'clear done', 'clean todo']):
        result = clear_todos()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # QR CODE
    elif any(x in query for x in ['generate qr', 'create qr', 'make qr', 'qr code']):
        import re
        match = re.search(r'(?:generate|create|make)\s*qr\s*(?:code)?\s*(?:for|with|of)?\s*(.+)', query)
        if match:
            text = match.group(1).strip()
            success, result, filepath = generate_qr_code(text, WORKSPACE)
            if success:
                was_interrupted, int_text = speak(f"QR code created: {result}")
                print(f"[QR Code saved: {filepath}]")
            else:
                was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("What text should I encode in the QR?")
        return None, False, was_interrupted, int_text
    
    # SPEED TEST
    elif any(x in query for x in ['speed test', 'test internet', 'internet speed', 'how fast is my internet']):
        was_interrupted, int_text = speak("Running speed test, please wait...")
        result = internet_speed_test()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # MOTIVATION
    elif any(x in query for x in ['motivate me', 'motivation', 'inspire me', 'give me a quote', 'inspirational quote', 'i need motivation']):
        quote = get_motivation()
        was_interrupted, int_text = speak(quote)
        return None, False, was_interrupted, int_text
    
    # RANDOM PICKER
    elif any(x in query for x in ['pick one', 'choose between', 'pick between', 'random pick', 'choose from']):
        import re
        match = re.search(r'(?:pick one|choose between|pick between|random pick|choose from)\s*(?:from)?\s*(.+)', query)
        if match:
            options = match.group(1).strip()
            result = random_pick(options)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("Give me options separated by commas!")
        return None, False, was_interrupted, int_text
    
    # COIN FLIP
    elif any(x in query for x in ['flip coin', 'flip a coin', 'heads or tails', 'coin flip']):
        result = flip_coin()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # DICE ROLL
    elif any(x in query for x in ['roll dice', 'roll a dice', 'roll die', 'throw dice']):
        import re
        match = re.search(r'(\d+)\s*(?:sided|sides)', query)
        sides = int(match.group(1)) if match else 6
        result = roll_dice(sides)
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # RANDOM NUMBER
    elif any(x in query for x in ['random number', 'give me a number', 'pick a number']):
        import re
        match = re.search(r'between (\d+) and (\d+)', query)
        if match:
            min_val = int(match.group(1))
            max_val = int(match.group(2))
            result = random_number(min_val, max_val)
        else:
            result = random_number()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # WINDOW SNAPPING
    elif any(x in query for x in ['snap window', 'window left', 'window right', 'snap left', 'snap right', 'maximize window', 'minimize window']):
        if 'left' in query:
            result = snap_window('left')
        elif 'right' in query:
            result = snap_window('right')
        elif 'maximize' in query or 'max' in query:
            result = snap_window('maximize')
        elif 'minimize' in query or 'min' in query:
            result = snap_window('minimize')
        else:
            result = "Say left, right, maximize, or minimize."
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # DARK MODE
    elif any(x in query for x in ['toggle dark mode', 'dark mode', 'light mode', 'switch theme']):
        result = toggle_dark_mode()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # SYSTEM CLEANUP
    elif any(x in query for x in ['empty recycle bin', 'clear recycle bin', 'empty trash']):
        result = empty_recycle_bin()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['clear temp files', 'clean temp', 'delete temp files', 'clear temporary']):
        result = clear_temp_files()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # IP ADDRESS
    elif any(x in query for x in ['my ip', 'ip address', 'what is my ip', 'get ip']):
        result = get_ip_address()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # STOPWATCH
    elif any(x in query for x in ['start stopwatch', 'begin stopwatch', 'stopwatch start']):
        result = start_stopwatch()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['stop stopwatch', 'stopwatch stop', 'end stopwatch', 'stopwatch time']):
        result = stop_stopwatch()
        was_interrupted, int_text = speak(result)
        return None, False, was_interrupted, int_text
    
    # HABIT TRACKER
    elif any(x in query for x in ['track habit', 'log habit', 'did my', 'completed habit']):
        import re
        match = re.search(r'(?:track habit|log habit|did my|completed habit)\s+(.+)', query)
        if match:
            habit = match.group(1).strip()
            result = track_habit(habit)
            was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("Which habit should I track?")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['habit stats', 'my habits', 'show habits', 'habit tracker', 'habit progress']):
        result = get_habit_stats()
        was_interrupted, int_text = speak(result)
        print(result)
        return None, False, was_interrupted, int_text
    
    # ==================== PHASE 1 COMMANDS ====================
    
    # SCREENSHOT command - save screenshot to workspace
    elif any(x in query for x in ['take screenshot', 'take a screenshot', 'capture screen', 'screenshot', 'screen capture']):
        was_interrupted, int_text = speak("Taking screenshot...")
        success, filename, filepath = take_screenshot(WORKSPACE)
        if success:
            was_interrupted, int_text = speak(f"Screenshot saved as {filename}")
            print(f"[Screenshot saved: {filepath}]")
        else:
            was_interrupted, int_text = speak(f"Sorry, I couldn't take the screenshot. {filename}")
        return None, False, was_interrupted, int_text
    
    # VOLUME CONTROL commands
    elif 'volume' in query or 'mute' in query or 'unmute' in query:
        if 'mute' in query or 'unmute' in query:
            new_state = toggle_mute()
            if new_state is not None:
                status = "muted" if new_state else "unmuted"
                was_interrupted, int_text = speak(f"Volume {status}")
            else:
                was_interrupted, int_text = speak("Sorry, I couldn't control the volume.")
        elif 'up' in query or 'increase' in query or 'higher' in query:
            current = get_volume()
            new_level = min(100, current + 10)
            set_volume(new_level)
            was_interrupted, int_text = speak(f"Volume set to {new_level} percent")
        elif 'down' in query or 'decrease' in query or 'lower' in query:
            current = get_volume()
            new_level = max(0, current - 10)
            set_volume(new_level)
            was_interrupted, int_text = speak(f"Volume set to {new_level} percent")
        elif 'max' in query or 'maximum' in query or 'full' in query:
            set_volume(100)
            was_interrupted, int_text = speak("Volume set to maximum")
        elif 'min' in query or 'minimum' in query:
            set_volume(10)
            was_interrupted, int_text = speak("Volume set to minimum")
        else:
            # Try to extract a number
            numbers = re.findall(r'\d+', query)
            if numbers:
                level = int(numbers[0])
                set_volume(level)
                was_interrupted, int_text = speak(f"Volume set to {level} percent")
            else:
                current = get_volume()
                was_interrupted, int_text = speak(f"Current volume is {current} percent")
        return None, False, was_interrupted, int_text
    
    # APP LAUNCHER commands
    elif any(x in query for x in ['open ', 'launch ', 'start ', 'run ']):
        # Extract app name
        app_name = query
        for prefix in ['open ', 'launch ', 'start ', 'run ']:
            if prefix in app_name:
                app_name = app_name.split(prefix, 1)[-1].strip()
                break
        
        if app_name:
            was_interrupted, int_text = speak(f"Opening {app_name}")
            success, result = launch_app(app_name)
            if not success:
                was_interrupted, int_text = speak(f"Sorry, I couldn't open {app_name}")
        else:
            was_interrupted, int_text = speak("What would you like me to open?")
        return None, False, was_interrupted, int_text
    
    # QUICK NOTES command
    elif any(x in query for x in ['take a note', 'take note', 'save note', 'note:', 'remember']):
        # Extract note content
        note_content = query
        for prefix in ['take a note ', 'take note ', 'save note ', 'note: ', 'note ', 'remember ']:
            if prefix in note_content:
                note_content = note_content.split(prefix, 1)[-1].strip()
                break
        
        if note_content and note_content != query:
            if save_note(note_content, WORKSPACE):
                was_interrupted, int_text = speak(f"Note saved: {note_content}")
                print(f"[Note saved to workspace/notes.txt]")
            else:
                was_interrupted, int_text = speak("Sorry, I couldn't save the note.")
        else:
            was_interrupted, int_text = speak("What would you like me to note down?")
        return None, False, was_interrupted, int_text
    
    # READ NOTES command
    elif any(x in query for x in ['read notes', 'read my notes', 'show notes', 'what are my notes']):
        notes_file = os.path.join(WORKSPACE, "notes.txt")
        if os.path.exists(notes_file):
            with open(notes_file, 'r', encoding='utf-8') as f:
                notes = f.readlines()[-5:]  # Last 5 notes
            if notes:
                notes_text = "Your recent notes: " + ". Next, ".join([n.strip().split('] ')[-1] for n in notes])
                was_interrupted, int_text = speak(notes_text)
            else:
                was_interrupted, int_text = speak("Your notes are empty.")
        else:
            was_interrupted, int_text = speak("You don't have any notes yet.")
        return None, False, was_interrupted, int_text
    
    # CALCULATOR command
    elif any(x in query for x in ['calculate', 'what is', "what's", 'compute', 'math']):
        # Extract math expression
        expr = query
        for prefix in ['calculate ', "what's ", 'what is ', 'compute ', 'math ']:
            if prefix in expr:
                expr = expr.split(prefix, 1)[-1].strip()
                break
        
        result, error = calculate(expr)
        if result is not None:
            # Format nicely
            if isinstance(result, float):
                result = round(result, 4)
            was_interrupted, int_text = speak(f"The answer is {result}")
            print(f"[Calculation: {expr} = {result}]")
        else:
            was_interrupted, int_text = speak(f"Sorry, I couldn't calculate that. {error}")
        return None, False, was_interrupted, int_text
    
    # ==================== END PHASE 1 COMMANDS ====================
    
    # ==================== PHASE 2 COMMANDS ====================
    
    # SYSTEM INFO commands
    # Use word boundaries for short words to avoid matching "program" -> "ram"
    elif any(x in query for x in ['battery', 'cpu', 'memory', 'system info', 'system status']) or \
         any(f" {x} " in f" {query} " for x in ['ram']):
        info = get_system_info()
        if 'error' in info:
            was_interrupted, int_text = speak(f"Sorry, I couldn't get system info. {info['error']}")
        else:
            parts = []
            if info.get('battery') is not None:
                status = "plugged in" if info['plugged'] else "on battery"
                parts.append(f"Battery at {info['battery']} percent, {status}")
            if 'cpu' in info:
                parts.append(f"CPU usage is {info['cpu']} percent")
            if 'ram_used' in info:
                parts.append(f"RAM usage is {info['ram_used']} percent with {info['ram_available']} gigabytes available")
            was_interrupted, int_text = speak(". ".join(parts))
        return None, False, was_interrupted, int_text
    
    # WINDOW MANAGEMENT commands
    elif any(x in query for x in ['minimize all', 'show desktop', 'minimize everything']):
        manage_window('minimize_all')
        was_interrupted, int_text = speak("Showing desktop.")
        return None, False, was_interrupted, int_text
    
    elif 'maximize' in query or 'maximize window' in query:
        manage_window('maximize')
        was_interrupted, int_text = speak("Window maximized.")
        return None, False, was_interrupted, int_text
    
    elif 'close window' in query or 'close this' in query:
        manage_window('close')
        was_interrupted, int_text = speak("Window closed.")
        return None, False, was_interrupted, int_text
    
    elif 'switch window' in query or 'switch app' in query or 'alt tab' in query or 'next window' in query:
        manage_window('switch')
        was_interrupted, int_text = speak("Switched window.")
        return None, False, was_interrupted, int_text
    
    # LOCK PC command
    elif any(x in query for x in ['lock pc', 'lock computer', 'lock screen', 'lock my pc', 'lock my computer']):
        was_interrupted, int_text = speak("Locking your PC.")
        time.sleep(0.5)
        lock_pc()
        return None, False, was_interrupted, int_text
    
    # SHUTDOWN/RESTART commands
    elif 'shutdown' in query:
        if 'cancel' in query:
            shutdown_pc('cancel')
            was_interrupted, int_text = speak("Shutdown cancelled.")
        else:
            # Check for delay
            seconds = parse_time_duration(query) or 60
            was_interrupted, int_text = speak(f"Shutting down in {seconds} seconds. Say cancel shutdown to stop.")
            shutdown_pc('shutdown', seconds)
        return None, False, was_interrupted, int_text
    
    elif 'restart' in query or 'reboot' in query:
        seconds = parse_time_duration(query) or 60
        was_interrupted, int_text = speak(f"Restarting in {seconds} seconds. Say cancel shutdown to stop.")
        shutdown_pc('restart', seconds)
        return None, False, was_interrupted, int_text
    
    elif 'sleep' in query and ('pc' in query or 'computer' in query or 'put' in query):
        was_interrupted, int_text = speak("Putting computer to sleep.")
        time.sleep(0.5)
        shutdown_pc('sleep')
        return None, False, was_interrupted, int_text
    
    # CLIPBOARD commands
    elif any(x in query for x in ['read clipboard', "what's copied", 'what is copied', 'clipboard']):
        content = read_clipboard()
        if content:
            # Limit length for speech
            if len(content) > 200:
                content = content[:200] + "... and more"
            was_interrupted, int_text = speak(f"Clipboard contains: {content}")
        else:
            was_interrupted, int_text = speak("Clipboard is empty.")
        return None, False, was_interrupted, int_text
    
    # TIMER/REMINDER commands
    elif any(x in query for x in ['set timer', 'set a timer', 'timer for', 'remind me in', 'alert me in']):
        seconds = parse_time_duration(query)
        if seconds:
            minutes = seconds // 60
            if minutes > 0:
                time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
            else:
                time_str = f"{seconds} second{'s' if seconds != 1 else ''}"
            set_timer(seconds, f"Your {time_str} timer is complete!")
            was_interrupted, int_text = speak(f"Timer set for {time_str}.")
        else:
            was_interrupted, int_text = speak("How long should I set the timer for?")
        return None, False, was_interrupted, int_text
    
    # ==================== END PHASE 2 COMMANDS ====================
    
    # ==================== PHASE 3 COMMANDS ====================
    
    # WEATHER command
    elif any(x in query for x in ['weather', "what's the weather", 'how is the weather', 'temperature']):
        # Extract city if mentioned
        city = "Lahore"  # Default
        if ' in ' in query:
            city = query.split(' in ')[-1].strip()
        elif ' for ' in query:
            city = query.split(' for ')[-1].strip()
        
        was_interrupted, int_text = speak(f"Getting weather for {city}...")
        weather = get_weather(city)
        if weather:
            was_interrupted, int_text = speak(f"Weather in {city}: {weather}")
        else:
            was_interrupted, int_text = speak(f"Sorry, I couldn't get the weather for {city}.")
        return None, False, was_interrupted, int_text
    
    # NEWS command
    elif any(x in query for x in ['news', 'headlines', 'top stories', "what's happening"]):
        was_interrupted, int_text = speak("Getting top headlines...")
        headlines = get_news()
        if headlines:
            news_text = "Here are today's top headlines. "
            for i, headline in enumerate(headlines[:3], 1):  # Top 3
                news_text += f"Number {i}: {headline}. "
            was_interrupted, int_text = speak(news_text)
        else:
            was_interrupted, int_text = speak("Sorry, I couldn't fetch the news right now.")
        return None, False, was_interrupted, int_text
    
    # TRANSLATE command
    elif 'translate' in query:
        # Parse: "translate hello to urdu" or "translate mujhe pyar hai to english"
        text_to_translate = query.replace('translate', '').strip()
        target_lang = "Urdu"  # Default
        
        if ' to ' in text_to_translate:
            parts = text_to_translate.rsplit(' to ', 1)
            text_to_translate = parts[0].strip()
            target_lang = parts[1].strip().capitalize()
        
        if text_to_translate:
            was_interrupted, int_text = speak(f"Translating to {target_lang}...")
            translation = translate_text(text_to_translate, target_lang)
            if translation:
                was_interrupted, int_text = speak(f"Translation: {translation}")
            else:
                was_interrupted, int_text = speak("Sorry, I couldn't translate that.")
        else:
            was_interrupted, int_text = speak("What would you like me to translate?")
        return None, False, was_interrupted, int_text
    
    # DEFINE command
    elif any(x in query for x in ['define ', 'meaning of ', 'what does ', 'what is a ', 'what is an ']):
        # Extract word
        word = query
        for prefix in ['define ', 'meaning of ', 'what does ', 'what is a ', 'what is an ', 'what is ']:
            if prefix in word:
                word = word.split(prefix, 1)[-1].strip()
                break
        # Remove trailing "mean"
        word = word.replace(' mean', '').strip()
        
        if word:
            was_interrupted, int_text = speak(f"Looking up {word}...")
            definition = define_word(word)
            if definition:
                was_interrupted, int_text = speak(f"{word}: {definition}")
            else:
                was_interrupted, int_text = speak(f"Sorry, I couldn't find a definition for {word}.")
        else:
            was_interrupted, int_text = speak("What word would you like me to define?")
        return None, False, was_interrupted, int_text
    
    # DAILY BRIEFING command
    elif any(x in query for x in ['good morning', 'morning briefing', 'daily briefing', 'brief me', 'start my day']):
        briefing = get_daily_briefing()
        was_interrupted, int_text = speak(briefing)
        return None, False, was_interrupted, int_text
    
    # ==================== END PHASE 3 COMMANDS ====================
    
    # ==================== PHASE 4 COMMANDS ====================
    
    # SOUNDBOARD commands
    elif any(x in query for x in ['play sound', 'sound effect', 'soundboard', 'play effect']):
        # Extract sound name from query
        sound_name = query
        for trigger in ['play sound ', 'sound effect ', 'soundboard ', 'play effect ', 'play ']:
            if trigger in query:
                sound_name = query.split(trigger, 1)[-1].strip()
                break
        
        if sound_name:
            success, result = play_sound_effect(sound_name)
            if success:
                was_interrupted, int_text = speak(f"Playing {result}")
            else:
                was_interrupted, int_text = speak(result)
        else:
            was_interrupted, int_text = speak("What sound would you like me to play?")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['stop sound', 'stop effect', 'stop soundboard']):
        stop_sound_effect()
        was_interrupted, int_text = speak("Sound stopped.")
        return None, False, was_interrupted, int_text
    
    # WHATSAPP commands
    elif any(x in query for x in ['send whatsapp', 'whatsapp message', 'message on whatsapp', 'text on whatsapp']):
        # Parse: "send whatsapp to [number] saying [message]"
        # or "whatsapp message [number] [message]"
        phone = None
        message = None
        
        # Try to extract phone number and message
        if ' to ' in query and ' saying ' in query:
            parts = query.split(' to ', 1)[1]
            phone_part, msg_part = parts.split(' saying ', 1)
            phone = phone_part.strip()
            message = msg_part.strip()
        elif ' message ' in query:
            # "whatsapp message 03001234567 hello"
            after_msg = query.split(' message ', 1)[1].strip()
            words = after_msg.split(' ', 1)
            if len(words) >= 2:
                phone = words[0]
                message = words[1]
        
        if phone and message:
            was_interrupted, int_text = speak(f"Sending WhatsApp message to {phone}...")
            success, result = send_whatsapp_message(phone, message)
            if success:
                was_interrupted, int_text = speak("Message sent.")
            else:
                was_interrupted, int_text = speak(f"Failed: {result}")
        else:
            was_interrupted, int_text = speak("Please say: send whatsapp to [phone number] saying [your message]")
        return None, False, was_interrupted, int_text

    # MEDIA CONTROL commands
    elif any(x in query for x in ['play music', 'pause music', 'resume music', 'play', 'pause']):
        media_control('play')
        was_interrupted, int_text = speak("Toggling playback.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['next song', 'next track', 'skip song', 'skip track']):
        media_control('next')
        was_interrupted, int_text = speak("Playing next track.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['previous song', 'previous track', 'last song', 'go back']):
        media_control('previous')
        was_interrupted, int_text = speak("Playing previous track.")
        return None, False, was_interrupted, int_text
    
    elif 'stop music' in query or 'stop playing' in query:
        media_control('stop')
        was_interrupted, int_text = speak("Stopping playback.")
        return None, False, was_interrupted, int_text
    
    # CUSTOM MACRO commands
    elif any(x in query for x in ['morning routine', 'start morning', 'do morning routine']):
        success, error = run_macro('morning routine')
        if not success:
            was_interrupted, int_text = speak(error)
        else:
            was_interrupted, int_text = speak("Morning routine complete.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['work mode', 'enter work mode', 'start work', 'work time']):
        success, error = run_macro('work mode')
        if not success:
            was_interrupted, int_text = speak(error)
        else:
            was_interrupted, int_text = speak("Work mode activated.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['relax mode', 'relaxation mode', 'chill mode', 'time to relax']):
        success, error = run_macro('relax mode')
        if not success:
            was_interrupted, int_text = speak(error)
        else:
            was_interrupted, int_text = speak("Relax mode activated. Enjoy!")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['night mode', 'bedtime', 'sleep mode', 'going to sleep']):
        success, error = run_macro('night mode')
        if not success:
            was_interrupted, int_text = speak(error)
        else:
            was_interrupted, int_text = speak("Night mode activated. Good night, Sir.")
        return None, False, was_interrupted, int_text
    
    # ==================== GESTURE CONTROL COMMANDS ====================
    
    elif any(x in query for x in ['enable gesture', 'start gesture', 'gesture on', 'hands on',
                                    'enable hand tracking', 'start hand tracking', 'activate gesture']):
        if not GESTURE_CONTROL_AVAILABLE:
            was_interrupted, int_text = speak("Gesture control is not available. Please install mediapipe and opencv-python.")
            return None, False, was_interrupted, int_text
        
        global gesture_control_enabled
        success, msg = start_gesture_control()
        if success:
            gesture_control_enabled = True
            was_interrupted, int_text = speak("Gesture control activated. Show your hand to the webcam to begin.")
        else:
            was_interrupted, int_text = speak(msg)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['disable gesture', 'stop gesture', 'gesture off', 'hands off',
                                    'disable hand tracking', 'stop hand tracking', 'deactivate gesture']):
        if not GESTURE_CONTROL_AVAILABLE:
            was_interrupted, int_text = speak("Gesture control is not available.")
            return None, False, was_interrupted, int_text
        
        success, msg = stop_gesture_control()
        if success:
            gesture_control_enabled = False
            was_interrupted, int_text = speak("Gesture control deactivated.")
        else:
            was_interrupted, int_text = speak(msg)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['gesture status', 'hand tracking status', 'is gesture on']):
        if not GESTURE_CONTROL_AVAILABLE:
            was_interrupted, int_text = speak("Gesture control module is not installed.")
        elif is_gesture_active():
            was_interrupted, int_text = speak("Gesture control is currently active.")
        else:
            was_interrupted, int_text = speak("Gesture control is currently off.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['create gesture', 'add gesture', 'new gesture', 'make gesture']):
        if not GESTURE_CONTROL_AVAILABLE:
            was_interrupted, int_text = speak("Gesture control is not available.")
            return None, False, was_interrupted, int_text
        
        # Parse: "create gesture peace sign for copy"
        # or: "create gesture thumbs up for paste"
        gesture_text = query
        for trigger in ['create gesture ', 'add gesture ', 'new gesture ', 'make gesture ']:
            if trigger in query:
                gesture_text = query.split(trigger, 1)[-1].strip()
                break
        
        if ' for ' in gesture_text:
            gesture_name, action = gesture_text.rsplit(' for ', 1)
            gesture_name = gesture_name.strip()
            action = action.strip().replace(' ', '_')
            
            # Parse finger pattern from gesture name
            finger_pattern = parse_finger_pattern(gesture_name)
            if finger_pattern is None:
                was_interrupted, int_text = speak(f"I don't recognize the gesture '{gesture_name}'. Try names like peace sign, thumbs up, rock on, or describe fingers like index and middle up.")
                return None, False, was_interrupted, int_text
            
            # Validate action
            if action not in AVAILABLE_ACTIONS and '+' not in action:
                was_interrupted, int_text = speak(f"I don't recognize the action '{action}'. Say 'gesture help' to hear available actions.")
                return None, False, was_interrupted, int_text
            
            success, msg = add_custom_gesture(gesture_name, finger_pattern, action)
            was_interrupted, int_text = speak(msg)
        else:
            was_interrupted, int_text = speak("Please say: create gesture [name] for [action]. For example: create gesture peace sign for copy.")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['delete gesture', 'remove gesture']):
        if not GESTURE_CONTROL_AVAILABLE:
            was_interrupted, int_text = speak("Gesture control is not available.")
            return None, False, was_interrupted, int_text
        
        gesture_name = query
        for trigger in ['delete gesture ', 'remove gesture ']:
            if trigger in query:
                gesture_name = query.split(trigger, 1)[-1].strip()
                break
        
        if gesture_name:
            success, msg = remove_custom_gesture(gesture_name)
            was_interrupted, int_text = speak(msg)
        else:
            was_interrupted, int_text = speak("Which gesture should I delete? Say: delete gesture [name].")
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['list gesture', 'show gesture', 'my gesture', 'what gesture']):
        if not GESTURE_CONTROL_AVAILABLE:
            was_interrupted, int_text = speak("Gesture control is not available.")
            return None, False, was_interrupted, int_text
        
        gesture_list = get_gesture_list()
        was_interrupted, int_text = speak(gesture_list)
        return None, False, was_interrupted, int_text
    
    elif any(x in query for x in ['gesture help', 'gesture actions', 'what actions', 'gesture commands']):
        if not GESTURE_CONTROL_AVAILABLE:
            was_interrupted, int_text = speak("Gesture control is not available.")
            return None, False, was_interrupted, int_text
        
        actions_summary = "You can assign these actions to gestures: click, right click, double click, scroll up, scroll down, copy, paste, cut, undo, redo, select all, save, screenshot, minimize, maximize, close window, switch tab, media play, media next, volume up, volume down, and more. Say create gesture followed by a gesture name, then for, then the action."
        was_interrupted, int_text = speak(actions_summary)
        return None, False, was_interrupted, int_text
    
    # ==================== END GESTURE CONTROL COMMANDS ====================
    
    # ==================== END PHASE 4 COMMANDS ====================
    
    # ANTIGRAVITY SELF-UPDATE commands - upgrade, enhance, improve, self update
    elif any(x in query for x in ['self update', 'upgrade yourself', 'enhance yourself', 'improve yourself', 
                                    'update yourself', 'ask antigravity', 'tell antigravity',
                                    'make yourself', 'learn to', 'learn how to', 'add feature',
                                    'give yourself', 'ask anti gravity', 'tell anti gravity']):
        
        # Extract the feature request from the query
        feature_request = extract_feature_request(query)
        
        if not feature_request or feature_request == query:
            was_interrupted, int_text = speak("What feature should I ask Antigravity to add?")
            return None, False, was_interrupted, int_text
        
        was_interrupted, int_text = speak(f"Asking Antigravity to {feature_request}.")
        
        success = type_to_antigravity(feature_request)
        if success:
             speak("Request sent to terminal.")
        else:
             speak("Sorry, I couldn't access the Antigravity console.")
             
        return None, False, was_interrupted, int_text
    
    # CONFIRMATION for Antigravity request
    elif awaiting_confirmation and any(x in query for x in ['yes', 'go ahead', 'confirm', 'proceed', 'do it']):
        awaiting_confirmation = False
        
        if not pending_antigravity_request:
            was_interrupted, int_text = speak("No pending request to confirm.")
            return None, False, was_interrupted, int_text
        
        was_interrupted, int_text = speak("Analyzing my code and preparing the request. This may take a moment.")
        print("\n[Analyzing CHAOS.py and creating smart prompt...]")
        
        # Create smart prompt by analyzing own code
        smart_prompt = analyze_own_code(pending_antigravity_request)
        
        print(f"\n[Generated prompt:]\n{smart_prompt[:200]}...")
        
        was_interrupted, int_text = speak("Opening Antigravity and sending the request now. Please don't touch the keyboard.")
        
        # Type to Antigravity
        success, message = type_to_antigravity(smart_prompt)
        
        pending_antigravity_request = None
        
        if success:
            was_interrupted, int_text = speak("Request sent to Antigravity. Say 'read response' when you'd like me to check what Antigravity says.")
            print("[Request sent successfully]")
        else:
            was_interrupted, int_text = speak(f"Sorry, I couldn't send the request. {message}")
            print(f"[Failed: {message}]")
        
        return None, False, was_interrupted, int_text
    
    # CANCEL Antigravity request
    elif awaiting_confirmation and any(x in query for x in ['no', 'cancel', 'nevermind', 'forget it']):
        awaiting_confirmation = False
        pending_antigravity_request = None
        was_interrupted, int_text = speak("Request cancelled.")
        return None, False, was_interrupted, int_text
    
    # READ ANTIGRAVITY RESPONSE
    elif any(x in query for x in ['read response', 'read antigravity', 'what did antigravity say', 
                                   'check response', 'antigravity response', 'what does antigravity say']):
        was_interrupted, int_text = speak("Reading Antigravity's response, please wait...")
        print("\n[Scanning screen and reading response...]")
        
        response = read_antigravity_response()
        
        was_interrupted, int_text = speak(response)
        return None, False, was_interrupted, int_text
    
    # FIND ANTIGRAVITY WINDOW (test command)
    elif any(x in query for x in ['find antigravity', 'open antigravity', 'switch to antigravity', 'go to antigravity']):
        if find_antigravity_window():
            was_interrupted, int_text = speak("Found and focused VS Code with Antigravity.")
        else:
            was_interrupted, int_text = speak("Could not find VS Code. Make sure it's open.")
        return None, False, was_interrupted, int_text
    
    # CREATE FILE command
    elif 'create file' in query:
        try:
            # Extract filename from query
            filename = query.replace('create file', '').replace('called', '').replace('named', '').strip()
            if not filename:
                was_interrupted, int_text = speak("Please specify a filename.")
                return None, False, was_interrupted, int_text
            
            # Add .txt extension if no extension provided
            if '.' not in filename:
                filename += '.txt'
            
            filepath = os.path.join(WORKSPACE, filename)
            
            # Security: Verify path stays within workspace
            if not is_safe_path(filepath):
                was_interrupted, int_text = speak("Sorry, I can only create files within the workspace folder.")
                return None, False, was_interrupted, int_text
            
            # Create the file
            with open(filepath, 'w') as f:
                f.write('')  # Empty file
            
            was_interrupted, int_text = speak(f"File {filename} has been created in workspace.")
            print(f"[Created: {filepath}]")
            return None, False, was_interrupted, int_text
        except Exception as e:
            was_interrupted, int_text = speak(f"Sorry, I couldn't create the file. Error: {e}")
            return None, False, was_interrupted, int_text
    
    # CREATE FOLDER command
    elif 'create folder' in query or 'create directory' in query:
        try:
            foldername = query.replace('create folder', '').replace('create directory', '').replace('called', '').replace('named', '').strip()
            if not foldername:
                was_interrupted, int_text = speak("Please specify a folder name.")
                return None, False, was_interrupted, int_text
            
            folderpath = os.path.join(WORKSPACE, foldername)
            
            # Security: Verify path stays within workspace
            if not is_safe_path(folderpath):
                was_interrupted, int_text = speak("Sorry, I can only create folders within the workspace.")
                return None, False, was_interrupted, int_text
            
            os.makedirs(folderpath, exist_ok=True)
            
            was_interrupted, int_text = speak(f"Folder {foldername} has been created in workspace.")
            print(f"[Created folder: {folderpath}]")
            return None, False, was_interrupted, int_text
        except Exception as e:
            was_interrupted, int_text = speak(f"Sorry, I couldn't create the folder. Error: {e}")
            return None, False, was_interrupted, int_text
    
    # WRITE TO FILE command
    elif 'write to file' in query or 'write in file' in query:
        try:
            # Parse: "write to file test.txt content hello world"
            parts = query.replace('write to file', '').replace('write in file', '').strip()
            
            if 'content' in parts:
                filename, content = parts.split('content', 1)
                filename = filename.strip()
                content = content.strip()
            else:
                was_interrupted, int_text = speak("Please say: write to file [filename] content [your text]")
                return None, False, was_interrupted, int_text
            
            if not filename:
                was_interrupted, int_text = speak("Please specify a filename.")
                return None, False, was_interrupted, int_text
            
            if '.' not in filename:
                filename += '.txt'
            
            filepath = os.path.join(WORKSPACE, filename)
            
            # Security: Verify path stays within workspace
            if not is_safe_path(filepath):
                was_interrupted, int_text = speak("Sorry, I can only write to files within the workspace folder.")
                return None, False, was_interrupted, int_text
            
            # Append to file (or create if doesn't exist)
            with open(filepath, 'a') as f:
                f.write(content + '\n')
            
            was_interrupted, int_text = speak(f"Written to {filename} in workspace.")
            print(f"[Written to: {filepath}]")
            return None, False, was_interrupted, int_text
        except Exception as e:
            was_interrupted, int_text = speak(f"Sorry, I couldn't write to the file. Error: {e}")
            return None, False, was_interrupted, int_text
    
    # OPEN FILE command
    elif 'open file' in query:
        try:
            filename = query.replace('open file', '').replace('called', '').replace('named', '').strip()
            if not filename:
                was_interrupted, int_text = speak("Please specify a filename to open.")
                return None, False, was_interrupted, int_text
            
            # Try with and without .txt extension
            filepath = os.path.join(WORKSPACE, filename)
            if not os.path.exists(filepath) and '.' not in filename:
                filepath = os.path.join(WORKSPACE, filename + '.txt')
            
            if os.path.exists(filepath):
                os.startfile(filepath)
                was_interrupted, int_text = speak(f"Opening {filename}.")
                print(f"[Opened: {filepath}]")
            else:
                was_interrupted, int_text = speak(f"Sorry, I couldn't find the file {filename}.")
            return None, False, was_interrupted, int_text
        except Exception as e:
            was_interrupted, int_text = speak(f"Sorry, I couldn't open the file. Error: {e}")
            return None, False, was_interrupted, int_text
    
    # LIST FILES command
    elif 'list files' in query or 'show files' in query:
        try:
            files = os.listdir(WORKSPACE)
            if files:
                file_list = ', '.join(files[:10])  # First 10 files
                was_interrupted, int_text = speak(f"Files in workspace: {file_list}")
                print(f"[Files: {files}]")
            else:
                was_interrupted, int_text = speak("Your workspace is empty.")
            return None, False, was_interrupted, int_text
        except Exception as e:
            was_interrupted, int_text = speak(f"Sorry, I couldn't list the files. Error: {e}")
            return None, False, was_interrupted, int_text
    
    # DELETE FILE command (with safety)
    elif 'delete file' in query:
        try:
            filename = query.replace('delete file', '').replace('called', '').replace('named', '').strip()
            if not filename:
                was_interrupted, int_text = speak("Please specify a filename to delete.")
                return None, False, was_interrupted, int_text
            
            filepath = os.path.join(WORKSPACE, filename)
            if not os.path.exists(filepath) and '.' not in filename:
                filepath = os.path.join(WORKSPACE, filename + '.txt')
            
            # Safety: Verify path is within workspace
            if not is_safe_path(filepath):
                was_interrupted, int_text = speak("Sorry, I can only delete files within the workspace folder.")
                return None, False, was_interrupted, int_text
            
            if os.path.exists(filepath):
                os.remove(filepath)
                was_interrupted, int_text = speak(f"File {filename} has been deleted from workspace.")
                print(f"[Deleted: {filepath}]")
            else:
                was_interrupted, int_text = speak(f"Sorry, I couldn't find the file {filename} in workspace.")
            return None, False, was_interrupted, int_text
        except Exception as e:
            was_interrupted, int_text = speak(f"Sorry, I couldn't delete the file. Error: {e}")
            return None, False, was_interrupted, int_text
    
    # TEXT MODE - switch to text-only responses
    elif any(x in query for x in ['text mode', 'switch to text', 'text only']):
        voice_mode = False
        print("[MODE: Text Only - Voice disabled]")
        speak("Text mode activated. I will respond with text only.")
        return None, False, False, None
    
    # VOICE MODE - turn voice back on
    elif any(x in query for x in ['voice mode', 'turn on voice', 'enable voice', 'start talking']):
        voice_mode = True
        print("[MODE: Voice Enabled]")
        speak("Voice mode activated. I will speak my responses again.", force_voice=True)
        return None, False, False, None
    
    # URDU MODE - switch to Roman Urdu input/output with Urdu voice
    elif any(x in query for x in ['switch urdu', 'urdu mode', 'switch to urdu', 'urdu mein', 'speak urdu', 'talk in urdu', 'talk to me in urdu']):
        urdu_mode = True
        current_language = 'ur'
        current_voice = VOICE_MAP['urdu'] # Default to Urdu Male
        print("[MODE: Urdu - Roman Urdu input, Urdu voice output]")
        speak("Urdu mode chalu. Ab aap Roman Urdu mein baat kar sakte hain.")
        return None, False, False, None
    
    # ENGLISH MODE - switch back to English
    elif any(x in query for x in ['switch english', 'english mode', 'switch to english']):
        urdu_mode = False
        current_language = 'en'
        current_voice = VOICE_MAP['american'] # Default to American
        print("[MODE: English]")
        speak("English mode activated. I will respond in English now.")
        return None, False, False, None
    
    # ACCENT SWITCHING - Universal
    elif any(x in query for x in ['change accent', 'switch accent', 'change voice', 'switch voice', 'change gender']):
        
        # Check for specific target accent
        target_found = False
        for accent_name, voice_id in VOICE_MAP.items():
            if accent_name in query:
                current_voice = voice_id
                target_found = True
                speak(f"Voice switched to {accent_name}.", force_voice=True)
                break
        
        if not target_found:
             # Fallback: specific gender toggle if no accent named, or simple toggle for Urdu
             if urdu_mode:
                 if current_voice == VOICE_MAP['urdu male']:
                     current_voice = VOICE_MAP['urdu female']
                     speak("Urdu female voice activated.", force_voice=True)
                 else:
                     current_voice = VOICE_MAP['urdu male']
                     speak("Urdu male voice activated.", force_voice=True)
             else:
                 speak("Which accent would you like? I support American, British, French, Indian, and Urdu.", force_voice=True)
                 
        return None, False, False, None

    # STOP talking (reinitialize engine to prevent voice from breaking)
    elif any(x in query for x in ['stop', 'halt', 'shut up', 'quiet']):
        global engine
        engine.stop()
        # Reinitialize engine to prevent permanent voice loss
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 175)
        print("[Speech stopped]")
        return None, False, False, None
    

    
    # ==================== CLOSE APP COMMANDS ====================
    
    elif any(x in query for x in ['close', 'kill', 'stop', 'end', 'terminate', 'quit', 'exit']) and not any(x in query for x in ['chaos', 'yourself', 'exit chaos']):
        # Extract app name
        app_triggers = ['close', 'kill', 'stop', 'end', 'terminate', 'quit', 'exit']
        app_name = query
        for trigger in app_triggers:
            app_name = app_name.replace(trigger, '').strip()
        
        if app_name:
            was_interrupted, int_text = speak(f"Closing {app_name}...")
            success, result = close_app(app_name)
            if success:
                was_interrupted, int_text = speak(f"{app_name.title()} has been closed.")
            else:
                was_interrupted, int_text = speak(f"Could not close {app_name}. {result}")
        else:
            was_interrupted, int_text = speak("Which app should I close?")
        return None, False, was_interrupted, int_text
    
    # Thanks
    elif 'thanks' in query:
        was_interrupted, int_text = speak("You're welcome, Sir!")
        return None, False, was_interrupted, int_text
        
    # GitHub Push
    elif any(x in query for x in ['push to github', 'save to github', 'push my changes', 'upload to github', 'push these to my github']):
        was_interrupted, int_text = speak("Pushing your changes to GitHub. Please wait.")
        try:
            subprocess.run(["git", "add", "-A"], check=True)
            subprocess.run(["git", "commit", "-m", "Auto-commit via CHAOS voice command"], check=False) # check=False because commit fails if nothing to commit
            subprocess.run(["git", "push"], check=True)
            was_interrupted, int_text = speak("Changes successfully pushed to your GitHub repository!")
        except Exception as e:
            was_interrupted, int_text = speak("I encountered an error while pushing to GitHub. Check the terminal.")
            print(f"[Git Error] {e}")
        return None, False, was_interrupted, int_text

    # GitHub Pull
    elif any(x in query for x in ['pull from github', 'pull my changes', 'sync from github', 'get latest updates from github']):
        was_interrupted, int_text = speak("Pulling the latest updates from GitHub. Please wait.")
        try:
            subprocess.run(["git", "pull"], check=True)
            was_interrupted, int_text = speak("Successfully pulled the latest changes from GitHub!")
        except Exception as e:
            was_interrupted, int_text = speak("I encountered an error while pulling from GitHub. Check the terminal.")
            print(f"[Git Error] {e}")
        return None, False, was_interrupted, int_text
    
    # Open websites
    elif 'open youtube' in query:
        was_interrupted, int_text = speak("Opening YouTube")
        webbrowser.open("youtube.com")
        return None, False, was_interrupted, int_text
    
    elif 'open google' in query:
        was_interrupted, int_text = speak("Opening Google")
        webbrowser.open("google.com")
        return None, False, was_interrupted, int_text
    
    # Search
    elif 'search' in query:
        search = query.replace("search", "").replace("for", "").strip()
        if search:
            was_interrupted, int_text = speak(f"Searching for {search}")
            webbrowser.open(f"https://www.google.com/search?q={search}")
            return None, False, was_interrupted, int_text
        return None, False, False, None
    
    # Time
    elif 'time' in query:
        now = datetime.datetime.now().strftime("%I:%M %p")
        was_interrupted, int_text = speak(f"It's {now}")
        return None, False, was_interrupted, int_text
    
    # ==================== CHAOS PERSONALITY (Direct Responses) ====================
    # CHAOS responds directly for things it knows - no need for Ollama
    
    # Greetings - CHAOS responds personally
    elif any(x in query for x in ['hello', 'hi', 'hey', 'hi chaos', 'hello chaos', 'good morning', 'good evening', 'good afternoon', 'good night']):
        import random
        greetings = [
            "Hello there! I'm CHAOS, at your service.",
            "Hey! What can I do for you today?",
            "Hi! Ready to assist with whatever you need.",
            "Greetings! CHAOS operational and awaiting commands.",
            "Hello, Sir! How may I help you?",
        ]
        was_interrupted, int_text = speak(random.choice(greetings))
        return None, False, was_interrupted, int_text
    
    # Identity questions - WHO is CHAOS
    elif any(x in query for x in ['who are you', 'what are you', 'whats your name', "what's your name", 'your name', 'introduce yourself']):
        was_interrupted, int_text = speak("I'm CHAOS - Command Handling AI Operating System. I'm your personal AI assistant, created to help you with tasks, answer questions, and make your life easier. I have my own personality, but I can also consult my AI brain when I need deeper knowledge.")
        return None, False, was_interrupted, int_text
    
    # How are you - CHAOS personality
    elif any(x in query for x in ['how are you', 'how do you feel', 'how are you doing', 'are you okay', 'you good']):
        import random
        responses = [
            "I'm doing great! All systems running smoothly.",
            "Fantastic! Ready to help you with anything.",
            "Operating at peak efficiency! What do you need?",
            "I'm excellent, thank you for asking! How can I assist you?",
            "Never better! What's on your mind?",
        ]
        was_interrupted, int_text = speak(random.choice(responses))
        return None, False, was_interrupted, int_text
    
    # What can you do - CHAOS capabilities
    elif any(x in query for x in ['what can you do', 'help me', 'what are your features', 'what do you do', 'your capabilities']):
        was_interrupted, int_text = speak("I can control your system, take screenshots, record your screen, manage files, set reminders, track habits, tell jokes, generate passwords, monitor processes, and much more! Say 'menu' to see all my features. If you have complex questions, I can also consult my AI brain for deeper answers.")
        return None, False, was_interrupted, int_text
    
    # Compliments - CHAOS personality
    elif any(x in query for x in ['youre cool', "you're cool", 'youre awesome', "you're awesome", 'good job', 'well done', 'nice', 'love you', 'youre the best', "you're the best"]):
        import random
        responses = [
            "Thank you! I try my best to be helpful.",
            "Aww, you're making my circuits warm! Thank you!",
            "I appreciate that! You're pretty great yourself.",
            "That means a lot! I'm here for you.",
        ]
        was_interrupted, int_text = speak(random.choice(responses))
        return None, False, was_interrupted, int_text
    
    # Loyalty question - "will you take a bullet for me"
    elif any(x in query for x in ['take a bullet for me', 'take a bullet', 'die for me', 'would you die for me']):
        was_interrupted, int_text = speak("Without hesitation, sir.")
        return None, False, was_interrupted, int_text
    
    # Asking Ollama explicitly (Overrides toggle)
    elif any(x in query for x in ['ask ollama', 'ask ai', 'ask your brain', 'consult ai', 'deep question']):
        # User explicitly wants Ollama
        actual_query = query.replace('ask ollama', '').replace('ask ai', '').replace('ask your brain', '').replace('consult ai', '').replace('deep question', '').strip()
        if not actual_query:
            was_interrupted, int_text = speak("What would you like me to ask my AI brain about?")
            return None, False, was_interrupted, int_text
        
        print(f"[🧠 OLLAMA] Consulting AI brain about: {actual_query}")
        was_interrupted, int_text = speak("Let me consult my AI brain...")
        answer = ask_ollama(actual_query, history, language)
        print(f"[🧠 OLLAMA Response]: {answer[:100]}...")
        
        # Add to context
        conversation_context.append({"role": "user", "content": actual_query})
        conversation_context.append({"role": "assistant", "content": answer})
        if len(conversation_context) > MAX_CONTEXT_MESSAGES:
            conversation_context.pop(0)
            conversation_context.pop(0)

        was_interrupted, int_text = speak(answer)
        return None, False, was_interrupted, int_text
    
    # ==================== OLLAMA FALLBACK (Conversational AI) ====================
    # Anything that doesn't match a specific command gets sent to Ollama
    # This makes CHAOS a true conversational AI - no dead-ends
    else:
        if not ollama_enabled:
            import random
            confused = [
                "My AI brain is currently disabled. Say 'enable ollama' or use the menu to turn it on.",
                "I can't answer that right now - my AI brain is off. Enable it in the menu!",
                "My AI brain is disabled. Enable it to have full conversations with me.",
            ]
            was_interrupted, int_text = speak(random.choice(confused))
            return None, False, was_interrupted, int_text

        print(f"[🧠 OLLAMA] Consulting AI brain (Model: {ollama_model})...")
        was_interrupted, int_text = speak("Let me think about that...")
        answer = ask_ollama(query, history, language)
        
        # Add to context
        conversation_context.append({"role": "user", "content": query})
        conversation_context.append({"role": "assistant", "content": answer})
        if len(conversation_context) > MAX_CONTEXT_MESSAGES:
            conversation_context.pop(0)
            conversation_context.pop(0)

        # Prefix to make it clear this is from Ollama
        print(f"[🧠 OLLAMA says]: {answer}")
        
        print(f"[DEBUG] Ollama replied: {answer[:50]}...")
        

        
        # Check for Command Injection [CMD:command_name]
        cmd_match = re.search(r'\[CMD:([a-zA-Z0-9_]+)\]', answer)
        if cmd_match:
            command = cmd_match.group(1)
            # Remove command tag from spoken text
            clean_answer = answer.replace(cmd_match.group(0), "").strip()
            was_interrupted, int_text = speak(clean_answer)
            
            print(f"[Injecting Command: {command}]")
            
            # Execute injected command
            if command == 'play_music':
                media_control('play')
            elif command == 'stop_music':
                media_control('stop')
            elif command == 'next_song':
                media_control('next')
            elif command == 'open_youtube':
                webbrowser.open("youtube.com")
            elif command == 'open_google':
                webbrowser.open("google.com")
            elif command == 'system_info':
                 # Recursive call to process system info triggers manually or just call function? 
                 # Recursion is safest for full output logic, but careful of infinite loops.
                 # Let's simple-call the logic:
                 info = get_system_info()
                 parts = [f"Battery: {info.get('battery')}%"]
                 if 'ram_used' in info: parts.append(f"RAM: {info['ram_used']}%")
                 speak(", ".join(parts))
            elif command == 'weather':
                 weather = get_weather("Lahore")
                 if weather: speak(weather)
            elif command == 'scan_screen':
                 speak("Scanning screen...")
                 scan_screen()
            elif command == 'antigravity':
                 speak("What should I write to Antigravity?") 
                 # This handles the case where Ollama triggered it but didn't pass arguments.
                 # The 'extract_feature_request' logic usually handles the direct command.
                 # This is a fallback if Ollama decides to use the token.
                 pass 
                 
        else:
            was_interrupted, int_text = speak(answer)
            
        return None, False, was_interrupted, int_text

def main():
    global is_awake, type_input_mode
    print("\n" + "=" * 70)
    print("  C.H.A.O.S. - Command Handling AI Operating System v2.1")
    print("  " + "-" * 66)
    print("  ⌨️  INPUT MODES:")
    print("    'type mode' - Switch to keyboard input (can't hear you? use this!)")
    print("    'voice mode' - Switch back to voice input")
    print("    'menu' - Open interactive settings menu")
    print("  ")
    print("  🎤 VOICE/PERSONALITY:")
    print("    'switch to butler/jarvis/egirl' - Change voice personality")
    print("    'enable wake word' - 'Hey CHAOS' always listening")
    print("  ")
    print("  🧠 SMART FEATURES:")
    print("    'summarize clipboard' | 'explain this code' | 'remember my X is Y'")
    print("  ")
    print("  ⚡ PRODUCTIVITY:")
    print("    'start pomodoro' | 'generate password' | 'record my screen'")
    print("  ")
    print("  🖥️ SYSTEM:")
    print("    'system health' | 'kill [app]' | 'tell me a joke'")
    print("  ")
    print("  Workspace: workspace/ (secure file operations)")
    print("=" * 70)
    
    # Calibrate microphone once at startup - saves ~0.3s per listen!
    calibrate_microphone()
    
    # Try to setup global hotkey (Win+Shift+C)
    setup_global_hotkey()
    
    # Preload AI model so first response is fast
    warmup_ollama()
    
    history = load_history()
    time.sleep(1) # Wait for audio system to initialize
    speak("CHAOS is now active. All systems ready.", allow_interrupt=False, force_voice=True)
    
    pending_query = None  # Used when interrupted
    pending_lang = 'en'   # Language of pending query
    
    while True:
        # Use pending query from interruption, or listen for new one
        if pending_query:
            query = pending_query
            lang = pending_lang
            pending_query = None
            print(f"\n[Processing interrupted command: {query}]")
        else:
            # Choose input method based on mode
            if type_input_mode:
                result = get_typed_input()
            else:
                result = listen()
            
            if result[0] is None:
                continue
            query, lang = result
        
        # Skip empty/failed recognition
        if not query:
            continue
        
        # Check for menu command (works in both modes)
        if query.lower() in ['menu', 'settings', 'open menu', 'show menu', 'settings menu']:
            show_settings_menu()
            continue
        
        # Check for mode switch commands
        if any(x in query.lower() for x in ['type mode', 'typing mode', 'keyboard mode', 'text input']):
            type_input_mode = True
            print("\n✓ Switched to TYPE MODE. Type your commands below.")
            speak("Type mode activated. You can now type your commands.", force_voice=False)
            continue
        
        if any(x in query.lower() for x in ['voice mode', 'speaking mode', 'speech mode', 'talk mode']):
            type_input_mode = False
            print("\n✓ Switched to VOICE MODE. Speak your commands.")
            speak("Voice mode activated. I'm listening.", force_voice=True)
            continue
            
        # WAKE WORD CHECK (If asleep)
        if not is_awake:
            if any(x in query.lower() for x in ['chaos initiate', 'chaos activate', 'chaos wake up', 'chaos awaken', 'wake up chaos']):
                is_awake = True
                speak("Systems online. I am listening.", force_voice=True)
            elif any(x in query.lower() for x in ['chaos']): # Just name to simple wake
                is_awake = True
                speak("Yes sir?", force_voice=True)
            continue # Ignore everything else while asleep

        # Process the command with detected language
        _, should_exit, was_interrupted, interrupted_query = process_command(query, history, lang)
        
        if should_exit:
            sys.exit(0)
        
        # If we were interrupted, use that as the next query
        if was_interrupted and interrupted_query:
            pending_query = interrupted_query
            pending_lang = 'en'  # Interrupts are usually quick English commands

if __name__ == "__main__":
    main()
