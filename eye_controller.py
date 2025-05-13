import cv2
import mediapipe as mp
import pyautogui
import time
import subprocess
import math

# Mediapipe face mesh setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

# Indices for eye landmarks (Mediapipe Face Mesh)
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]  # [p1, p2, p3, p4, p5, p6]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]  # [p1, p2, p3, p4, p5, p6]

# Thresholds
BLINK_THRESHOLD = 0.15  # Adjusted for better detection
BLINK_DURATION = 0.2    # Minimum duration (in seconds) for a valid blink
COOLDOWN = 2            # Seconds between actions

# Timing
last_left_blink_time = 0
last_right_blink_time = 0
left_blink_start_time = None
right_blink_start_time = None

def calculate_distance(point1, point2, w, h):
    """Calculate the Euclidean distance between two points."""
    x1, y1 = int(point1.x * w), int(point1.y * h)
    x2, y2 = int(point2.x * w), int(point2.y * h)
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_eye_aspect_ratio(landmarks, eye_idx, w, h):
    """Calculate the Eye Aspect Ratio (EAR) for blink detection."""
    # Horizontal distance (p1, p4)
    horizontal_dist = calculate_distance(landmarks[eye_idx[0]], landmarks[eye_idx[3]], w, h)
    # Vertical distances (p2, p6) and (p3, p5)
    vertical_dist1 = calculate_distance(landmarks[eye_idx[1]], landmarks[eye_idx[5]], w, h)
    vertical_dist2 = calculate_distance(landmarks[eye_idx[2]], landmarks[eye_idx[4]], w, h)
    # EAR calculation
    ear = (vertical_dist1 + vertical_dist2) / (2.0 * horizontal_dist)
    return ear

def draw_eye_landmarks(frame, landmarks, eye_indices, w, h):
    """Draw circles around the eye landmarks for visualization."""
    for idx in eye_indices:
        x = int(landmarks[idx].x * w)
        y = int(landmarks[idx].y * h)
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

def open_bookmarks():
    """Simulate opening bookmarks in Chrome."""
    print("Opening bookmarks...")
    pyautogui.hotkey("command", "shift", "b")  # Shortcut to open bookmarks bar
    time.sleep(0.5)  # Wait for the bookmarks bar to appear
    pyautogui.press("tab")  # Navigate to the first bookmark
    pyautogui.press("enter")  # Open the selected bookmark

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    h, w, _ = frame.shape

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        # Draw eye landmarks for debugging
        draw_eye_landmarks(frame, landmarks, LEFT_EYE_IDX, w, h)
        draw_eye_landmarks(frame, landmarks, RIGHT_EYE_IDX, w, h)

        # Mouse movement
        left = landmarks[33]
        right = landmarks[133]
        x = int(((left.x + right.x) / 2) * screen_width)
        y = int(((left.y + right.y) / 2) * screen_height)
        pyautogui.moveTo(x, y)

        # EAR calculation
        left_ear = get_eye_aspect_ratio(landmarks, LEFT_EYE_IDX, w, h)
        right_ear = get_eye_aspect_ratio(landmarks, RIGHT_EYE_IDX, w, h)
        current_time = time.time()

        # Debugging: Display EAR values
        cv2.putText(frame, f"Left EAR: {left_ear:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(frame, f"Right EAR: {right_ear:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Detect left eye blink
        if left_ear < BLINK_THRESHOLD and right_ear > BLINK_THRESHOLD:
            if left_blink_start_time is None:
                left_blink_start_time = current_time
            elif current_time - left_blink_start_time >= BLINK_DURATION:
                if current_time - last_left_blink_time > COOLDOWN:
                    print("Left blink detected - left click")
                    pyautogui.click(button='left')  # Simulate a left click
                    last_left_blink_time = current_time
                    left_blink_start_time = None
        else:
            left_blink_start_time = None

        # Detect right eye blink
        if right_ear < BLINK_THRESHOLD and left_ear > BLINK_THRESHOLD:
            if right_blink_start_time is None:
                right_blink_start_time = current_time
            elif current_time - right_blink_start_time >= BLINK_DURATION:
                if current_time - last_right_blink_time > COOLDOWN:
                    print("Right blink detected - right click")
                    pyautogui.click(button='right')  # Simulate a right click
                    last_right_blink_time = current_time
                    right_blink_start_time = None
        else:
            right_blink_start_time = None

    cv2.imshow("Eye Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()