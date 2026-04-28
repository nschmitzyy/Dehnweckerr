import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. SETUP & VIDEO-LINK ---
st.set_page_config(page_title="ZenStretch Turbo", layout="centered")
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

# --- 2. CSS & VIDEO HINTERGRUND (Optimiert für Performance) ---
st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: -1;
        object-fit: cover;
        filter: brightness(40%);
        background-color: #000;
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 30px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        text-align: center;
        margin-top: 50px;
    }}
    h1, h3, p {{ color: white !important; font-family: 'Helvetica', sans-serif; }}
    .stDeployButton, header, footer {{ visibility: hidden !important; }}
    </style>

    <video autoplay muted loop playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 3. APP LOGIK ---
if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.title("🧘 ZenStretch")

if st.session_state.phase == "SETUP":
    st.markdown("<h3>Bereit für die Übung?</h3>", unsafe_allow_html=True)
    sek = st.number_input("Countdown (Sekunden)", 5, 300, 10)
    if st.button("Start"):
        st.session_state.timer = sek
        st.session_state.phase = "ALARM" # Wir springen direkt zum Alarm-Modus für den Pre-Load
        st.rerun()

elif st.session_state.phase == "ALARM":
    # Der Timer läuft jetzt INNERHALB der Kamera-Komponente ab.
    # Das bedeutet: Während du die Zahlen siehst, lädt im Hintergrund schon die KI!
    
    js_turbo_code = f"""
    <div style="text-align: center; font-family: sans-serif; color: white;">
        <h1 id="countdown-display" style="font-size: 80px; margin: 10px; font-weight: 100;">{st.session_state.timer}</h1>
        <div id="camera-container" style="display: none; position: relative; margin: 0 auto;">
            <video id="webcam" style="width: 100%; max-width: 450px; border-radius: 20px; transform: scaleX(-1);" autoplay playsinline></video>
            <canvas id="out" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></canvas>
            <h2 id="msg" style="margin-top: 15px;">Arme hoch!</h2>
        </div>
        <p id="loading-msg">KI wird vorbereitet...</p>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const cdDisplay = document.getElementById('countdown-display');
        const camContainer = document.getElementById('camera-container');
        const loadMsg = document.getElementById('loading-msg');
        const msg = document.getElementById('msg');
        const video = document.getElementById('webcam');
        
        let timeLeft = {st.session_state.timer};
        let counter = 0;
        let aiReady = false;

        // 1. MediaPipe SOFORT initialisieren (während Countdown läuft)
        const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
        pose.setOptions({{ modelComplexity: 1, minDetectionConfidence: 0.5 }});
        
        pose.onResults(res => {{
            aiReady = true;
            if (timeLeft <= 0 && res.poseLandmarks) {{
                const lm = res.poseLandmarks;
                // Check: Hände über Nase
                if (lm[15].y < lm[0].y && lm[16].y < lm[0].y) {{
                    counter++;
                    msg.innerText = "Haltung erkannt! " + Math.round(counter/5) + "%";
                    if (counter >= 500) {{
                        msg.innerText = "Meisterschaft erreicht.";
                        setTimeout(() => window.parent.location.reload(), 2000);
                    }}
                }}
            }}
        }});

        const camera = new Camera(video, {{
            onFrame: async () => {{ await pose.send({{image: video}}); }},
            width: 640, height: 480
        }});
        camera.start();

        // 2. Countdown-Intervall
        const interval = setInterval(() => {{
            timeLeft--;
            if (timeLeft > 0) {{
                cdDisplay.innerText = timeLeft;
            }} else {{
                clearInterval(interval);
                cdDisplay.style.display = 'none';
                loadMsg.style.display = 'none';
                camContainer.style.display = 'block';
                // Audio abspielen (Trick: Browser braucht Interaktion)
                const audio = new Audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3");
                audio.loop = true;
                audio.play();
            }}
        }}, 1000);
    </script>
    """
    components.html(js_turbo_code, height=600)

    if st.button("Abbrechen"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
