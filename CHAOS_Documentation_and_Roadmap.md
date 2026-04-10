# C.H.A.O.S - Documentation & Roadmap

## 1. Capabilities (What CHAOS can do)
- **Core interaction**: Operates via Voice & Type mode. Uses a Wake-Word system to passively listen.
- **Multiple Personalities**: Switches between different preset personas dynamically (Jarvis, Friday, E-girl, Professional, Urdu mode, etc.) using diverse voice synthesis profiles.
- **AI Brain**: Directly integrated with local LLMs (Ollama) for reasoning, summarization, complex Q&A, and coding assistance without external servers.
- **Media & App Handling**: Voice controls for media (Spotify, YouTube, skip, pause) and launching/forcefully killing active applications.
- **System Utilities**: Checks Battery, RAM, and CPU health, performs internet speed testing, clears temporary files, empties the recycle bin, and toggles OS dark/light mode.
- **Smart Vision (True Sight & Screen Watcher)**: Takes screenshots and reads them using multimodal models (`llava`). A background thread periodically monitors your screen to proactively notify you about coding errors or UI issues.
- **Context-Aware Memory**: Understands context in conversation (resolves pronouns like "he" or "this code") and has a short-term key-value memory system for saving facts.
- **Productivity & Reminders**: Features a Pomodoro timer, task/todo lists, a habit tracker, clipboard analysis (summarize/translate), and screen recording.
- **Self-Editing Codebase**: Interfaces with the Antigravity assistant developer tool to write/deploy fixes to its own Python codebase (e.g., issuing commands to modify code).
- **Gesture Control**: Real-time hand tracking via webcam using MediaPipe. Control mouse movement, clicks, scroll, and drag with hand gestures. Supports creating custom gestures mapped to 30+ actions (copy, paste, screenshot, media control, etc.). Gestures are persisted to JSON.

## 2. Libraries & Technologies Used
CHAOS utilizes several Python libraries to achieve these features:
- **Audio & TTS**: `pyttsx3`, `edge-tts` (high quality neural voices), `SpeechRecognition` (Google API speech-to-text), `pygame` (audio playback of generated voice), `pycaw.pycaw` & `comtypes` (Windows Volume Control), `pyaudio` (for interrupt/voice detection).
- **Vision & GUI Automation**: `pyautogui` (mouse/keyboard automation and screenshots), `PIL` (Image processing), `pygetwindow` (window management).
- **Gesture Control**: `mediapipe` (real-time hand landmark detection), `opencv-python` (webcam capture & display), `numpy` (coordinate math & smoothing).
- **Networking & Content**: `requests` (API calls to Ollama), `asyncio`, `webbrowser`, `base64` & `json`.
- **System Internals**: `os`, `sys`, `time`, `threading`, `subprocess` (shell commands), `hashlib`, `tempfile`, `ctypes`.
- **Background Processes**: `pystray` (used in the related launcher script for the system tray).

## 3. Resources Utilized
- **Processing Power**: High reliance on the local CPU and GPU to infer Ollama's `llama3.2` and `llava` models instantly.
- **Memory (RAM)**: Running local LLMs natively consumes significant gigabytes of RAM.
- **Hardware Peripherals**: Active Microphone arrays (background listening), audio output (speakers), GPU screen buffers for reading the active display, and webcam (for gesture control hand tracking).
- **Storage**: Small JSON footprints for `conversation_history.json` and temporary audio processing files.
- **Network**: Internet access is necessary for `edge-tts` (Microsoft voice endpoints) and speech-to-text processing (Google API).

## 4. How CHAOS Works (Architecture)
1. **Input Loop**: A listener loop uses `SpeechRecognition` and `pyaudio` to convert speech into text strings, rejecting noise using ambient calibration. 
2. **Command Gateway**: Quick keyword or regex checks intercept standard system commands (e.g., "play music", "system health") and trigger immediate Python subprocess or API actions, bypassing the heavy LLM to save time.
3. **AI Routing**: If a query is conversational or complex, it is packaged with previous conversation history and a system prompt (establishing the current Persona/Language). This is sent via API POST request to the local `localhost:11434` Ollama instance.
4. **Execution & Vision Layer**:
   - Background threads (like the "Screen Watcher") continuously hash scaled-down screenshots to detect UI changes. If changes are detected, it captures a Base64 encoded screenshot and pushes it to `llava` for anomaly detection (coding errors).
5. **Output Delivery**: Text responses are synthesized natively via `edge-tts` into temporary `.mp3` files and played asynchronously via `pygame.mixer`. An overlapping thread monitors RMS volume levels on the mic allowing you to physically talk over CHAOS and interrupt its speech.

---

## 5. Roadmap: Turning CHAOS into a Kernel-Level OS Assistant
Currently, CHAOS is a purely user-space application running top-side of the Windows GUI. To transform CHAOS into an OS-level orchestrator or operate as the Operating System itself, a completely different architectural direction is necessary. Here is the roadmap for how to scale into that format:

### Phase 1: Deep OS Integration (User Space & System Control)
- [x] Basic process lifecycle execution (via `subprocess` and `pyautogui`).
- [x] Basic hardware resource monitoring (CPU/RAM).
- [x] Context-aware AI integration via local LLM.
- [x] Background looping and system tray presence.
- [ ] **Run as a Windows Service (Session 0)**: Launch CHAOS invisibly before login screens, maintaining the state across all profiles, running with `SYSTEM` privileges instead of Admin privileges.
- [ ] **Custom Desktop Shell**: Replace `explorer.exe` entirely in the Windows Registry so CHAOS boots as the primary Desktop Environment (UI), managing all window placements natively via Python/C integration rather than simulating mouse clicks.
- [ ] **Native API Hooks**: Move away from brittle screen-scraping/mouse-automating and hook directly into Win32 APIs (e.g., `SetWindowsHookEx` via C++ bindings) to globally intercept all keyboard and mouse IO accurately.

### Phase 2: Driver & Kernel Modules (Ring 0 / Ring 1)
- [ ] **File System Mini-Filter Driver**: Intercept read/write requests directly at the kernel storage level. This allows CHAOS to auto-index everything instantly and enforce AI-driven security/malware controls beneath the OS.
- [ ] **NDIS Network Filter Driver**: Allows CHAOS to monitor and modify packet networking natively, essentially acting as an AI firewall to block/allow traffic natively.
- [ ] **Kernel-mode Audio Hooker**: Intercept the microphone and OS audio output directly at the driver driver layer without relying on user-land APIs like PyAudio. This cuts latency to virtually zero and makes CHAOS "omnipresent" in audio regardless of what's happening in user space.
- [ ] **ACPI/WMI Native Control**: Implement deep ACPI communication for hardware-level control over hardware power states, fan curves, and CPU throttling.

### Phase 3: Bare Metal / Hypervisor Assistant (Ring -1)
*This is where CHAOS becomes the underlying Operating System itself.*
- [ ] **Custom POSIX OS Kernel / Linux Distro Base**: Build a minimal customized Linux initialization layer where CHAOS is PID 1 (init), natively controlling hardware without Windows overhead.
- [ ] **Type 1 Hypervisor / Custom Bootloader**: Write a bootloader that loads CHAOS *before* Windows or Linux. CHAOS then allocates CPU cores and memory to the target OS, effectively acting as an overarching hypervisor that supervises virtualized OS instances while maintaining supreme control over the bare metal hardware.
