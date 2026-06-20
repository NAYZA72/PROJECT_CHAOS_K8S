<p align="center">
  <img src="chaos.jpg" alt="CHAOS Logo" width="200">
</p>

<h1 align="center">C.H.A.O.S.</h1>
<h3 align="center">Command Handling AI Operating System</h3>

<p align="center">
  A voice-controlled AI desktop assistant built in Python — think JARVIS, but yours.
</p>

---

## ⚡ What is CHAOS?

CHAOS is a fully local, voice-controlled AI assistant for Windows that can:

- 🎤 **Listen & Talk** — Voice commands with 40+ neural voice personalities (British butler, JARVIS, e-girl, Urdu, and more)
- 🧠 **Think** — Integrated with local LLMs via [Ollama](https://ollama.ai) (llama3.2 + llava vision) — no cloud, no API keys
- 👁️ **See** — Takes screenshots, reads your screen, and proactively alerts you about coding errors
- 🖐️ **Gesture Control** — Hand tracking via webcam for mouse control, clicks, scroll, and custom gesture creation
- 🖥️ **Control Your PC** — Launch/kill apps, media controls, system health, dark mode, volume, and more
- 📋 **Productivity** — Pomodoro timer, todo lists, habit tracker, clipboard analysis, screen recording
- 🗂️ **File Management** — Create, read, write, delete files via voice in a secure workspace
- 🔧 **Self-Editing** — Can request code changes to its own codebase through Antigravity

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **Windows 10/11**
- **[Ollama](https://ollama.ai)** installed and running with `llama3.2` model pulled
- **Microphone** (for voice control)
- **Webcam** (optional, for gesture control)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/PROJECT-CHAOS.git
cd PROJECT-CHAOS

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull Ollama models
ollama pull llama3.2
ollama pull llava        # Optional: for vision/screen reading

# 4. Run CHAOS
python CHAOS.py
```

### Build the Launcher (Optional)

The system tray launcher can be built as a standalone `.exe`:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the launcher exe
pyinstaller --onefile --noconsole --icon=chaos_new.ico ^
  --add-data "chaos_new.ico;." ^
  --add-data "chaos_icon_new.jpg;." ^
  --add-data "chaos.jpg;." ^
  --name CHAOS_Launcher launcher.py
```

The exe will be in the `dist/` folder.

## 🎤 Voice Commands

| Category | Commands |
|---|---|
| **Modes** | `type mode`, `voice mode`, `urdu mode`, `english mode` |
| **Voice** | `switch to butler/jarvis/egirl`, `change accent british` |
| **Vision** | `scan my screen`, `true sight`, `enable screen watcher` |
| **Gesture** | `enable gesture control`, `create gesture peace sign for copy`, `list gestures` |
| **Media** | `play music`, `next song`, `volume up`, `mute` |
| **System** | `system health`, `battery status`, `speed test`, `dark mode` |
| **Apps** | `open youtube`, `open spotify`, `kill chrome` |
| **Productivity** | `start pomodoro`, `add task`, `track habit`, `record screen` |
| **Files** | `create file notes.txt`, `write to file`, `list files` |
| **AI** | `ask ollama`, `remember my name is...`, `summarize clipboard` |
| **Fun** | `tell me a joke`, `motivate me`, `flip a coin`, `roll a dice` |
| **Sleep** | `chaos sleep` / `chaos activate` |

## 🖐️ Gesture Control

Enable with voice: **"enable gesture control"** or **"hands on"**

### Built-in Gestures

| Gesture | Action |
|---|---|
| ☝️ Index finger | Move mouse cursor |
| 🤏 Index + thumb pinch | Left click |
| Middle + thumb pinch | Right click |
| Index + middle + thumb pinch | Double click |
| ✌️ Index + middle up, move hand | Scroll up/down |
| ✊ Fist | Drag |
| 🖐️ Open palm (5 fingers) | Pause/Resume gestures |

### Custom Gestures

Create your own gestures mapped to 33+ actions:

```
"Create gesture peace sign for copy"
"Create gesture thumbs up for paste"
"Create gesture rock on for screenshot"
"Delete gesture peace sign"
"List gestures"
```

Available actions: `click`, `right_click`, `copy`, `paste`, `cut`, `undo`, `redo`, `save`, `screenshot`, `minimize`, `maximize`, `close_window`, `switch_tab`, `media_play`, `volume_up`, and more.

## 🏗️ Architecture

```
CHAOS.py              → Main brain (voice loop, command processing, Ollama integration)
gesture_control.py    → Hand tracking engine + custom gesture system
launcher.py           → System tray launcher
antigravity_helpers.py → Self-editing code helpers
```

### How It Works

1. **Input Loop** — Listens via microphone (SpeechRecognition) or keyboard
2. **Command Gateway** — Fast keyword matching for system commands (bypasses LLM)
3. **AI Routing** — Complex questions go to Ollama with conversation context
4. **Vision Layer** — Background screen monitoring via llava multimodal model
5. **Output** — Neural voice synthesis via Edge TTS, played through pygame

## 📦 Tech Stack

| Category | Libraries |
|---|---|
| Audio & TTS | `pyttsx3`, `edge-tts`, `SpeechRecognition`, `pygame`, `pycaw`, `pyaudio` |
| Vision & Automation | `pyautogui`, `Pillow`, `pygetwindow` |
| Gesture Control | `mediapipe`, `opencv-python`, `numpy` |
| AI | Ollama (`llama3.2`, `llava`) via REST API |
| System | `psutil`, `subprocess`, `ctypes`, `pystray` |

## 📄 License

This project is private and for personal use.

---

<p align="center">
  <b>Built with ❤️ by Afzal Akhtar</b>
</p>

# CI-CD Trigger
