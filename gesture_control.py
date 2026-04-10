"""
C.H.A.O.S. Gesture Control Module
==================================
Hand tracking + gesture recognition using MediaPipe and OpenCV.
Allows mouse control, built-in gestures, and custom user-defined gestures.

Dependencies: mediapipe, opencv-python, numpy, pyautogui
"""

import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import json
import os
import time
import threading
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Callable

# ==================== CONFIGURATION ====================

# Smoothing factor for mouse movement (higher = smoother but laggier)
SMOOTHING_FACTOR = 5

# Minimum distance change to trigger mouse move (prevents micro-jitter)
MIN_MOVE_THRESHOLD = 3

# Pinch distance threshold (fingertip to thumb tip) in pixels
PINCH_THRESHOLD = 40

# Click cooldown in seconds (prevents rapid double-triggering)
CLICK_COOLDOWN = 0.4

# Scroll sensitivity (how many scroll units per gesture)
SCROLL_AMOUNT = 3

# Scroll movement threshold (minimum Y movement in pixels to trigger scroll)
SCROLL_THRESHOLD = 15

# Gesture detection confidence thresholds
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.6

# Webcam feed window name
WINDOW_NAME = "CHAOS Gesture Control"

# How small the preview window should be (fraction of webcam resolution)
PREVIEW_SCALE = 0.4

# ==================== DATA STRUCTURES ====================

# Finger tip and pip (base joint) landmark indices from MediaPipe
FINGER_TIPS = {
    'thumb': 4,
    'index': 8,
    'middle': 12,
    'ring': 16,
    'pinky': 20
}

FINGER_PIPS = {
    'thumb': 3,
    'index': 6,
    'middle': 10,
    'ring': 14,
    'pinky': 18
}

# Available actions that can be assigned to custom gestures
AVAILABLE_ACTIONS = {
    # Mouse actions
    'click': 'Left click',
    'right_click': 'Right click',
    'double_click': 'Double click',
    'scroll_up': 'Scroll up',
    'scroll_down': 'Scroll down',
    'drag': 'Toggle drag (hold/release)',

    # Keyboard shortcuts
    'copy': 'Copy (Ctrl+C)',
    'paste': 'Paste (Ctrl+V)',
    'cut': 'Cut (Ctrl+X)',
    'undo': 'Undo (Ctrl+Z)',
    'redo': 'Redo (Ctrl+Y)',
    'select_all': 'Select All (Ctrl+A)',
    'save': 'Save (Ctrl+S)',
    'find': 'Find (Ctrl+F)',

    # Window management
    'screenshot': 'Take screenshot',
    'minimize': 'Minimize window',
    'maximize': 'Maximize window',
    'close_window': 'Close window (Alt+F4)',
    'switch_tab': 'Switch window (Alt+Tab)',
    'new_tab': 'New tab (Ctrl+T)',
    'close_tab': 'Close tab (Ctrl+W)',

    # Media controls
    'media_play': 'Play/Pause media',
    'media_next': 'Next track',
    'media_prev': 'Previous track',
    'volume_up': 'Volume up',
    'volume_down': 'Volume down',
    'mute': 'Mute/Unmute',

    # Special
    'enter': 'Press Enter',
    'escape': 'Press Escape',
    'space': 'Press Space',
    'delete': 'Press Delete',
    'backspace': 'Press Backspace',
    'tab': 'Press Tab',
}


@dataclass
class CustomGesture:
    """Represents a user-defined gesture with finger states and an action."""
    name: str
    fingers: Dict[str, bool]  # {thumb: True/False, index: True/False, ...}
    action: str               # Key from AVAILABLE_ACTIONS or custom key combo
    conditions: List[str] = field(default_factory=list)  # Extra conditions (future use)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# ==================== GESTURE MANAGER (Custom Gestures) ====================

