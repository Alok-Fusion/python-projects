import time
from collections import deque

import cv2
import mediapipe as mp
import numpy as np
import pytesseract

# Ensure Tesseract Path (Update if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Create a black canvas
canvas = np.zeros((480, 640, 3), dtype=np.uint8)

# Variables for tracking movements
prev_x, prev_y = None, None
drawing = False
draw_buffer = deque(maxlen=10)  # Buffer to smooth drawing
clear_motion_buffer = deque(maxlen=20)  # Store hand positions for clearing
erase_mode = False
last_clear_time = time.time()
break_point = False  # Allow writing with clear separation

# Open Camera
cap = cv2.VideoCapture(0)

def recognize_drawing(image):
    """Recognize numbers or letters drawn on the canvas."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # Reduce noise
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)
    text = pytesseract.image_to_string(thresh, config='--psm 10')  # Read single character
    return text.strip()

def count_fingers(hand_landmarks):
    """Count the number of extended fingers."""
    tips = [8, 12, 16, 20]  # Index, Middle, Ring, Pinky Finger Tips
    count = 0
    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1
    return count

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger tip coordinates
            index_finger = hand_landmarks.landmark[8]
            x, y = int(index_finger.x * 640), int(index_finger.y * 480)
            clear_motion_buffer.append((x, y))

            # Writing Mode (Index Finger Down)
            if index_finger.y < hand_landmarks.landmark[6].y and not break_point:
                draw_buffer.append((x, y))
                if len(draw_buffer) > 1:
                    for i in range(len(draw_buffer) - 1):
                        cv2.line(canvas, draw_buffer[i], draw_buffer[i + 1], (255, 255, 255), 5)
                prev_x, prev_y = x, y
                drawing = True
            else:
                draw_buffer.clear()
                prev_x, prev_y = None, None  # Stop drawing

            # Set breakpoint when hand moves away
            if index_finger.y > hand_landmarks.landmark[6].y:
                break_point = True  # Pause writing until finger is back
            else:
                break_point = False

            # Count fingers
            finger_count = count_fingers(hand_landmarks)

            # Clear screen if full hand is open and waved
            if finger_count == 5 and time.time() - last_clear_time > 1.5:
                motion_variation = np.std(clear_motion_buffer, axis=0).sum()
                if motion_variation > 50:  # Ensure actual movement before clearing
                    canvas[:] = 0
                    last_clear_time = time.time()
                    print("Screen Cleared!")

            # Detect fist gesture for recognition
            thumb_tip = hand_landmarks.landmark[4]
            pinky_tip = hand_landmarks.landmark[20]
            if abs(thumb_tip.x - pinky_tip.x) < 0.05 and abs(thumb_tip.y - pinky_tip.y) < 0.05:
                recognized_text = recognize_drawing(canvas)
                print(f"Recognized: {recognized_text}")
                canvas[:] = 0

    # Merge frame and canvas
    blended = cv2.addWeighted(frame, 0.7, canvas, 0.3, 0)
    cv2.putText(blended, "Press 'C' to Clear", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.imshow("Finger Drawing & Recognition", blended)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas[:] = 0  # Clear screen manually

cap.release()
cv2.destroyAllWindows()
