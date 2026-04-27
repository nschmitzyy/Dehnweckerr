import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
import mediapipe as mp
import cv2
import time
import numpy as np

# --- ZEN DESIGN (Custom CSS) ---
st.set_page_config(page_title="StretchWake", page_icon="🧘")
st.markdown("""
    <style>
    .main { background-color: #F0F4F2; }
    .stButton>button { 
        border-radius: 20px; 
        background-color: #A3B18A; 
        color: white;
        border: none;
        padding: 10px 25px;
    }
    h1 { color: #3A5A40; font-family: 'Helvetica Neue', sans-serif; }
    .stProgress > div > div > div > div { background-color: #588157; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧘 StretchWake")
st.write("Dein sanfter Start in den Tag. Stell den Timer und dehne dich wach.")

# --- LOGIK: WINKELBERECHNUNG ---
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# --- MEDIA PIPE POSE PROCESSOR ---
class StretchProcessor(VideoProcessorBase):
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.stretch_complete = False
        self.counter = 0

    def recv(self, frame):
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img, 1)
        results = self.pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            
            # Beispiel: Handgelenk (15), Schulter (11), Hüfte (23)
            # Wir prüfen, ob der Arm für eine Dehnung über den Kopf gehoben wird
            shoulder = [landmarks[11].x, landmarks[11].y]
            elbow = [landmarks[13].x, landmarks[13].y]
            wrist = [landmarks[15].x, landmarks[15].y]
            
            angle = calculate_angle(shoulder, elbow, wrist)

            # Logik: Wenn Winkel > 150 Grad (Arm gestreckt), zähle hoch
            if angle > 150:
                self.counter += 1
            
            if self.counter > 60: # Ca. 2-3 Sekunden halten (je nach FPS)
                self.stretch_complete = True

            # Zeichne Feedback ins Bild (Optional für User)
            cv2.putText(img, f"Stretch-Score: {self.counter}", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return frame

# --- UI CONTROLS ---
tab1, tab2 = st.tabs(["⏰ Wecker", "⏱️ Timer"])

with tab1:
    alarm_time = st.time_input("Wann möchtest du aufwachen?", time(7, 0))
    if st.button("Wecker aktivieren"):
        st.success(f"Wecker für {alarm_time} gestellt.")

with tab2:
    minutes = st.number_input("Minuten", min_value=0, max_value=60, value=1)
    if st.button("Timer starten"):
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                st.metric("Verbleibende Zeit", f"{seconds // 60:02d}:{seconds % 60:02d}")
                time.sleep(1)
            st.warning("ALARM! Zeit zum Dehnen!")
            
            # Hier startet die Kamera-Logik
            webrtc_streamer(key="stretch", video_processor_factory=StretchProcessor)
