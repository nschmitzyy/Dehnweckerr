import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. KONFIGURATION ---
# Ersetze den Link, falls dein Branch nicht 'main' heißt
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

st.set_page_config(page_title="ZenStretch", page_icon="🧘", layout="centered")

# --- 2. CSS & VIDEO BACKGROUND ---
st.markdown(f"""
    <style>
    /* Video-Hintergrund fixieren */
    #bgVideo {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        z-index: -1;
        object-fit: cover;
        filter: brightness(50%); /* Dunkler für bessere Lesbarkeit */
    }}

    .stApp {{
        background: transparent;
247740_medium.mp4
    }}

    /* Schwebender Glaskasten für die UI */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 40px !important;
        border-radius: 30px;
        margin-top: 50px;
    }}

    /* Texte & Timer */
    h1, h3, p, .stMarkdown {{
        color: white !important;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
        text-shadow: 1px 1px 10px rgba(0,0,0,0.5);
    }}

    .timer-display {{
        font-size: 120px !important;
        font-weight: 100;
        color: white;
        text-align: center;
        margin: 20px 0;
    }}

    /* Buttons & Inputs */
    .stButton>button {{
        width: 100%;
        border-radius: 25px;
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 1px solid white;
        padding: 10px;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: white;
        color: black;
    }}

    /* Verstecke Streamlit Header/Footer */
    header, footer {{visibility: hidden;}}
    </style>

    <video autoplay muted loop id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 3. APP LOGIK ---
if 'state' not in st.session_state:
    st.session_state.state = "SETUP" # Mögliche States: SETUP, COUNTDOWN, ALARM

st.markdown("<h1>ZenStretch</h1>", unsafe_allow_html=True)

# STATE: SETUP
if st.session_state.state == "SETUP":
    st.markdown("<h3>Wann möchtest du aus der Stille erwachen?</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        m = st.number_input("Minuten", 0, 60, 0)
    with col2:
        s = st.number_input("Sekunden", 0, 59, 10)
    
    if st.button("Timer starten"):
        st.session_state.duration = m * 60 + s
        st.session_state.state = "COUNTDOWN"
        st.rerun()

# STATE: COUNTDOWN
elif st.session_state.state == "COUNTDOWN":
    placeholder = st.empty()
    for i in range(st.session_state.duration, 0, -1):
        placeholder.markdown(f"<p class='timer-display'>{i:02d}</p>", unsafe_allow_html=True)
        time.sleep(1)
    st.session_state.state = "ALARM"
    st.rerun()

# STATE: ALARM & DEHNEN
elif st.session_state.state == "ALARM":
    st.markdown("<h3 style='color: #ff4b4b;'>Die Zeit ist gekommen. Erhebe dich.</h3>", unsafe_allow_html=True)
    
    # Gong-Sound (Loop)
    st.audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3", format="audio/mp3", autoplay=True)

    # Browser-KI (MediaPipe JavaScript)
    js_ui = """
    <div style="text-align: center;">
        <div style="position: relative; display: inline-block;">
            <video id="v" style="width: 100%; max-width: 450px; border-radius: 20px; transform: scaleX(-1);"></video>
            <canvas id="c" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"></canvas>
        </div>
        <h2 id="msg" style="color: white; font-weight: 200; margin-top: 15px;">Arme über den Kopf!</h2>
        <div style="width: 100%; background: rgba(255,255,255,0.1); height: 8px; border-radius: 4px; margin-top: 10px;">
            <div id="bar" style="width: 0%; height: 100%; background: #fff; border-radius: 4px; transition: width 0.2s;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const video = document.getElementById('v');
        const canvas = document.getElementById('c');
        const ctx = canvas.getContext('2d');
        const bar = document.getElementById('bar');
        const msg = document.getElementById('msg');
        
        let count = 0;
        const goal = 120; // ca. 8 Sekunden

        const pose = new Pose({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`});
        pose.setOptions({modelComplexity: 1, minDetectionConfidence: 0.5});
        
        pose.onResults(res => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            if (res.poseLandmarks) {
                const lm = res.poseLandmarks;
                // Logik: Hände (15,16) über Nase (0)
                if (lm[15].y < lm[0].y && lm[16].y < lm[0].y) {
                    count++;
                    bar.style.width = (count/goal*100) + "%";
                    msg.innerText = "Haltung erkannt...";
                    if (count >= goal) {
                        msg.innerText = "Erwacht. Seite wird geladen...";
                        setTimeout(() => { window.parent.location.reload(); }, 2000);
                    }
                } else {
                    if(count > 0) count -= 0.5;
                    bar.style.width = (count/goal*100) + "%";
                    msg.innerText = "Bitte Arme heben!";
                }
            }
        });

        const cam = new Camera(video, {onFrame: async () => {await pose.send({image: video});}, width: 640, height: 480});
        cam.start();
    </script>
    """
    components.html(js_ui, height=650)

    if st.button("Notfall: Zurück zum Start"):
        st.session_state.state = "SETUP"
        st.rerun()
