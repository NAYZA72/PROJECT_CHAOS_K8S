"""
C.H.A.O.S. System Tray Launcher
Command Handling AI Operating System
Click the tray icon to start/stop CHAOS
"""

import pystray
from pystray import MenuItem as item
from PIL import Image
import subprocess
import sys
import os

import shutil

# ... imports ...

def get_python_path():
    """Find the correct Python executable, avoiding Windows Store stubs"""
    # 1. Check for specific versioned executable (known working one)
    local_app_data = os.environ.get('LOCALAPPDATA', '')
    specific_path = os.path.join(local_app_data, r"Microsoft\WindowsApps\python3.11.exe")
    if os.path.exists(specific_path):
        return specific_path
        
    # 2. Check standard aliases but try to verify they verify
    for cmd in ["python3.11", "python3", "python"]:
        path = shutil.which(cmd)
        if path:
            # If it's the generic python.exe in WindowsApps, it might be the stub.
            # Only use it if checks pass, otherwise checking others is safer.
            if "WindowsApps" in path and "python.exe" in path.lower():
                continue
            return path
            
    # 3. Fallback to specific path even if existence check failed (path issue?)
    return "python"

# Determine execution mode (frozen or script)
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    application_path = os.path.dirname(sys.executable)
    PYTHON_PATH = get_python_path()
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))
    PYTHON_PATH = sys.executable

# Path to CHAOS (main script)
CHAOS_PATH = os.path.join(application_path, "CHAOS.py")

# Global state
chaos_process = None
is_running = False

def load_icon_image():
    """Load the CHAOS tray icon, preferring .ico files and ensuring 64x64 size"""
    # Use sys._MEIPASS if available (PyInstaller onefile temp dir), otherwise application_path
    if hasattr(sys, '_MEIPASS'):
        script_dir = sys._MEIPASS
    else:
        script_dir = application_path

    # Compatibility for older Pillow versions
    if hasattr(Image, 'Resampling'):
        resample_method = Image.Resampling.LANCZOS
    else:
        resample_method = Image.LANCZOS

    # 1. Prefer .ico files for tray icons
    ico_paths = [
        os.path.join(script_dir, "chaos_new.ico"),
        os.path.join(script_dir, "chaos.ico"),
    ]
    for ico_path in ico_paths:
        if os.path.exists(ico_path):
            try:
                img = Image.open(ico_path)
                # Ensure correct size
                if img.size != (64, 64):
                    img = img.resize((64, 64), resample_method)
                return img
            except Exception:
                continue

    # 2. Fallback to other image formats
    other_paths = [
        os.path.join(script_dir, "chaos_icon_new.jpg"),
        os.path.join(script_dir, "chaos_logo.jpg"),
    ]
    for img_path in other_paths:
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                img = img.resize((64, 64), resample_method)
                return img
            except Exception:
                continue

    # 3. Final fallback: generate a simple "C" icon
    from PIL import ImageDraw, ImageFont
    size = 64
    image = Image.new('RGBA', (size, size), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse([4, 4, size - 4, size - 4], fill=(200, 50, 0), outline=(255, 100, 0))
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except Exception:
        font = ImageFont.load_default()
    text = "C"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 5
    draw.text((x, y), text, fill=(255, 255, 255), font=font)
    return image

def start_chaos(icon=None, item=None):
    """Start CHAOS process"""
    global chaos_process, is_running
    
    if is_running:
        print("[CHAOS already running]")
        return
    
    try:
        # Start CHAOS in a new console window
        # Use cmd /k to keep window open if it crashes (debugging)
        chaos_process = subprocess.Popen(
            ["cmd", "/k", PYTHON_PATH, CHAOS_PATH],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        is_running = True
        print("[CHAOS Started]")
        
        if icon:
            icon.notify("CHAOS Online", "Command Handling AI Operating System")
    except Exception as e:
        print(f"[Error starting CHAOS: {e}]")

def stop_chaos(icon=None, item=None):
    """Stop CHAOS process"""
    global chaos_process, is_running
    
    if not is_running or chaos_process is None:
        print("[CHAOS not running]")
        return
    
    try:
        chaos_process.terminate()
        chaos_process.wait(timeout=5)
    except:
        chaos_process.kill()
    
    chaos_process = None
    is_running = False
    print("[CHAOS Stopped]")
    
    if icon:
        icon.notify("CHAOS Offline", "System deactivated")

def toggle_chaos(icon, item):
    """Toggle CHAOS on/off"""
    if is_running:
        stop_chaos(icon)
    else:
        start_chaos(icon)

def get_status_text(item):
    """Get current status for menu"""
    return "● Running" if is_running else "○ Stopped"

def exit_app(icon, item):
    """Exit the launcher"""
    stop_chaos()
    icon.stop()

def on_clicked(icon, item):
    """Handle left-click on tray icon"""
    toggle_chaos(icon, item)

def setup(icon):
    """Setup callback when icon is ready"""
    icon.visible = True
    print("=" * 60)
    print("  C.H.A.O.S. - Command Handling AI Operating System")
    print("  " + "-" * 56)
    print("  Left-click: Start/Stop CHAOS")
    print("  Right-click: Menu")
    print("=" * 60)
    
    # Auto-start CHAOS
    start_chaos(icon)

def main():
    """Main launcher function"""
    # Load the icon
    image = load_icon_image()
    
    # Create menu
    menu = pystray.Menu(
        item(get_status_text, None, enabled=False),
        item('─' * 15, None, enabled=False),
        item('Start CHAOS', start_chaos),
        item('Stop CHAOS', stop_chaos),
        item('─' * 15, None, enabled=False),
        item('Exit', exit_app)
    )
    
    # Create system tray icon
    icon = pystray.Icon(
        "CHAOS",
        image,
        "C.H.A.O.S. - Command Handling AI Operating System",
        menu
    )
    
    # Set up click handler
    icon.on_activate = on_clicked
    
    # Run the icon
    icon.run(setup)

if __name__ == "__main__":
    main()
