import cv2
import mediapipe as mp
import time
import math
import numpy as np

MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----'
}
MORSE_REVERSED = {value: key for key, value in MORSE_CODE_DICT.items()}

DOT_DURATION = 0.25
DASH_DURATION = 0.60
DELETE_DURATION = 1.2
LETTER_GAP = 0.5
WORD_GAP = 1.2

EYE_AR_THRESH = 0.22

LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]

def eye_aspect_ratio(eye_points):
    A = math.dist(eye_points[1], eye_points[5])
    B = math.dist(eye_points[2], eye_points[4])
    C = math.dist(eye_points[0], eye_points[3])
    ear = (A + B) / (2.0 * max(C, 1e-6))
    return ear

def main():
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    cap = cv2.VideoCapture(0)
    time.sleep(1.0)
    
    while True:
        success, frame = cap.read()
        if not success:
            continue
        
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        start_text = "Press 'S' to Start"
        text_size, _ = cv2.getTextSize(start_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        text_x = (w - text_size[0]) // 2
        text_y = (h + text_size[1]) // 2
        
        cv2.putText(frame, start_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press ESC to Quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.imshow("Eye Blink Morse Code", frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s'):
            break
        if key == 27:
            cap.release()
            cv2.destroyAllWindows()
            return

    is_blinking = False
    blink_start_time = 0
    last_event_time = time.time()
    current_morse_char = ""
    message = ""
    feedback_message = ""
    feedback_end_time = 0

    while True:
        success, frame = cap.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame.flags.writeable = False
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)
        frame.flags.writeable = True

        now = time.time()

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_eye_pts = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in LEFT_EYE_INDICES])
            right_eye_pts = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in RIGHT_EYE_INDICES])
            ear = (eye_aspect_ratio(left_eye_pts) + eye_aspect_ratio(right_eye_pts)) / 2.0
            blink_detected_now = ear < EYE_AR_THRESH

            if blink_detected_now and not is_blinking:
                is_blinking = True
                blink_start_time = now
            elif not blink_detected_now and is_blinking:
                is_blinking = False
                blink_duration = now - blink_start_time
                if blink_duration <= DOT_DURATION:
                    current_morse_char += "."
                elif blink_duration <= DASH_DURATION:
                    current_morse_char += "-"
                elif blink_duration <= DELETE_DURATION:
                    if message:
                        message = message[:-1]
                        feedback_message = "DELETED!"
                        feedback_end_time = now + 1
                last_event_time = now

            if not is_blinking:
                gap_duration = now - last_event_time
                if current_morse_char and gap_duration > LETTER_GAP:
                    char = MORSE_REVERSED.get(current_morse_char, "?")
                    message += char
                    current_morse_char = ""
                    last_event_time = now
                elif message and not message.endswith(" ") and gap_duration > WORD_GAP:
                    message += " "
                    last_event_time = now

            cv2.drawContours(frame, [left_eye_pts.astype(int)], -1, (0, 255, 0), 1)
            cv2.drawContours(frame, [right_eye_pts.astype(int)], -1, (0, 255, 0), 1)
            cv2.putText(frame, f"EAR: {ear:.2f}", (w - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.putText(frame, "Press ESC to Quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Morse: {current_morse_char}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Message: {message}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, "Long Blink = Delete", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        if now < feedback_end_time:
            text_size, _ = cv2.getTextSize(feedback_message, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)
            text_x = (w - text_size[0]) // 2
            text_y = (h + text_size[1]) // 2
            cv2.putText(frame, feedback_message, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

        cv2.imshow("Eye Blink Morse Code", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    face_mesh.close()

if __name__ == "__main__":
    main()
