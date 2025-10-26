import cv2
import numpy as np
import time
import math
from fer import FER
from cvzone.HandTrackingModule import HandDetector

# -------------------------------
# CONFIGURATION
# -------------------------------
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
DETECT_WIDTH = 320     # width for processing (speed)
DETECT_HEIGHT = 240    # height for processing
FRAME_SKIP = 2         # process every Nth frame
CLOSE_THRESHOLD = 0.05
TIME_THRESHOLD = 2.0

# -------------------------------
# INIT MODULES
# -------------------------------
# OpenCV face detector (Haar Cascade)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Emotion detector
emotion_detector = FER(mtcnn=True)

# Hand detector
hand_detector = HandDetector(maxHands=1, detectionCon=0.7)

# Video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

# -------------------------------
# STATE VARIABLES
# -------------------------------
frame_count = 0
close_start_time = None
last_emotion = None
stress_start_time = None

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def euclidean(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

# -------------------------------
# MAIN LOOP
# -------------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    if frame_count % FRAME_SKIP != 0:
        continue  # skip frame for speed

    # Flip and downscale for processing
    frame = cv2.flip(frame, 1)
    small_frame = cv2.resize(frame, (DETECT_WIDTH, DETECT_HEIGHT))
    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_center = None
    hand_center = None

    # --- FACE DETECTION ---
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) > 0:
        x, y, w, h = faces[0]
        face_center = (x + w / 2, y + h / 2)
        # Draw rectangle on original frame
        fx = int(x * FRAME_WIDTH / DETECT_WIDTH)
        fy = int(y * FRAME_HEIGHT / DETECT_HEIGHT)
        fw = int(w * FRAME_WIDTH / DETECT_WIDTH)
        fh = int(h * FRAME_HEIGHT / DETECT_HEIGHT)
        cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (0, 255, 0), 2)

        # Emotion detection (on downscaled frame)
        emotions = emotion_detector.detect_emotions(cv2.resize(frame, (DETECT_WIDTH, DETECT_HEIGHT)))
        if emotions:
            dominant = max(emotions[0]['emotions'], key=emotions[0]['emotions'].get)
            last_emotion = dominant
            cv2.putText(frame, f"Emotion: {dominant}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # --- HAND DETECTION ---
    hands = hand_detector.findHands(small_frame, draw=False)
    if hands:
        hand = hands[0]
        cx, cy = hand['center']
        hand_center = (cx, cy)
        # Scale coordinates to original frame
        hx = int(cx * FRAME_WIDTH / DETECT_WIDTH)
        hy = int(cy * FRAME_HEIGHT / DETECT_HEIGHT)
        hand_detector.findHands(frame, draw=True)  # draw on original frame

    # --- STRESS DETECTION ---
    stressed = False
    if face_center and hand_center:
        dist = euclidean(face_center, hand_center)
        if dist < CLOSE_THRESHOLD * DETECT_WIDTH:
            if close_start_time is None:
                close_start_time = time.time()
            elif time.time() - close_start_time > TIME_THRESHOLD:
                if last_emotion in ["sad", "angry", "fear", "disgust"]:
                    stressed = True
        else:
            close_start_time = None

    if stressed:
        if stress_start_time is None:
            stress_start_time = time.time()
        cv2.putText(frame, "😰 Possible Stress Detected!", (50, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        print(f"⚠️ Stress detected: Emotion={last_emotion}")
    else:
        stress_start_time = None

    # --- DISPLAY ---
    cv2.imshow("Stress Detector", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
