def calculate_eye_ratio(landmarks, eye_indices, height):
    """Calculate the eye aspect ratio to detect blinks."""
    top = landmarks[eye_indices[0]]
    bottom = landmarks[eye_indices[1]]
    top_y = int(top.y * height)
    bottom_y = int(bottom.y * height)
    ratio = abs(top_y - bottom_y) / height
    return ratio

def draw_eye_landmarks(frame, landmarks, eye_indices, width, height):
    """Draw circles around the eye landmarks for visualization."""
    for idx in eye_indices:
        x = int(landmarks[idx].x * width)
        y = int(landmarks[idx].y * height)
        cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)