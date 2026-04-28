import streamlit as st
import streamlit.components.v1 as components
import time
import base64
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch: Instant Alarm", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(30%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-radius: 30px; padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 5vh;
    }}
    .timer-display {{ font-size: 100px; font-weight: 100; font-family: monospace; margin: 10px; color: #fff; }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: #ffffff; color: #000; font-weight: bold; padding: 15px;
    }}
    header, footer {{ visibility: hidden !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- 2. AUDIO VORBEREITEN ---
audio_html_src = ""
if os.path.exists("sirene-da-monique.mp3"):
    with open("sirene-da-monique.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        audio_html_src = f"data:audio/mp3;base64,{b64}"

# --- 3. PHASEN ---

if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    st.write("Der Alarm startet SOFORT nach Ablauf der Zeit.")
    c1, c2 = st.columns(2)
    with c1: mins = st.number_input("Minuten", 0, 60, 0)
    with c2: secs = st.number_input("Sekunden", 0, 59, 10)
    
    if st.button("WECKER SCHARF SCHALTEN"):
        st.session_state.total_seconds = (mins * 60) + secs
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    # Dieser Teil kombiniert Countdown und Kamera in einem einzigen HTML-Block,
    # damit der Sound ohne erneutes Klicken ausgelöst werden kann.
    
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 100px; font-weight: 100; font-family: monospace; margin: 20px 0;">0</p>
            <p id="hint">Bereite dich vor...</p>
        </div>

        <div id="exercise-area" style="display: none;">
            <h2 style="color: #ff4b4b; margin: 0;">🚨 ALARM! 🚨</h2>
            <h2 id="hold-timer" style="font-size: 64px; margin: 10px 0; font-family: monospace;">30.0</h2>
            <div style="position: relative; display: inline-block; border: 2px solid white; border-radius: 20px; overflow: hidden; background: #000;">
                <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1);" autoplay playsinline></video>
            </div>
            <p id="status" style="margin-top: 10px; font-size: 18px; color: #ff4b4b;">BEUGE DICH!</p>
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
        let isAlarmActive = false;

        // 1. COUNTDOWN STARTEN
        const mainInterval = setInterval(() => {{
            timeLeft--;
            bigTimer.innerText = timeLeft;
            
            if (timeLeft <= 0) {{
                clearInterval(mainInterval);
                startAlarmMode();
            }}
        }}, 1000);
        bigTimer.innerText = timeLeft;

        async function startAlarmMode() {{
            isAlarmActive = true;
            countdownArea.style.display = 'none';
            exerciseArea.style.display = 'block';
            
            // SOFORTIGER SOUND (funktioniert, weil der User "Scharf schalten" geklickt hat)
            alarm.play().catch(e => console.log("Audio Blocked:", e));
            
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
                            status.innerText = "FERTIG!";
                            holdTimerDisplay.innerText = "✓";
                        }}
                    }} else {{
                        if (totalHeldMs < 30000) alarm.play().catch(()=>{{}});
                        status.innerText = "TIEFER! BEUGE DICH!";
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
