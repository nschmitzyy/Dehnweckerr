import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from datetime import datetime, timedelta

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

# Daten-Initialisierung im Session State
if 'logbook' not in st.session_state:
    st.session_state.logbook = [] # Liste von Dicts: {"date": dt, "duration": sec, "notes": str}

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
    .block-container {{ padding-top: 0rem !important; margin-top: -20px !important; }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-radius: 25px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 2vh;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }}
    .stats-card {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 15px; margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: rgba(255, 255, 255, 0.9); 
        color: #000; font-weight: bold; padding: 12px; border: none;
    }}
    div[data-testid="stWidgetLabel"] p {{ color: white !important; font-size: 1.1rem; }}
    textarea {{ background: rgba(255,255,255,0.1) !important; color: white !important; border-radius: 15px !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

# Hilfsfunktion für Statistiken
def get_stats():
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_logs = [l for l in st.session_state.logbook if l['date'] > seven_days_ago]
    total_sec = sum(l['duration'] for l in recent_logs)
    units = len(recent_logs)
    return total_sec // 60, units

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
""", height=50)

# Audio
audio_html_src = ""
if os.path.exists("sirene-da-monique.mp3"):
    with open("sirene-da-monique.mp3", "rb") as f:
        audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- PHASE: SETUP ---
if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    
    # Dashboard
    mins_total, units_total = get_stats()
    st.markdown(f"""
    <div class="stats-card">
        <p style="margin:0; opacity:0.7;">Letzte 7 Tage</p>
        <h3 style="margin:5px 0;">{mins_total} Min. | {units_total} Einheiten</h3>
    </div>
    """, unsafe_allow_html=True)

    stretch_choice = st.radio("Pose:", ["Vorbeuge (Rücken & Beine)", "Herabschauender Hund (Bloodflow)"], horizontal=True)
    c1, c2, c3 = st.columns(3)
    hrs = c1.number_input("Std", 0, 23, 0)
    mins = c2.number_input("Min", 0, 59, 20)
    secs = c3.number_input("Sek", 0, 59, 0)
    
    if st.button("SCHARF SCHALTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.mode = "DOG" if "Hund" in stretch_choice else "FORWARD"
        st.session_state.phase = "ALARM_READY"
        st.rerun()

# --- PHASE: TRAINING ---
elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif; width: 100%;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 18vw; font-weight: 100; font-family: monospace; margin: 10px 0; line-height: 1;">00:00:00</p>
            <p style="opacity: 0.7; font-size: 3.5vw;">FOKUS AKTIV</p>
        </div>
        
        <div id="exercise-area" style="display: none;">
            <h2 id="hold-timer" style="font-size: 14vw; font-family: monospace; margin: 5px 0;">30.0</h2>
            <button id="cam-perm-btn" onclick="requestCam()" style="background: white; color: black; border: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; cursor: pointer; margin-bottom: 15px; width: 80%;">📷 KAMERA FREIGEBEN</button>
            <div id="video-container" style="display: none; position: relative; width: 90%; max-width: 320px; margin: 0 auto;">
                <video id="vid" style="width: 100%; border-radius: 15px; border: 2px solid white; transition: transform 0.3s ease;" autoplay playsinline></video>
                <button onclick="switchCamera()" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.6); color: white; border: 1px solid white; border-radius: 20px; padding: 8px 12px; cursor: pointer; font-size: 12px; z-index: 100;">🔄</button>
            </div>
            <p id="status" style="margin-top: 10px; font-size: 4.5vw; font-weight: bold;"></p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script>
        const mode = "{st.session_state.mode}";
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        let timeLeft = {st.session_state.total_seconds};
        let stretchMs = 0; let lastTs = Date.now();
        let currentFacingMode = "user";
        let cameraObj = null;
        let finished = false;

        const timerInt = setInterval(() => {{
            if (timeLeft > 0) {{
                timeLeft--;
                document.getElementById('big-timer').innerText = new Date(timeLeft * 1000).toISOString().substr(11, 8);
            }} else {{
                clearInterval(timerInt);
                document.getElementById('countdown-area').style.display = 'none';
                document.getElementById('exercise-area').style.display = 'block';
                alarm.play();
            }}
        }}, 1000);

        async function requestCam() {{
            try {{
                const stream = await navigator.mediaDevices.getUserMedia({{ video: true }});
                stream.getTracks().forEach(track => track.stop());
                document.getElementById('cam-perm-btn').style.display = 'none';
                document.getElementById('video-container').style.display = 'block';
                startCamera();
            }} catch (err) {{ alert("Kamera-Fehler"); }}
        }}

        async function startCamera() {{
            const video = document.getElementById('vid');
            video.style.transform = (currentFacingMode === "user") ? "scaleX(-1)" : "scaleX(1)";
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
            
            pose.onResults(res => {{
                if (finished) return;
                const now = Date.now(); const dt = now - lastTs; lastTs = now;
                if (!res.poseLandmarks) return;
                const noseY = res.poseLandmarks[0].y;
                const avgHipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;
                let isStretching = (mode === "FORWARD") ? (noseY > avgHipY + 0.05) : (avgHipY < noseY - 0.1);

                if (isStretching) {{
                    alarm.pause(); stretchMs += dt;
                    let rem = Math.max(0, (30000 - stretchMs) / 1000);
                    document.getElementById('hold-timer').innerText = rem.toFixed(1);
                    document.getElementById('hold-timer').style.color = "#4CAF50";
                    document.getElementById('status').innerText = "HALTEN!";
                    if (stretchMs >= 30000 && !finished) {{
                        finished = true;
                        window.parent.postMessage({{"type": "STRETCH_DONE"}}, "*");
                    }}
                }} else {{
                    if (stretchMs < 30000) alarm.play();
                    document.getElementById('hold-timer').style.color = "#ff4b4b";
                    document.getElementById('status').innerText = "TIEFER!";
                }}
            }});

            cameraObj = new Camera(video, {{
                onFrame: async () => {{ await pose.send({{image: video}}); }},
                width: 640, height: 480, facingMode: currentFacingMode
            }});
            cameraObj.start();
        }}
        function switchCamera() {{
            currentFacingMode = (currentFacingMode === "user") ? "environment" : "user";
            startCamera();
        }}
    </script>
    """
    components.html(js_code, height=550)
    
    # Message Listener für Streamlit (Um Phase zu wechseln wenn fertig)
    st.components.v1.html("""
        <script>
        window.addEventListener("message", (event) => {
            if (event.data.type === "STRETCH_DONE") {
                window.parent.location.hash = "done";
            }
        });
        </script>
    """, height=0)
    
    # Trick um von JS zurück zu Streamlit zu kommen
    if st.button("MANUELL FERTIG (Logbuch)"):
        st.session_state.phase = "LOGBOOK"
        st.rerun()

# --- PHASE: LOGBOOK (Active Remembering) ---
elif st.session_state.phase == "LOGBOOK":
    st.title("📝 Logbuch")
    st.subheader("Active Remembering")
    st.write("Was hast du während dieser Dehneinheit über deinen Körper oder deinen Fokus gelernt?")
    
    note = st.text_area("Deine Erkenntnis...", placeholder="z.B. Linke Hüfte ist heute fester als rechts...")
    
    if st.button("SPEICHERN & BEENDEN"):
        # Daten sichern
        new_entry = {
            "date": datetime.now(),
            "duration": 30, # Die 30 Sekunden Dehnzeit
            "notes": note
        }
        st.session_state.logbook.append(new_entry)
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
