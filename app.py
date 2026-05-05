import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import json
from datetime import datetime
import pandas as pd

# --- 1. DATENVERWALTUNG ---
LOG_FILE = "study_log.json"

def load_data():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_study_session(minutes, summary):
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    data.append({
        "date": today, 
        "minutes": round(minutes, 1),
        "summary": summary
    })
    with open(LOG_FILE, "w") as f:
        json.dump(data, f)

# --- 2. CONFIG & STYLE ---
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
    [data-testid="stHeader"], header {{ display: none !important; }}
    .stApp {{ background: transparent !important; }}
    
    .fullscreen-btn {{
        position: fixed; top: 20px; right: 20px; z-index: 9999;
        background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2); color: white;
        padding: 10px 15px; border-radius: 12px; cursor: pointer;
    }}

    .main-card {{
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px);
        border-radius: 30px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 5vh;
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: white; color: black; font-weight: bold;
    }}
    div[data-testid="stWidgetLabel"] p {{ color: white !important; }}
    </style>
    
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    <button class="fullscreen-btn" onclick="toggleFullScreen()">⛶ Vollbild</button>

    <script>
    function toggleFullScreen() {{
        if (!document.fullscreenElement) {{ document.documentElement.requestFullscreen(); }}
        else {{ if (document.exitFullscreen) {{ document.exitFullscreen(); }} }}
    }}
    </script>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

audio_html_src = ""
if os.path.exists("sirene-da-monique.mp3"):
    with open("sirene-da-monique.mp3", "rb") as f:
        audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- 3. PHASEN ---

if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    raw_data = load_data()
    if raw_data:
        df = pd.DataFrame(raw_data)
        st.subheader("Fortschritte")
        df['date_only'] = pd.to_datetime(df['date']).dt.date
        stats = df.groupby('date_only')['minutes'].sum()
        st.bar_chart(stats, height=150)

    st.markdown("---")
    stretch_choice = st.radio("Pose:", ["Vorbeuge", "Hund"])
    col1, col2, col3 = st.columns(3)
    hrs, mins, secs = col1.number_input("Std", 0,23,0), col2.number_input("Min", 0,59,20), col3.number_input("Sek", 0,59,0)
    
    if st.button("LERNEN STARTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.mode = "DOG" if "Hund" in stretch_choice else "FORWARD"
        st.session_state.current_minutes = (hrs * 60) + mins + (secs / 60)
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 80px; font-weight: 100; font-family: monospace;">00:00:00</p>
        </div>
        <div id="exercise-area" style="display: none;">
            <h2 id="hold-timer" style="font-size: 64px; font-family: monospace; color: #ff4b4b;">30.0</h2>
            <div style="position: relative; display: inline-block;">
                <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1); border-radius: 20px; border: 2px solid white;" autoplay playsinline></video>
                <button onclick="switchCam()" style="position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.6); color: white; border: none; border-radius: 50%; width: 40px; height: 40px; cursor: pointer; font-size: 20px;">🔄</button>
            </div>
            <p id="status" style="font-size: 18px; margin-top: 10px;"></p>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script>
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        let timeLeft = {st.session_state.total_seconds};
        let stretchMs = 0; let lastTs = Date.now();
        let currentFacingMode = "user";
        let cameraObj = null;

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
            const video = document.getElementById('vid');
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
            pose.onResults(res => {{
                const now = Date.now(); const dt = now - lastTs; lastTs = now;
                if (!res.poseLandmarks) return;
                const noseY = res.poseLandmarks[0].y;
                const hipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;
                let ok = ("{st.session_state.mode}" === "FORWARD") ? (noseY > hipY + 0.05) : (hipY < noseY - 0.1);
                if (ok) {{
                    alarm.pause(); stretchMs += dt;
                    document.getElementById('hold-timer').innerText = Math.max(0, (30000-stretchMs)/1000).toFixed(1);
                    document.getElementById('hold-timer').style.color = "#4CAF50";
                }} else {{
                    if (stretchMs < 30000) alarm.play();
                    document.getElementById('hold-timer').style.color = "#ff4b4b";
                }}
            }});

            if (cameraObj) await cameraObj.stop();
            
            cameraObj = new Camera(video, {{
                onFrame: async () => {{ await pose.send({{image: video}}); }},
                width: 1280, height: 720, facingMode: currentFacingMode
            }});

            await cameraObj.start();

            // Zoom-Logik (0.5 / Weitwinkel versuchen)
            const stream = video.srcObject;
            const track = stream.getVideoTracks()[0];
            const capabilities = track.getCapabilities();
            if (capabilities.zoom) {{
                try {{
                    await track.applyConstraints({{ advanced: [{{ zoom: capabilities.zoom.min }}] }});
                }} catch (e) {{ console.log("Zoom nicht anwendbar"); }}
            }}
        }}

        function switchCam() {{
            currentFacingMode = (currentFacingMode === "user") ? "environment" : "user";
            document.getElementById('vid').style.transform = (currentFacingMode === "user") ? "scaleX(-1)" : "scaleX(1)";
            startCamera();
        }}
    </script>
    """
    components.html(js_code, height=600)
    if st.button("DEHNEN BEENDET -> RECAP"):
        st.session_state.phase = "RECAP"
        st.rerun()

elif st.session_state.phase == "RECAP":
    st.subheader("📝 Recap")
    recap = st.text_area("Erkenntnisse:", height=150)
    if st.button("FERTIG"):
        save_study_session(st.session_state.current_minutes, recap)
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
