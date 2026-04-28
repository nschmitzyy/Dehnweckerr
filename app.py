import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch Fix", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(45%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 30px; padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 10vh;
    }}
    .timer-display {{ font-size: 100px; font-weight: 100; color: white; margin: 20px; }}
    h1, h3, p, label {{ color: white !important; }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: white; color: black;
        font-weight: bold; border: none; padding: 12px; margin-top: 10px;
    }}
    header, footer {{ visibility: hidden !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo" poster="{POSTER_URL}">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- 3. PHASEN ---

# PHASE: SETUP
if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    st.write("Wann soll die Übung beginnen?")
    
    col1, col2 = st.columns(2)
    with col1:
        mins = st.number_input("Minuten", 0, 60, 0)
    with col2:
        secs = st.number_input("Sekunden", 0, 59, 10)
    
    if st.button("Timer starten"):
        st.session_state.total_seconds = (mins * 60) + secs
        st.session_state.phase = "COUNTDOWN"
        st.rerun()

# PHASE: COUNTDOWN (Python-basiert, läuft garantiert ab)
elif st.session_state.phase == "COUNTDOWN":
    st.title("In der Stille...")
    placeholder = st.empty()
    
    for i in range(st.session_state.total_seconds, 0, -1):
        placeholder.markdown(f"<p class='timer-display'>{i}</p>", unsafe_allow_html=True)
        time.sleep(1)
    
    st.session_state.phase = "ALARM"
    st.rerun()

# PHASE: ALARM & KI-ÜBUNG
elif st.session_state.phase == "ALARM":
    st.markdown("<h3>Erhebe dich!</h3>", unsafe_allow_html=True)
    st.audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3", autoplay=True)

    js_code = """
    <div style="text-align: center; color: white;">
        <video id="vid" style="width: 100%; max-width: 400px; border-radius: 20px; transform: scaleX(-1); border: 2px solid white;" autoplay playsinline></video>
        <p id="msg" style="font-size: 20px; margin-top: 10px;">Lade Kamera...</p>
        <div style="width: 100%; height: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;">
            <div id="bar" style="width: 0%; height: 100%; background: #4CAF50; border-radius: 5px; transition: 0.1s;"></div>
        </div>
    </div>

    <script type="module">
        import { Pose } from "https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js";
        import { Camera } from "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js";

        const video = document.getElementById('vid');
        const msg = document.getElementById('msg');
        const bar = document.getElementById('bar');
        let counter = 0;
        let lastTime = 0;

        const pose = new Pose({locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
        pose.setOptions({ modelComplexity: 0, minDetectionConfidence: 0.5 });

        pose.onResults(res => {
            msg.innerText = "Haltung einnehmen!";
            if (res.poseLandmarks) {
                const lm = res.poseLandmarks;
                // Hände über Nase
                if (lm[15].y < lm[0].y && lm[16].y < lm[0].y) {
                    counter++;
                    bar.style.width = (counter / 1.5) + "%";
                    msg.innerText = "Sehr gut! Halten...";
                    if (counter >= 150) {
                        msg.innerText = "FERTIG!";
                    }
                }
            }
        });

        const camera = new Camera(video, {
            onFrame: async () => {
                const now = Date.now();
                if (now - lastTime >= 80) { // ca. 12 FPS
                    lastTime = now;
                    await pose.send({image: video});
                }
            },
            width: 480, height: 360
        });
        camera.start();
    </script>
    """
    components.html(js_code, height=500)
    
    if st.button("Übung beendet - Neustart"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
