# Eye Blink Morse Code Translator

This project allows users to **communicate using eye blinks**. It tracks eye blinks with **MediaPipe FaceMesh** and translates blink patterns into **Morse code**, which is then converted into readable text.

## ✨ Features
- Real-time eye blink detection using **MediaPipe** and **OpenCV**
- Converts **short blinks** into dots (`.`) and **long blinks** into dashes (`-`)
- Supports **letter spacing** and **word spacing** using timed gaps
- **Long blink** can also be used as a **delete/backspace action**
- Displays Morse code sequence and translated text on screen

## ⌨️ Morse Code Rules in This Project
- **Short Blink** → `.` (dot)
- **Medium Blink** → `-` (dash)
- **Long Blink (> 1.2s)** → Delete last character
- **Gap between blinks** → Next character
- **Long gap** → Next word

This project has been completed by help from eye blink detection tutorial of [pyimagesearch.com](https://pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/).It was originally built using dlib for facial landmark detection, but has been improved by replacing it with MediaPipe Face Mesh for better accuracy and easier installation