class GestureManager:
    """Manages custom gesture definitions — create, delete, save, load, match."""

    def __init__(self, gestures_file=None):
        if gestures_file is None:
            self.gestures_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "chaos_gestures.json"
            )
        else:
            self.gestures_file = gestures_file
        self.custom_gestures: List[CustomGesture] = []
        self.load_gestures()

    def create_gesture(self, name: str, fingers: Dict[str, bool], action: str,
                       conditions: List[str] = None) -> Tuple[bool, str]:
        """Create a new custom gesture. Returns (success, message)."""
        # Check for duplicate name
        for g in self.custom_gestures:
            if g.name.lower() == name.lower():
                return False, f"A gesture named '{name}' already exists."

        gesture = CustomGesture(
            name=name,
            fingers=fingers,
            action=action,
            conditions=conditions or []
        )
        self.custom_gestures.append(gesture)
        self.save_gestures()
        return True, f"Gesture '{name}' created and mapped to '{action}'."

    def delete_gesture(self, name: str) -> Tuple[bool, str]:
        """Delete a custom gesture by name. Returns (success, message)."""
        for i, g in enumerate(self.custom_gestures):
            if g.name.lower() == name.lower():
                self.custom_gestures.pop(i)
                self.save_gestures()
                return True, f"Gesture '{name}' deleted."
        return False, f"No gesture named '{name}' found."

    def list_gestures(self) -> List[Dict]:
        """Return all custom gestures as a list of dicts."""
        return [g.to_dict() for g in self.custom_gestures]

    def save_gestures(self):
        """Persist custom gestures to JSON file."""
        data = {"gestures": [g.to_dict() for g in self.custom_gestures]}
        try:
            with open(self.gestures_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[Gesture] Error saving gestures: {e}")

    def load_gestures(self):
        """Load custom gestures from JSON file."""
        if not os.path.exists(self.gestures_file):
            self.custom_gestures = []
            return
        try:
            with open(self.gestures_file, 'r') as f:
                data = json.load(f)
            self.custom_gestures = [
                CustomGesture.from_dict(g) for g in data.get("gestures", [])
            ]
            print(f"[Gesture] Loaded {len(self.custom_gestures)} custom gestures.")
        except Exception as e:
            print(f"[Gesture] Error loading gestures: {e}")
            self.custom_gestures = []

    def match_gesture(self, finger_states: Dict[str, bool]) -> Optional[CustomGesture]:
        """Check if current finger states match any custom gesture.
        Returns the matched CustomGesture or None."""
        for gesture in self.custom_gestures:
            if gesture.fingers == finger_states:
                return gesture
        return None


# ==================== ACTION EXECUTOR ====================

def execute_action(action: str):
    """Execute the action mapped to a gesture."""
    try:
        # Mouse actions
        if action == 'click':
            pyautogui.click()
        elif action == 'right_click':
            pyautogui.rightClick()
        elif action == 'double_click':
            pyautogui.doubleClick()
        elif action == 'scroll_up':
            pyautogui.scroll(SCROLL_AMOUNT)
        elif action == 'scroll_down':
            pyautogui.scroll(-SCROLL_AMOUNT)

        # Keyboard shortcuts
        elif action == 'copy':
            pyautogui.hotkey('ctrl', 'c')
        elif action == 'paste':
            pyautogui.hotkey('ctrl', 'v')
        elif action == 'cut':
            pyautogui.hotkey('ctrl', 'x')
        elif action == 'undo':
            pyautogui.hotkey('ctrl', 'z')
        elif action == 'redo':
            pyautogui.hotkey('ctrl', 'y')
        elif action == 'select_all':
            pyautogui.hotkey('ctrl', 'a')
        elif action == 'save':
            pyautogui.hotkey('ctrl', 's')
        elif action == 'find':
            pyautogui.hotkey('ctrl', 'f')

        # Window management
        elif action == 'screenshot':
            pyautogui.hotkey('win', 'shift', 's')  # Windows snipping tool
        elif action == 'minimize':
            pyautogui.hotkey('win', 'down')
        elif action == 'maximize':
            pyautogui.hotkey('win', 'up')
        elif action == 'close_window':
            pyautogui.hotkey('alt', 'F4')
        elif action == 'switch_tab':
            pyautogui.hotkey('alt', 'tab')
        elif action == 'new_tab':
            pyautogui.hotkey('ctrl', 't')
        elif action == 'close_tab':
            pyautogui.hotkey('ctrl', 'w')

        # Media controls
        elif action == 'media_play':
            pyautogui.press('playpause')
        elif action == 'media_next':
            pyautogui.press('nexttrack')
        elif action == 'media_prev':
            pyautogui.press('prevtrack')
        elif action == 'volume_up':
            pyautogui.press('volumeup')
        elif action == 'volume_down':
            pyautogui.press('volumedown')
        elif action == 'mute':
            pyautogui.press('volumemute')

        # Direct key presses
        elif action == 'enter':
            pyautogui.press('enter')
        elif action == 'escape':
            pyautogui.press('escape')
        elif action == 'space':
            pyautogui.press('space')
        elif action == 'delete':
            pyautogui.press('delete')
        elif action == 'backspace':
            pyautogui.press('backspace')
        elif action == 'tab':
            pyautogui.press('tab')

        # Custom key combo (e.g., "ctrl+shift+s")
        elif '+' in action:
            keys = [k.strip() for k in action.split('+')]
            pyautogui.hotkey(*keys)
        else:
            print(f"[Gesture] Unknown action: {action}")

    except Exception as e:
        print(f"[Gesture] Error executing action '{action}': {e}")


# ==================== GESTURE ENGINE (Core Hand Tracking) ====================

class GestureEngine:
    """Core engine: webcam capture → hand detection → gesture recognition → action."""

    def __init__(self):
        # MediaPipe setup
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )

        # Webcam
        self.cap = None

        # Screen dimensions for coordinate mapping
        self.screen_w, self.screen_h = pyautogui.size()

        # Mouse smoothing - rolling average of positions
        self.prev_x, self.prev_y = 0, 0
        self.smooth_positions = []

        # State tracking
        self.is_running = False
        self.is_paused = False  # Paused by open palm gesture
        self.is_dragging = False
        self.thread = None

        # Cooldown trackers
        self.last_click_time = 0
        self.last_action_time = 0
        self.last_scroll_y = 0
        self.last_custom_action_time = 0

        # Gesture manager for custom gestures
        self.gesture_manager = GestureManager()

        # Disable pyautogui failsafe (we handle our own safety via open palm)
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0  # No delay between pyautogui calls

    def _open_camera(self) -> bool:
        """Try to open the webcam. Returns True if successful."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[Gesture] ERROR: Could not open webcam.")
            return False
        # Set lower resolution for performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("[Gesture] Webcam opened successfully.")
        return True

    def _close_camera(self):
        """Release the webcam."""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        print("[Gesture] Webcam released.")

    def _get_finger_states(self, landmarks) -> Dict[str, bool]:
        """Determine which fingers are extended (up) based on landmarks.
        Returns dict like {'thumb': True, 'index': False, ...}"""
        states = {}

        # Thumb: compare x-position of tip vs pip (works for right hand facing camera)
        # Thumb is extended if tip is further from palm center than pip
        thumb_tip = landmarks[FINGER_TIPS['thumb']]
        thumb_pip = landmarks[FINGER_PIPS['thumb']]
        wrist = landmarks[0]

        # Determine hand orientation (left vs right) based on thumb direction
        # If wrist x < middle finger base x, it's likely a right hand (mirrored in camera)
        mid_base = landmarks[9]
        if wrist.x < mid_base.x:
            # Right hand (in camera view) - thumb extends to the left
            states['thumb'] = thumb_tip.x < thumb_pip.x
        else:
            # Left hand (in camera view) - thumb extends to the right
            states['thumb'] = thumb_tip.x > thumb_pip.x

        # Other fingers: tip is above pip means extended (y decreases upward in image)
        for finger in ['index', 'middle', 'ring', 'pinky']:
            tip = landmarks[FINGER_TIPS[finger]]
            pip = landmarks[FINGER_PIPS[finger]]
            states[finger] = tip.y < pip.y

        return states

    def _get_distance(self, landmarks, idx1: int, idx2: int, frame_w: int, frame_h: int) -> float:
        """Calculate pixel distance between two landmarks."""
        l1 = landmarks[idx1]
        l2 = landmarks[idx2]
        x1, y1 = int(l1.x * frame_w), int(l1.y * frame_h)
        x2, y2 = int(l2.x * frame_w), int(l2.y * frame_h)
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def _smooth_position(self, x: int, y: int) -> Tuple[int, int]:
        """Apply rolling average smoothing to mouse position."""
        self.smooth_positions.append((x, y))
        if len(self.smooth_positions) > SMOOTHING_FACTOR:
            self.smooth_positions.pop(0)

        avg_x = int(np.mean([p[0] for p in self.smooth_positions]))
        avg_y = int(np.mean([p[1] for p in self.smooth_positions]))
        return avg_x, avg_y

    def _map_to_screen(self, landmark, frame_w: int, frame_h: int) -> Tuple[int, int]:
        """Map a hand landmark position to screen coordinates.
        Uses a padded region of the camera frame for more comfortable pointing."""
        # Add padding so you don't need to reach the very edges of the frame
        pad_x = frame_w * 0.15
        pad_y = frame_h * 0.15

        # Normalize within the padded region
        norm_x = (landmark.x * frame_w - pad_x) / (frame_w - 2 * pad_x)
        norm_y = (landmark.y * frame_h - pad_y) / (frame_h - 2 * pad_y)

        # Clamp to [0, 1]
        norm_x = max(0.0, min(1.0, norm_x))
        norm_y = max(0.0, min(1.0, norm_y))

        # Map to screen (mirror X since webcam is mirrored)
        screen_x = int((1 - norm_x) * self.screen_w)
        screen_y = int(norm_y * self.screen_h)

        return screen_x, screen_y

    def _process_frame(self, frame):
        """Process a single frame: detect hands, recognize gestures, execute actions.
        Returns the annotated frame for display."""
        frame_h, frame_w, _ = frame.shape

        # Flip horizontally for selfie view (mirror)
        frame = cv2.flip(frame, 1)

        # Convert BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        # Status text
        status = "PAUSED" if self.is_paused else "ACTIVE"
        color = (0, 165, 255) if self.is_paused else (0, 255, 0)
        cv2.putText(frame, f"CHAOS Gesture: {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if not results.multi_hand_landmarks:
            cv2.putText(frame, "No hand detected", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
            return frame

        # Process the first detected hand
        hand_landmarks = results.multi_hand_landmarks[0]

        # Draw hand skeleton
        self.mp_draw.draw_landmarks(
            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
            self.mp_styles.get_default_hand_landmarks_style(),
            self.mp_styles.get_default_hand_connections_style()
        )

        landmarks = hand_landmarks.landmark
        finger_states = self._get_finger_states(landmarks)

        # Count extended fingers
        fingers_up = sum(1 for v in finger_states.values() if v)

        # Display finger state
        finger_str = " ".join(
            [f"{'👆' if finger_states[f] else '👇'}{f[0].upper()}" for f in
             ['thumb', 'index', 'middle', 'ring', 'pinky']]
        )
        cv2.putText(frame, finger_str, (10, frame_h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        now = time.time()

        # ========== OPEN PALM = PAUSE/RESUME TOGGLE ==========
        if fingers_up == 5:
            if now - self.last_action_time > 1.0:  # 1 second cooldown for toggle
                self.is_paused = not self.is_paused
                state = "PAUSED" if self.is_paused else "RESUMED"
                print(f"[Gesture] {state} - Open palm detected")
                self.last_action_time = now
            return frame

        # If paused, skip all gesture processing
        if self.is_paused:
            cv2.putText(frame, "Show open palm to resume", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)
            return frame

        # ========== CUSTOM GESTURE CHECK (priority over built-ins) ==========
        matched = self.gesture_manager.match_gesture(finger_states)
        if matched and now - self.last_custom_action_time > CLICK_COOLDOWN:
            execute_action(matched.action)
            self.last_custom_action_time = now
            cv2.putText(frame, f"Custom: {matched.name} -> {matched.action}",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
            return frame

        # ========== BUILT-IN GESTURES ==========

        # Get key distances for built-in gesture detection
        index_thumb_dist = self._get_distance(landmarks, 4, 8, frame_w, frame_h)
        middle_thumb_dist = self._get_distance(landmarks, 4, 12, frame_w, frame_h)

        # --- FIST = DRAG ---
        if fingers_up == 0:
            if not self.is_dragging:
                pyautogui.mouseDown()
                self.is_dragging = True
                print("[Gesture] Drag START")
            cv2.putText(frame, "DRAGGING", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            # Still track position during drag
            index_tip = landmarks[FINGER_TIPS['index']]
            sx, sy = self._map_to_screen(index_tip, frame_w, frame_h)
            sx, sy = self._smooth_position(sx, sy)
            pyautogui.moveTo(sx, sy)
            return frame
        else:
            if self.is_dragging:
                pyautogui.mouseUp()
                self.is_dragging = False
                print("[Gesture] Drag END")

        # --- INDEX ONLY = MOUSE MOVE ---
        if (finger_states['index'] and
                not finger_states['middle'] and
                not finger_states['ring'] and
                not finger_states['pinky']):

            index_tip = landmarks[FINGER_TIPS['index']]
            sx, sy = self._map_to_screen(index_tip, frame_w, frame_h)
            sx, sy = self._smooth_position(sx, sy)

            # Only move if beyond minimum threshold
            if abs(sx - self.prev_x) > MIN_MOVE_THRESHOLD or abs(sy - self.prev_y) > MIN_MOVE_THRESHOLD:
                pyautogui.moveTo(sx, sy)
                self.prev_x, self.prev_y = sx, sy

            # Check for pinch = CLICK
            if index_thumb_dist < PINCH_THRESHOLD and now - self.last_click_time > CLICK_COOLDOWN:
                pyautogui.click()
                self.last_click_time = now
                cv2.putText(frame, "CLICK!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "MOVE", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1)

            return frame

        # --- INDEX + MIDDLE = SCROLL or DOUBLE CLICK or RIGHT CLICK ---
        if (finger_states['index'] and finger_states['middle'] and
                not finger_states['ring'] and not finger_states['pinky']):

            # Both pinching thumb = DOUBLE CLICK
            if (index_thumb_dist < PINCH_THRESHOLD and
                    middle_thumb_dist < PINCH_THRESHOLD and
                    now - self.last_click_time > CLICK_COOLDOWN):
                pyautogui.doubleClick()
                self.last_click_time = now
                cv2.putText(frame, "DOUBLE CLICK!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                return frame

            # Middle pinching thumb only = RIGHT CLICK
            if (middle_thumb_dist < PINCH_THRESHOLD and
                    index_thumb_dist >= PINCH_THRESHOLD and
                    now - self.last_click_time > CLICK_COOLDOWN):
                pyautogui.rightClick()
                self.last_click_time = now
                cv2.putText(frame, "RIGHT CLICK!", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                return frame

            # Otherwise = SCROLL (based on vertical hand movement)
            index_tip = landmarks[FINGER_TIPS['index']]
            current_y = int(index_tip.y * frame_h)

            if self.last_scroll_y != 0:
                dy = self.last_scroll_y - current_y  # Positive = moved up
                if abs(dy) > SCROLL_THRESHOLD:
                    if dy > 0:
                        pyautogui.scroll(SCROLL_AMOUNT)
                        cv2.putText(frame, "SCROLL UP", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    else:
                        pyautogui.scroll(-SCROLL_AMOUNT)
                        cv2.putText(frame, "SCROLL DOWN", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    self.last_scroll_y = current_y
            else:
                self.last_scroll_y = current_y

            return frame
        else:
            self.last_scroll_y = 0  # Reset scroll tracking when not in scroll gesture

        return frame

    def _run_loop(self):
        """Main gesture processing loop. Runs in a background thread."""
        print("[Gesture] Starting gesture control loop...")

        if not self._open_camera():
            self.is_running = False
            return

        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                print("[Gesture] Failed to read frame.")
                time.sleep(0.1)
                continue

            # Process the frame
            annotated = self._process_frame(frame)

            # Show preview window (scaled down)
            preview = cv2.resize(annotated, None,
                                 fx=PREVIEW_SCALE, fy=PREVIEW_SCALE)
            cv2.imshow(WINDOW_NAME, preview)

            # Check for 'q' key to close (backup exit)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("[Gesture] 'Q' pressed — stopping.")
                self.is_running = False
                break

        # Cleanup
        if self.is_dragging:
            pyautogui.mouseUp()
            self.is_dragging = False
        self._close_camera()
        print("[Gesture] Gesture control stopped.")

    def start(self) -> Tuple[bool, str]:
        """Start gesture control in a background thread. Returns (success, message)."""
        if self.is_running:
            return False, "Gesture control is already running."

        self.is_running = True
        self.is_paused = False
        self.smooth_positions = []
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        return True, "Gesture control activated. Show your hand to begin."

    def stop(self) -> Tuple[bool, str]:
        """Stop gesture control. Returns (success, message)."""
        if not self.is_running:
            return False, "Gesture control is not running."

        self.is_running = False
        if self.thread:
            self.thread.join(timeout=3)
        return True, "Gesture control deactivated."


# ==================== GLOBAL ENGINE INSTANCE ====================

_engine: Optional[GestureEngine] = None


def _get_engine() -> GestureEngine:
    """Get or create the global gesture engine instance."""
    global _engine
    if _engine is None:
        _engine = GestureEngine()
    return _engine


# ==================== PUBLIC API (called from CHAOS.py) ====================

def start_gesture_control() -> Tuple[bool, str]:
    """Start the gesture control system. Returns (success, message)."""
    engine = _get_engine()
    return engine.start()


def stop_gesture_control() -> Tuple[bool, str]:
    """Stop the gesture control system. Returns (success, message)."""
    engine = _get_engine()
    return engine.stop()


def is_gesture_active() -> bool:
    """Check if gesture control is currently running."""
    engine = _get_engine()
    return engine.is_running


def add_custom_gesture(name: str, finger_pattern: Dict[str, bool],
                       action: str) -> Tuple[bool, str]:
    """Add a new custom gesture.
    finger_pattern: {'thumb': True/False, 'index': True/False, ...}
    action: key from AVAILABLE_ACTIONS or a custom key combo like 'ctrl+shift+s'
    Returns (success, message)."""
    engine = _get_engine()
    return engine.gesture_manager.create_gesture(name, finger_pattern, action)


def remove_custom_gesture(name: str) -> Tuple[bool, str]:
    """Remove a custom gesture by name. Returns (success, message)."""
    engine = _get_engine()
    return engine.gesture_manager.delete_gesture(name)


def get_gesture_list() -> str:
    """Get a human-readable list of all custom gestures."""
    engine = _get_engine()
    gestures = engine.gesture_manager.list_gestures()

    if not gestures:
        return "No custom gestures defined. You can create one by saying 'create gesture [name] for [action]'."

    lines = [f"You have {len(gestures)} custom gesture{'s' if len(gestures) != 1 else ''}:"]
    for g in gestures:
        fingers_desc = ", ".join(
            [f"{f} {'up' if v else 'down'}" for f, v in g['fingers'].items()]
        )
        action_desc = AVAILABLE_ACTIONS.get(g['action'], g['action'])
        lines.append(f"  • {g['name']}: {fingers_desc} → {action_desc}")

    return "\n".join(lines)


def get_available_actions() -> str:
    """Get a human-readable list of all available actions for gesture assignment."""
    lines = ["Available actions you can assign to gestures:"]
    for key, desc in AVAILABLE_ACTIONS.items():
        lines.append(f"  • {key}: {desc}")
    return "\n".join(lines)


def parse_finger_pattern(description: str) -> Optional[Dict[str, bool]]:
    """Parse a natural language finger description into a finger pattern dict.
    Examples:
      'index and middle up' → {'thumb': False, 'index': True, 'middle': True, 'ring': False, 'pinky': False}
      'peace sign' → {'thumb': False, 'index': True, 'middle': True, 'ring': False, 'pinky': False}
      'thumbs up' → {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': False}
    """
    desc = description.lower().strip()

    # Preset gesture names
    presets = {
        'peace sign': {'thumb': False, 'index': True, 'middle': True, 'ring': False, 'pinky': False},
        'peace': {'thumb': False, 'index': True, 'middle': True, 'ring': False, 'pinky': False},
        'thumbs up': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': False},
        'thumb up': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': False},
        'pointing': {'thumb': False, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'rock': {'thumb': False, 'index': True, 'middle': False, 'ring': False, 'pinky': True},
        'rock on': {'thumb': False, 'index': True, 'middle': False, 'ring': False, 'pinky': True},
        'horns': {'thumb': False, 'index': True, 'middle': False, 'ring': False, 'pinky': True},
        'ok': {'thumb': True, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'okay': {'thumb': True, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'three': {'thumb': False, 'index': True, 'middle': True, 'ring': True, 'pinky': False},
        'three fingers': {'thumb': False, 'index': True, 'middle': True, 'ring': True, 'pinky': False},
        'four': {'thumb': False, 'index': True, 'middle': True, 'ring': True, 'pinky': True},
        'four fingers': {'thumb': False, 'index': True, 'middle': True, 'ring': True, 'pinky': True},
        'shaka': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': True},
        'hang loose': {'thumb': True, 'index': False, 'middle': False, 'ring': False, 'pinky': True},
        'gun': {'thumb': True, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'finger gun': {'thumb': True, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'pinky': {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': True},
        'pinky up': {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': True},
        'l shape': {'thumb': True, 'index': True, 'middle': False, 'ring': False, 'pinky': False},
        'middle finger': {'thumb': False, 'index': False, 'middle': True, 'ring': False, 'pinky': False},
    }

    # Check presets first
    for preset_name, pattern in presets.items():
        if preset_name in desc:
            return pattern

    # Try to parse natural language like "index and middle up" or "thumb index middle up"
    # Default all fingers down
    pattern = {'thumb': False, 'index': False, 'middle': False, 'ring': False, 'pinky': False}
    found_any = False

    for finger in ['thumb', 'index', 'middle', 'ring', 'pinky']:
        if finger in desc:
            # Check if explicitly "down"
            finger_idx = desc.index(finger)
            surrounding = desc[max(0, finger_idx - 10):finger_idx + len(finger) + 10]
            if 'down' in surrounding or 'closed' in surrounding or 'curled' in surrounding:
                pattern[finger] = False
            else:
                pattern[finger] = True
            found_any = True

    if found_any:
        return pattern

    return None


# ==================== STANDALONE TEST ====================

if __name__ == "__main__":
    print("=" * 50)
    print("  CHAOS Gesture Control - Standalone Test")
    print("=" * 50)
    print("\nControls:")
    print("  Index finger  → Move mouse")
    print("  Pinch (index+thumb) → Click")
    print("  Middle+thumb pinch → Right click")
    print("  Index+middle pinch → Double click")
    print("  Index+middle up → Scroll (move hand up/down)")
    print("  Fist → Drag")
    print("  Open palm (5 fingers) → Pause/Resume")
    print("  Press 'Q' in the preview window to quit")
    print()

    success, msg = start_gesture_control()
    print(msg)

    if success:
        try:
            while is_gesture_active():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
            stop_gesture_control()
