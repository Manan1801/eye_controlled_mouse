import cv2
import mediapipe as mp
import pyautogui
import time
import subprocess

# Mediapipe face mesh setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

# Indices for eyelid landmarks
LEFT_EYE_IDX = [33, 160]    # upper, lower
RIGHT_EYE_IDX = [133, 387]  # upper, lower

# Thresholds
BLINK_THRESHOLD = 0.02
INTENTIONAL_BLINK_DURATION = 0.3  # seconds
COOLDOWN = 2  # seconds between actions

# Timing
last_left_blink_time = 0
last_right_blink_time = 0

def get_eye_ratio(landmarks, eye_idx, w, h):
    top = landmarks[eye_idx[0]]
    bottom = landmarks[eye_idx[1]]
    top_y = int(top.y * h)
    bottom_y = int(bottom.y * h)
    ratio = abs(top_y - bottom_y) / h
    return ratio

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

        # Mouse movement
        left = landmarks[33]
        right = landmarks[133]
        x = int(((left.x + right.x) / 2) * screen_width)
        y = int(((left.y + right.y) / 2) * screen_height)
        pyautogui.moveTo(x, y)

        # Blink detection
        left_ratio = get_eye_ratio(landmarks, LEFT_EYE_IDX, w, h)
        right_ratio = get_eye_ratio(landmarks, RIGHT_EYE_IDX, w, h)
        current_time = time.time()

        # Left eye intentional blink
        if left_ratio < BLINK_THRESHOLD and right_ratio > BLINK_THRESHOLD:
            if current_time - last_left_blink_time > COOLDOWN:
                print("Left blink detected - opening Chrome")
                subprocess.Popen(["open", "-a", "Google Chrome"])
                last_left_blink_time = current_time

        # Right eye intentional blink
        elif right_ratio < BLINK_THRESHOLD and left_ratio > BLINK_THRESHOLD:
            if current_time - last_right_blink_time > COOLDOWN:
                print("Right blink detected - opening Telegram")
                subprocess.Popen(["open", "-a", "Telegram"])
                last_right_blink_time = current_time

    cv2.imshow("Eye Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()