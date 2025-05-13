from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from PIL import Image
import base64
import io
import cv2
import numpy as np
import mediapipe as mp
import time
import math

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True, max_num_faces=1)
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
BLINK_THRESHOLD = 0.15
BLINK_DURATION = 0.2
COOLDOWN = 1

last_left_blink_time = 0
last_right_blink_time = 0
left_blink_start_time = None
right_blink_start_time = None

def calculate_distance(p1, p2, w, h):
    x1, y1 = int(p1.x * w), int(p1.y * h)
    x2, y2 = int(p2.x * w), int(p2.y * h)
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def get_ear(landmarks, eye_idx, w, h):
    horiz = calculate_distance(landmarks[eye_idx[0]], landmarks[eye_idx[3]], w, h)
    vert1 = calculate_distance(landmarks[eye_idx[1]], landmarks[eye_idx[5]], w, h)
    vert2 = calculate_distance(landmarks[eye_idx[2]], landmarks[eye_idx[4]], w, h)
    return (vert1 + vert2) / (2.0 * horiz)
@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")
@socketio.on('process_frame')
def process_frame(data):
    print("Processing frame...")
    global last_left_blink_time, last_right_blink_time, left_blink_start_time, right_blink_start_time

    image_b64 = data.get("image")
    if not image_b64:
        return {"error": "No image data"}
    print("Image data received")
    image_bytes = base64.b64decode(image_b64)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    action = "none"
    x, y = 0.5, 0.5

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        left_ear = get_ear(lm, LEFT_EYE_IDX, w, h)
        right_ear = get_ear(lm, RIGHT_EYE_IDX, w, h)

        cx = (lm[33].x + lm[133].x) / 2
        cy = (lm[33].y + lm[133].y) / 2
        x, y = cx, cy

        t = time.time()
        if left_ear < BLINK_THRESHOLD and right_ear > BLINK_THRESHOLD:
            if left_blink_start_time is None:
                left_blink_start_time = t
            elif t - left_blink_start_time >= BLINK_DURATION and t - last_left_blink_time > COOLDOWN:
                action = "left_click"
                last_left_blink_time = t
                left_blink_start_time = None
        else:
            left_blink_start_time = None

        if right_ear < BLINK_THRESHOLD and left_ear > BLINK_THRESHOLD:
            if right_blink_start_time is None:
                right_blink_start_time = t
            elif t - right_blink_start_time >= BLINK_DURATION and t - last_right_blink_time > COOLDOWN:
                action = "right_click"
                last_right_blink_time = t
                right_blink_start_time = None
        else:
            right_blink_start_time = None
    from datetime import datetime
    from flask import request  # assuming you're using Flask

# Inside your route or function
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_ip = request.remote_addr or 'Unknown IP'

    log_line = (
        f"[{timestamp}] IP: {client_ip}\n"
        f"X: {x}, Y: {y}\n"
        "-------------------------\n"
    )

    with open("log.txt", "a") as f:
        f.write(log_line)
    socketio.emit('response', {"x": x, "y": y, "action": action})

if __name__ == '__main__':
    socketio.run(app, port=5071, debug=True)
