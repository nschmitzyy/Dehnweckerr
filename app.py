import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. GRUNDKONFIGURATION ---
st.set_page_config(page_title="ZenStretch", page_icon="🧘", layout="centered")

# Dein Video-Link von GitHub
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

# --- 2. CSS FÜR PROFESSIONELLE ZENTRIERUNG ---
st.markdown(f"""
    <style>
    /* Fullscreen Video Hintergrund-Fix */
    #bgVideo {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1;
        object-fit: cover; /* Füllt den Bildschirm ohne Verzerrung */
        object-position: center; /* Zentriert das Video */
        filter: brightness(45%); /* Optimale Lesbarkeit der Schrift */
    }}

    /* Streamlit UI Transparenz */
    .stApp {{
        background: transparent;
    }}

    /* Die schwebende Glas-Box */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 40px !important;
        border-radius: 30px;
        margin-top: 50px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.4);
    }}

    /* Texte & Timer Styling */
    h1, h2, h3, p, label, .stMarkdown {{
        color: white !important;
        text-align: center;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.6);
        font-family: 'Helvetica Neue', sans-serif;
    }}

    .timer-display {{
        font-size: clamp(60px, 10vw, 120px) !important; /* Passt sich Bildschirmgröße an */
        font-weight: 100;
        margin: 20px 0;
    }}

    /* Buttons */
    .stButton>button {{
        width: 100%;
        border-radius: 25px;
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid white;
        padding: 12px;
        transition: 0.4s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    .stButton>button:hover {{
        background-color: white;
        color: #1a1a1a;
        box-shadow: 0 0 20px rgba(255,255,255,0.4);
    }}

    /* Verstecke Streamlit-Standardelemente */
    header, footer {{visibility: hidden;}}
    </style>

    <video autoplay muted loop playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 3. APP LOGIK ---
if 'status' not in st.session_state:
    st.session_state.status = "SETUP"

st.markdown("<h1>ZenStretch</h1>", unsafe_allow_html=True)

# PHASE 1: Timer einstellen
if st.session_state.status == "SETUP":
    st.markdown("<h3>Stelle die Zeit deiner Meditation ein.</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        minuten = st.number_input("Minuten", 0, 60, 0, key="m_in")
    with col2:
        sekunden = st.number_input("Sekunden", 0, 59, 10, key="s_in")
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Timer starten"):
        st.session_state.gesamtzeit = minuten * 60 + sekunden
        st.session_state.status = "COUNTDOWN"
        st.rerun()

# PHASE 2: Countdown läuft
elif st.session_state.status == "COUNTDOWN":
    platzhalter = st.empty()
    for i in range(st.session_state.gesamtzeit, 0, -1):
        platzhalter.markdown(f"<p class='timer-display'>{i:02d}</p>", unsafe_allow_html=True)
        time.sleep(1)
    st.session_state.status = "ALARM"
    st.rerun()

# PHASE 3: Dehn-Check (KI im Browser)
elif st.session_state.status == "ALARM":
    st.markdown("<h3 style='color: #ffb3b3;'>Erhebe deine Arme, um den Gong zu besänftigen.</h3>", unsafe_allow_html=True)
    
    # Gong-Audio
    st.audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3", format="audio/mp3", autoplay=True)

    js_code = """
    <div style="text-align: center;">
        <div style="position: relative; display: inline-block; border-radius: 20px; overflow: hidden; border: 2px solid rgba(255,255,255,0.3);">
            <video id="webcam" style="width: 100%; max-width: 480px; transform: scaleX(-1); display: block;"></video>
            <canvas id="overlay" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"></canvas>
        </div>
        <h2 id="feedback" style="color: white; font-weight: 300; margin-top: 15px;">Suche Pose...</h2>
        <div style="width: 100%; max-width: 480px; background: rgba(255,255,255,0.1); height: 12px; border-radius: 6px; margin: 15px auto;">
            <div id="progress" style="width: 0%; height: 100%; background: #ffffff; border-radius: 6px; transition: width 0.2s ease;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const video = document.getElementById('webcam');
        const canvas = document.getElementById('overlay');
        const bar = document.getElementById('progress');
        const feedback = document.getElementById('feedback');
        
        let score = 0;
        const goal = 100; // Dauer der Übung

        const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
        pose.setOptions({modelComplexity: 1, minDetectionConfidence: 0.6});
        
        pose.onResults(res => {
            if (res.poseLandmarks) {
                const points = res.poseLandmarks;
                // Check: Handgelenke (15, 16) über Nasenspitze (0)
                if (points[15].y < points[0].y && points[16].y < points[0].y) {
                    score++;
                    bar.style.width = (score/goal*100) + "%";
                    feedback.innerText = "Haltung perfekt. Bleib so...";
                    feedback.style.color = "#b3ffb3";
                    
                    if (score >= goal) {
                        feedback.innerText = "Du bist erwacht.";
                        setTimeout(() => { window.parent.location.reload(); }, 2000);
                    }
                } else {
                    if(score > 0) score -= 0.5;
                    bar.style.width = (score/goal*100) + "%";
                    feedback.innerText = "Bitte hebe deine Arme über den Kopf!";
                    feedback.style.color = "#ffb3b3";
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
    components.html(js_code, height=680)

    if st.button("Abbruch & Reset"):
        st.session_state.status = "SETUP"
        st.rerun()
        
