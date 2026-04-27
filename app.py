import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. SETTINGS ---
st.set_page_config(page_title="ZenStretch Wecker", page_icon="🧘", layout="centered")

# --- 2. VIDEO-HINTERGRUND & DESIGN (CSS) ---
# Link zu deinem Video auf GitHub
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

st.markdown(f"""
    <style>
    /* Fullscreen Video-Hintergrund */
    #bgVideo {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        z-index: -1;
        object-fit: cover;
        filter: brightness(50%); /* Macht das Video dunkler, damit Schrift lesbar ist */
    }}

    .stApp {{
        background: transparent;
    }}

    /* Die schwebende "Zen-Box" */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 40px !important;
        border-radius: 30px;
        margin-top: 50px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}

    /* Texte & Styling */
    h1, h2, h3, p, label {{
        color: white !important;
        text-align: center;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.5);
    }}

    .timer-display {{
        font-size: 100px !important;
        font-weight: 100;
        color: white;
        text-align: center;
        margin: 20px 0;
    }}

    /* Buttons anpassen */
    .stButton>button {{
        width: 100%;
        border-radius: 20px;
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid white;
        padding: 10px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: white;
        color: #333;
    }}

    /* Verstecke Streamlit-Elemente */
    header, footer {{visibility: hidden;}}
    </style>

    <video autoplay muted loop id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 3. APP LOGIK ---
if 'status' not in st.session_state:
    st.session_state.status = "SETUP"

st.markdown("<h1>ZenStretch</h1>", unsafe_allow_html=True)

# SCHRITT 1: Einstellen
if st.session_state.status == "SETUP":
    st.markdown("<h3>Bereite dich auf die Einkehr vor.</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        minuten = st.number_input("Minuten", 0, 60, 0)
    with col2:
        sekunden = st.number_input("Sekunden", 0, 59, 10)
    
    if st.button("Timer starten"):
        st.session_state.gesamtzeit = minuten * 60 + sekunden
        st.session_state.status = "COUNTDOWN"
        st.rerun()

# SCHRITT 2: Countdown
elif st.session_state.status == "COUNTDOWN":
    platzhalter = st.empty()
    for i in range(st.session_state.gesamtzeit, 0, -1):
        platzhalter.markdown(f"<p class='timer-display'>{i:02d}</p>", unsafe_allow_html=True)
        time.sleep(1)
    st.session_state.status = "ALARM"
    st.rerun()

# SCHRITT 3: Alarm & Pose-Erkennung
elif st.session_state.status == "ALARM":
    st.markdown("<h3 style='color: #ffcccc;'>Erhebe deine Arme zur Sonne.</h3>", unsafe_allow_html=True)
    
    # Gong-Sound (Streamlit Audio)
    st.audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3", format="audio/mp3", autoplay=True)

    # Browser-KI (JavaScript)
    js_code = """
    <div style="text-align: center;">
        <div style="position: relative; display: inline-block;">
            <video id="webcam" style="width: 100%; max-width: 450px; border-radius: 20px; transform: scaleX(-1);"></video>
            <canvas id="overlay" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"></canvas>
        </div>
        <h2 id="feedback" style="color: white; font-weight: 200; margin-top: 15px;">Suche Pose...</h2>
        <div style="width: 100%; background: rgba(255,255,255,0.1); height: 10px; border-radius: 5px; margin-top: 10px;">
            <div id="progress" style="width: 0%; height: 100%; background: white; border-radius: 5px; transition: width 0.2s;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('overlay');
        const ctx = canvas.getContext('2d');
        const bar = document.getElementById('progress');
        const feedback = document.getElementById('feedback');
        
        let counter = 0;
        const target = 100; // Dauer der Dehnung

        const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
        pose.setOptions({modelComplexity: 1, minDetectionConfidence: 0.5});
        
        pose.onResults(res => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (res.poseLandmarks) {
                const points = res.poseLandmarks;
                // Check: Hände (15, 16) über Kopf-Niveau
                if (points[15].y < points[0].y && points[16].y < points[0].y) {
                    counter++;
                    bar.style.width = (counter/target*100) + "%";
                    feedback.innerText = "Haltung bewahren...";
                    if (counter >= target) {
                        feedback.innerText = "Du bist bereit für den Tag.";
                        setTimeout(() => { window.parent.location.reload(); }, 2000);
                    }
                } else {
                    if(counter > 0) counter -= 0.5;
                    bar.style.width = (counter/target*100) + "%";
                    feedback.innerText = "Bitte Arme hoch!";
                }
            }
        });

        const camera = new Camera(video, {
            onFrame: async () => { await pose.send({image: video}); },
            width: 640, height: 480
        });
        camera.start();
    </script>
    """
    components.html(js_code, height=650)

    if st.button("Abbruch"):
        st.session_state.status = "SETUP"
        st.rerun()
