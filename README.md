# Hand Gesture Control System

This project integrates **Arduino sensors** and **Python-based gesture recognition** to create a smart control system.  
The system detects hand gestures using **MediaPipe** and controls the PC cursor, clicks, and scrolling.  
Meanwhile, the Arduino side uses **ultrasonic and infrared sensors** with LED + buzzer indicators for proximity and obstacle detection.  

---

## Features
- **Arduino Side**
  - Ultrasonic + IR sensors for object detection
  - LED + Buzzer alerts
- **Python Side**
  - Hand gesture recognition with OpenCV + MediaPipe
  - Control mouse movement and clicks using gestures
  - Toggle gesture modes (activate/deactivate, scroll mode, show/hide landmarks)
- **Keyboard Shortcuts**
  - `F1` → Toggle gesture control  
  - `F2` → Toggle landmark visualization  
  - `F3` → Toggle scroll mode  
  - `ESC` → Exit program  

---

## Hardware Requirements
- Arduino UNO R3
- Ultrasonic Sensor (HC-SR04)
- Infrared Sensor
- LED + 4.7kΩ resistor
- Buzzer
- Jumper wires & breadboard

---

## Software Requirements
- Arduino IDE
- Python 3.8+
- Libraries:
  ```bash
  pip install opencv-python mediapipe pyautogui numpy pynput
