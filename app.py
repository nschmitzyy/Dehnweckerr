import streamlit as st
import streamlit.components.v1 as components
import time
import base64
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch: 20min Preset", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(35%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    header, footer, .stDeployButton, #MainMenu {{
        visibility: hidden !important;
        height: 0 !important;
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 30px; 
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: white; 
        text-align: center; 
        margin-top: 10vh;
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; 
        background: rgba(255, 255, 255, 0.9); 
        color: #000; font-weight: bold; padding: 15px;
        border: none;
    }}
    .stNumberInput div[data-baseweb="input"] {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

audio_html_src = ""
if os.path.exists("sirene-da-monique.mp3"):
    with open("sirene-da-monique.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        audio_html_src = f"data:audio/mp3;base64,{b64}"

if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    st.write("Wähle deine Zeit bis zum Alarm:")
    col1, col2, col3 = st.columns(3)
    with col1: hrs = st.number_input("Std", 0, 23, 0)
    with col2: mins = st.number_input("Min", 0, 59, 20) # Voreinstellung 20
    with col3: secs = st.number_input("Sek", 0, 59, 0)  # Voreinstellung 0
    
    if st.button("WECKER STARTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 80px; font-weight: 100; font-family: monospace; margin: 20px 0;">00:00:00</p>
            <p style="letter-spacing: 2px; opacity: 0.6;">DURCHATMEN...</p>
        </div>
        <div id="exercise-area" style="display: none;">
            <h2 style="color: #ff4b4b; margin: 0; letter-spacing: 5px;">🚨 ALARM 🚨</h2>
            <h2 id="hold-timer" style="font-size: 64px; margin: 10px 0; font-family: monospace;">30.0</h2>
            <div style="position: relative; display: inline-block; border: 2px solid rgba(255,255,255,0.4); border-radius: 20px; overflow: hidden; background: #000;">
                <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1);" autoplay playsinline></video>
            </div>
            <p id="status" style="margin-top: 10px; font-size: 18px; color: #ff4b4b; font-weight: bold;">TIEF VORBEUGEN!</p>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script>
        const bigTimer = document.getElementById('big-timer');
        const countdownArea = document.getElementById('countdown-area');
        const exerciseArea = document.getElementById('exercise-area');
        const holdTimerDisplay = document.getElementById('hold-timer');
        const status = document.getElementById('status');
        const video = document.getElementById('vid');
        const alarm = new Audio("{audio_html_src}");
        alarm.loop = true;
        let timeLeft = {st.session_state.total_seconds};
        let totalHeldMs = 0;
        let lastTimestamp = Date.now();
        function formatTime(s) {{
            const h = Math.floor(s / 3600);
            const m = Math.floor((s % 3600) / 60);
            const sec = s % 60;
            return [h, m, sec].map(v => v < 10 ? "0" + v : v).join(":");
        }}
        const mainInterval = setInterval(() => {{
            if (timeLeft > 0) {{
                timeLeft--;
                bigTimer.innerText = formatTime(timeLeft);
            }} else {{
                clearInterval(mainInterval);
                startAlarmMode();
            }}
        }}, 1000);
        bigTimer.innerText = formatTime(timeLeft);
        async function startAlarmMode() {{
            countdownArea.style.display = 'none';
            exerciseArea.style.display = 'block';
            alarm.play().catch(e => console.log("Audio Blocked"));
            startCamera();
        }}
        async function startCamera() {{
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
            pose.onResults(res => {{
                const now = Date.now();
                const delta = now - lastTimestamp;
                lastTimestamp = now;
                if (res.poseLandmarks) {{
                    const noseY = res.poseLandmarks[0].y;
                    const hipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;
                    if (noseY > hipY + 0.05) {{
                        alarm.pause();
                        totalHeldMs += delta;
                        let rem = Math.max(0, (30000 - totalHeldMs) / 1000);
                        holdTimerDisplay.innerText = rem.toFixed(1);
                        holdTimerDisplay.style.color = "#4CAF50";
                        status.innerText = "Sirene pausiert...";
                        if (totalHeldMs >= 30000) {{
                            status.innerText = "ALLES KLAR! WACH?";
                            holdTimerDisplay.innerText = "✓";
                        }}
                    }} else {{
                        if (totalHeldMs < 30000) alarm.play().catch(()=>{{}});
                        status.innerText = "TIEFER! BEUGE DICH!";
                        status.style.color = "#ff4b4b";
                        holdTimerDisplay.style.color = "#ff4b4b";
                    }}
                }}
            }});
            const camera = new Camera(video, {{
                onFrame: async () => {{ await pose.send({{image: video}}); }},
                width: 480, height: 360
            }});
            camera.start();
        }}
    </script>
    """
    components.html(js_code, height=650)
    if st.button("RESET"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
