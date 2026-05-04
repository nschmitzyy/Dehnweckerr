import streamlit as st
import streamlit.components.v1 as components
import base64
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(35%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    [data-testid="stHeader"], header, .st-emotion-cache-18ni7ap {{
        display: none !important; visibility: hidden !important;
    }}
    .block-container {{ padding-top: 0rem !important; margin-top: -50px !important; }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-radius: 30px; padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 5vh;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: rgba(255, 255, 255, 0.9); 
        color: #000; font-weight: bold; padding: 15px; border: none;
    }}
    div[data-testid="stWidgetLabel"] p {{ color: white !important; font-size: 1.1rem; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

# Vollbild Button
components.html("""
<div style="position: fixed; top: 10px; right: 10px; z-index: 10000;">
    <button onclick="toggleFS()" style="width: 40px; height: 40px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: white; cursor: pointer; backdrop-filter: blur(10px);">⛶</button>
</div>
<script>
function toggleFS() {
    var doc = window.parent.document;
    if (!doc.fullscreenElement) doc.documentElement.requestFullscreen();
    else doc.exitFullscreen();
}
</script>
""", height=60)

# Audio
audio_html_src = ""
if os.path.exists("sirene-da-monique.mp3"):
    with open("sirene-da-monique.mp3", "rb") as f:
        audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    
    # Auswahl der Übung
    stretch_choice = st.radio("Wähle deine Pose:", ["Vorbeuge (Rücken & Beine)", "Herabschauender Hund (Bloodflow)"])
    
    st.write("Timer einstellen:")
    col1, col2, col3 = st.columns(3)
    hrs = col1.number_input("Std", 0, 23, 0)
    mins = col2.number_input("Min", 0, 59, 20)
    secs = col3.number_input("Sek", 0, 59, 0)
    
    if st.button("SCHARF SCHALTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.mode = "DOG" if "Hund" in stretch_choice else "FORWARD"
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 80px; font-weight: 100; font-family: monospace;">00:00:00</p>
            <p style="opacity: 0.7;">TABS AUSGEBLENDET? FOKUS...</p>
        </div>
        <div id="exercise-area" style="display: none;">
            <h2 style="color: #ff4b4b;">🚨 ZEIT ZUM DEHNEN! 🚨</h2>
            <h2 id="hold-timer" style="font-size: 64px; font-family: monospace;">30.0</h2>
            <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1); border-radius: 20px; border: 2px solid white;" autoplay playsinline></video>
            <p id="status" style="margin-top: 10px; font-size: 20px; font-weight: bold;"></p>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script>
        const mode = "{st.session_state.mode}";
        const holdTimerDisplay = document.getElementById('hold-timer');
        const status = document.getElementById('status');
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        let timeLeft = {st.session_state.total_seconds};
        let stretchMs = 0; let lastTs = Date.now();

        const timerInt = setInterval(() => {{
            if (timeLeft > 0) {{
                timeLeft--;
                document.getElementById('big-timer').innerText = new Date(timeLeft * 1000).toISOString().substr(11, 8);
            }} else {{
                clearInterval(timerInt);
                document.getElementById('countdown-area').style.display = 'none';
                document.getElementById('exercise-area').style.display = 'block';
                alarm.play(); startCamera();
            }}
        }}, 1000);

        async function startCamera() {{
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
            pose.onResults(res => {{
                const now = Date.now(); const dt = now - lastTs; lastTs = now;
                if (!res.poseLandmarks) return;

                const noseY = res.poseLandmarks[0].y;
                const lHipY = res.poseLandmarks[23].y;
                const rHipY = res.poseLandmarks[24].y;
                const avgHipY = (lHipY + rHipY) / 2;

                let isStretching = false;
                if (mode === "FORWARD") {{
                    if (noseY > avgHipY + 0.05) isStretching = true;
                    status.innerText = isStretching ? "Sirene pausiert..." : "TIEFER BEUGEN!";
                }} else {{ // DOG MODE
                    if (avgHipY < noseY - 0.1) isStretching = true;
                    status.innerText = isStretching ? "Gute Form! Halten..." : "HÜFTE HÖHER! (V-Form)";
                }}

                if (isStretching) {{
                    alarm.pause(); stretchMs += dt;
                    let rem = Math.max(0, (30000 - stretchMs) / 1000);
                    holdTimerDisplay.innerText = rem.toFixed(1);
                    holdTimerDisplay.style.color = "#4CAF50";
                    if (stretchMs >= 30000) {{ holdTimerDisplay.innerText = "✓"; status.innerText = "FERTIG!"; }}
                }} else {{
                    if (stretchMs < 30000) alarm.play();
                    holdTimerDisplay.style.color = "#ff4b4b";
                }}
            }});
            new Camera(document.getElementById('vid'), {{
                onFrame: async () => {{ await pose.send({{image: document.getElementById('vid')}}); }},
                width: 480, height: 360
            }}).start();
        }}
    </script>
    """
    components.html(js_code, height=650)
    if st.button("RESET"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
