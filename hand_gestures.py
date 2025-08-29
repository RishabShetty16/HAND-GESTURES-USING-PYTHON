import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import threading
import time
import serial
from pynput import keyboard

# Initialize Arduino serial
arduino = serial.Serial('COM5', 9600)  
time.sleep(2)  

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7
)

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
SMOOTHING = 10
prev_x, prev_y = 0, 0

# Global variables
is_active = True
show_landmarks = True
scroll_mode = False
last_click_time = 0
DOUBLE_CLICK_TIME = 0.3

def get_hand_landmarks(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    return results.multi_hand_landmarks

def calculate_distance(p1, p2):
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

def is_click_gesture(landmarks, finger1, finger2):
    return calculate_distance(landmarks[finger1], landmarks[finger2]) < 0.05

def is_hand_closed(landmarks):
    tips = [4, 8, 12, 16, 20]
    mcp = [0, 5, 9, 13, 17]
    return all(calculate_distance(landmarks[tips[i]], landmarks[mcp[i]]) < 0.07 for i in range(5))

def is_hand_open(landmarks):
    tips = [4, 8, 12, 16, 20]
    mcp = [0, 5, 9, 13, 17]
    return all(calculate_distance(landmarks[tips[i]], landmarks[mcp[i]]) > 0.15 for i in range(5))

def blink_arduino_led():
    try:
        arduino.write(b'B')  # Send blink signal
    except:
        print("Failed to send signal to Arduino")

def move_cursor(landmarks):
    global prev_x, prev_y
    index_tip = landmarks[8]
    x = int(index_tip.x * SCREEN_WIDTH)
    y = int(index_tip.y * SCREEN_HEIGHT)
    speed = ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5
    speed_factor = min(speed / 10, 5)
    smooth_x = prev_x + (x - prev_x) / SMOOTHING * speed_factor
    smooth_y = prev_y + (y - prev_y) / SMOOTHING * speed_factor
    pyautogui.moveTo(smooth_x, smooth_y)
    prev_x, prev_y = smooth_x, smooth_y

def handle_custom_scroll(landmarks):
    index_tip = landmarks[8]
    index_mcp = landmarks[5]
    index_is_up = index_tip.y < index_mcp.y
    index_is_down = index_tip.y > index_mcp.y
    other_tips = [12, 16, 20]
    all_others_closed = all(calculate_distance(landmarks[i], landmarks[0]) < 0.07 for i in other_tips)
    if all_others_closed:
        if index_is_up:
            pyautogui.scroll(200)
        elif index_is_down:
            pyautogui.scroll(-200)

def on_press(key):
    global is_active, show_landmarks, scroll_mode
    if key == keyboard.Key.f1:
        is_active = not is_active
        print(f"Gesture control {'activated' if is_active else 'deactivated'}")
    elif key == keyboard.Key.f2:
        show_landmarks = not show_landmarks
        print(f"Landmark visualization {'enabled' if show_landmarks else 'disabled'}")
    elif key == keyboard.Key.f3:
        scroll_mode = not scroll_mode
        print(f"Scroll mode {'activated' if scroll_mode else 'deactivated'}")

keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    hand_landmarks = get_hand_landmarks(frame)

    if hand_landmarks and is_active:
        for i, landmarks in enumerate(hand_landmarks):
            if show_landmarks:
                mp_drawing.draw_landmarks(frame, landmarks, mp_hands.HAND_CONNECTIONS)

            is_right_hand = landmarks.landmark[4].x < landmarks.landmark[20].x

            if is_right_hand:
                move_cursor(landmarks.landmark)

                if is_click_gesture(landmarks.landmark, 4, 8):
                    current_time = time.time()
                    blink_arduino_led()
                    if current_time - last_click_time < DOUBLE_CLICK_TIME:
                        pyautogui.doubleClick()
                        last_click_time = 0
                    else:
                        pyautogui.click()
                        last_click_time = current_time
                    time.sleep(0.2)

                elif is_click_gesture(landmarks.landmark, 4, 12):
                    pyautogui.click(button="right")
                    blink_arduino_led()
                    time.sleep(0.2)

                elif is_hand_closed(landmarks.landmark):
                    pyautogui.hotkey("win", "down")
                    blink_arduino_led()
                    time.sleep(0.5)

                elif is_hand_open(landmarks.landmark):
                    pyautogui.hotkey("win", "up")
                    blink_arduino_led()
                    time.sleep(0.5)

            else:
                if scroll_mode:
                    handle_custom_scroll(landmarks.landmark)
                    blink_arduino_led()
                elif is_hand_open(landmarks.landmark):
                    pyautogui.hotkey("ctrl", "+")
                    blink_arduino_led()
                    time.sleep(0.5)
                elif is_hand_closed(landmarks.landmark):
                    pyautogui.hotkey("ctrl", "-")
                    blink_arduino_led()
                    time.sleep(0.5)

    # UI Text
    cv2.putText(frame, f"Gesture Control: {'Active' if is_active else 'Inactive'}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if is_active else (0, 0, 255), 2)
    cv2.putText(frame, f"Landmark Visualization: {'Enabled' if show_landmarks else 'Disabled'}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if show_landmarks else (0, 0, 255), 2)
    cv2.putText(frame, f"Scroll Mode: {'Active' if scroll_mode else 'Inactive'}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0) if scroll_mode else (0, 0, 255), 2)
    cv2.putText(frame, "F1: Toggle gesture control | F2: Toggle landmarks | F3: Toggle scroll mode", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
keyboard_listener.stop()
arduino.close()
