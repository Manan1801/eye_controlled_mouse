import cv2
import mediapipe as mp
import pyautogui
import time

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()  # Get screen size

while True:
    success, frame = cap.read()
    if not success:
        break

    # Flip the frame (to make it mirror-like)
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB (required by mediapipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get face landmarks
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Get the coordinates of the eyes (use specific landmarks for eye tracking)
            left_eye = face_landmarks.landmark[33]  # Example landmark for left eye
            right_eye = face_landmarks.landmark[133]  # Example landmark for right eye

            # Get the center of the eyes
            left_eye_x = int(left_eye.x * screen_width)
            left_eye_y = int(left_eye.y * screen_height)

            right_eye_x = int(right_eye.x * screen_width)
            right_eye_y = int(right_eye.y * screen_height)

            # Calculate the average position between the eyes (for smoother movement)
            mouse_x = (left_eye_x + right_eye_x) // 2
            mouse_y = (left_eye_y + right_eye_y) // 2

            # Move the mouse using pyautogui
            pyautogui.moveTo(mouse_x, mouse_y)

    # Display the frame for debugging purposes
    cv2.imshow("Eye Control", frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
