import streamlit as st
import streamlit.components.v1 as components
import base64
import os
from datetime import datetime, timedelta

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

if 'logbook' not in st.session_state:
    st.session_state.logbook = []
if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"
if 'stretch_complete' not in st.session_state:
    st.session_state.stretch_complete = False

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(35%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    [data-testid="stHeader"], header {{ display: none !important; }}
    .block-container {{ padding-top: 0rem !important; margin-top: -20px !important; }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
        border-radius: 25px; padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 2vh;
    }}
    .stats-card {{
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px; padding: 15px; margin-bottom: 20px;
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: white; 
        color: black; font-weight: bold; padding: 15px; border: none;
        font-size: 1.2rem; box-shadow: 0 4px 15px rgba(255,255,255,0.2);
    }}
    textarea {{ background: rgba(255,255,255,0.1) !important; color: white !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

def get_stats():
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent = [l for l in st.session_state.logbook if l['date'] > seven_days_ago]
    return sum(l['duration'] for l in recent) // 60, len(recent)

audio_src = ""
if os.path.exists("sirene-da-monique.mp3"):
    with open("sirene-da-monique.mp3", "rb") as f:
        audio_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- NAVIGATION ---
if st.query_params.get("finished") == "true":
    st.session_state.stretch_complete = True
    st.query_params.clear()

# --- PHASEN ---
if st.session_state.phase == "SETUP":
    st.session_state.stretch_complete = False
    st.title("🧘 ZenStretch")
    mins, units = get_stats()
    st.markdown(f'<div class="stats-card"><p style="margin:0; opacity:0.7; padding-top:10px;">LETZTE 7 TAGE</p><h3 style="padding-bottom:10px;">{mins} Min. | {units} Einheiten</h3></div>', unsafe_allow_html=True)
    
    pose = st.radio("Pose:", ["Vorbeuge", "Hund"], horizontal=True)
    c1, c2, c3 = st.columns(3)
    h, m, s = c1.number_input("h",0,23,0), c2.number_input("m",0,59,20), c3.number_input("s",0,59,0)
    
    if st.button("SCHARF SCHALTEN"):
        st.session_state.total_seconds = (h*3600)+(m*60)+s
        st.session_state.mode = "DOG" if "Hund" in pose else "FORWARD"
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    if not st.session_state.stretch_complete:
        js_code = f"""
        <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
            <div id="countdown-area">
                <p id="big-timer" style="font-size: 18vw; font-weight: 100; font-family: monospace; margin: 10px 0;">00:00:00</p>
                <p style="opacity: 0.7;">FOKUS AKTIV</p>
            </div>
            <div id="exercise-area" style="display: none;">
                <h2 id="hold-timer" style="font-size: 14vw; font-family: monospace; margin: 5px 0;">30.0</h2>
                <button id="cam-btn" onclick="requestCam()" style="background: white; color: black; border: none; padding: 15px 25px; border-radius: 50px; font-weight: bold; cursor: pointer; width: 80%;">📷 KAMERA FREIGEBEN</button>
                <div id="video-container" style="display: none; position: relative; width: 90%; max-width: 320px; margin: 0 auto;">
                    <video id="vid" style="width: 100%; border-radius: 15px; border: 2px solid white;" autoplay playsinline></video>
                </div>
                <p id="status" style="margin-top: 10px; font-weight: bold; font-size: 5vw;"></p>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
        <script>
            const alarm = new Audio("{audio_src}"); alarm.loop = true;
            let timeLeft = {st.session_state.total_seconds};
            let stretchMs = 0; let lastTs = Date.now();
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
                const stream = await navigator.mediaDevices.getUserMedia({{ video: true }});
                stream.getTracks().forEach(t => t.stop());
                document.getElementById('cam-btn').style.display = 'none';
                document.getElementById('video-container').style.display = 'block';
                startCamera();
            }}

            async function startCamera() {{
                const video = document.getElementById('vid');
                const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
                pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
                pose.onResults(res => {{
                    if(finished) return;
                    const now = Date.now(); const dt = now - lastTs; lastTs = now;
                    if (!res.poseLandmarks) return;
                    const noseY = res.poseLandmarks[0].y;
                    const avgHipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;
                    let isStretching = ("{st.session_state.mode}" === "FORWARD") ? (noseY > avgHipY + 0.05) : (avgHipY < noseY - 0.1);
                    if (isStretching) {{
                        alarm.pause(); stretchMs += dt;
                        document.getElementById('hold-timer').innerText = Math.max(0, (30000 - stretchMs) / 1000).toFixed(1);
                        if (stretchMs >= 30000) {{
                            finished = true;
                            window.top.location.href = window.top.location.pathname + "?finished=true";
                        }}
                    }} else {{ if (stretchMs < 30000) alarm.play(); }}
                }});
                const camera = new Camera(video, {{ onFrame: async () => {{ await pose.send({{image: video}}); }}, width: 640, height: 480 }});
                camera.start();
            }}
        </script>
        """
        components.html(js_code, height=500)
    
    # Der Button erscheint nur, wenn der Timer auf 0 ist (durch JS-Umleitung getriggert)
    if st.session_state.stretch_complete:
        st.success("🎉 Dehnen erfolgreich beendet!")
        if st.button("DEHNEN ABSCHLIESSEN & ZUM LOGBUCH"):
            st.session_state.phase = "LOGBOOK"
            st.rerun()

elif st.session_state.phase == "LOGBOOK":
    st.title("📝 Lern-Logbuch")
    st.write("Was hast du in der gerade beendeten Lernsession gelernt?")
    note = st.text_area("Zusammenfassung...", placeholder="Schreibe kurz auf, was hängen geblieben ist...", height=150)
    if st.button("SPEICHERN & BEENDEN"):
        st.session_state.logbook.append({"date": datetime.now(), "duration": 30, "notes": note})
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
