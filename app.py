import streamlit as st
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
    data.append({"date": today, "minutes": round(minutes, 1), "summary": summary})
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
        position: fixed; top: 20px; right: 20px; z-index: 10000;
        background: rgba(255, 255, 255, 0.2); backdrop-filter: blur(10px);
        border: 2px solid white; color: white; padding: 12px 20px;
        border-radius: 15px; cursor: pointer; font-weight: bold;
    }}

    .main-card {{
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(20px);
        border-radius: 30px; padding: 40px; border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 5vh;
    }}
    .stButton>button {{ width: 100%; border-radius: 50px; background: white; color: black; font-weight: bold; }}
    </style>
    
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    
    <button class="fullscreen-btn" onclick="openFullscreen()">⛶ VOLLBILD AKTIVIEREN</button>

    <script>
    function openFullscreen() {{
        var elem = document.documentElement;
        if (elem.requestFullscreen) {{
            elem.requestFullscreen();
        }} else if (elem.webkitRequestFullscreen) {{ /* Safari */
            elem.webkitRequestFullscreen();
        }} else if (elem.msRequestFullscreen) {{ /* IE11 */
            elem.msRequestFullscreen();
        }}
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
        st.bar_chart(df.groupby(pd.to_datetime(df['date']).dt.date)['minutes'].sum(), height=150)

    st.markdown("---")
    stretch_choice = st.radio("Fokus:", ["Vorbeuge", "Hund"])
    c1, c2, c3 = st.columns(3)
    hrs, mins, secs = c1.number_input("H",0,23,0), c2.number_input("M",0,59,20), c3.number_input("S",0,59,0)
    
    if st.button("LERNEN STARTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.mode = "DOG" if "Hund" in stretch_choice else "FORWARD"
        st.session_state.current_minutes = (hrs * 60) + mins + (secs / 60)
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    # WICHTIG: Wir bauen den HTML-Code für die Kamera hier zusammen
    camera_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    </head>
    <body style="margin:0; background:transparent; color:white; font-family:sans-serif; text-align:center;">
        <div id="countdown-area">
            <h1 id="timer" style="font-size:80px; margin:20px 0;">00:00:00</h1>
        </div>
        <div id="exercise-area" style="display:none;">
            <h2 id="ht" style="font-size:60px; color:#ff4b4b;">30.0</h2>
            <div style="position:relative; display:inline-block;">
                <video id="v" style="width:90%; max-width:400px; border-radius:20px; border:3px solid white; transform:scaleX(-1);" autoplay playsinline></video>
                <button onclick="switchC()" style="position:absolute; bottom:20px; right:30px; width:50px; height:50px; border-radius:50%; background:rgba(0,0,0,0.6); color:white; border:none; font-size:24px;">🔄</button>
            </div>
        </div>
        <script>
            const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
            let sec = {st.session_state.total_seconds};
            let ms = 0; let last = Date.now();
            let mode = "{st.session_state.mode}";
            let face = "user"; let cam = null;

            const countdown = setInterval(() => {{
                if(sec > 0) {{
                    sec--;
                    document.getElementById('timer').innerText = new Date(sec * 1000).toISOString().substr(11, 8);
                }} else {{
                    clearInterval(countdown);
                    document.getElementById('countdown-area').style.display='none';
                    document.getElementById('exercise-area').style.display='block';
                    alarm.play(); start();
                }}
            }}, 1000);

            async function start() {{
                const vid = document.getElementById('v');
                const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
                pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
                pose.onResults(res => {{
                    const now = Date.now(); const dt = now - last; last = now;
                    if(!res.poseLandmarks) return;
                    const noseY = res.poseLandmarks[0].y;
                    const hipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y)/2;
                    let ok = (mode === "FORWARD") ? (noseY > hipY + 0.05) : (hipY < noseY - 0.1);
                    if(ok) {{
                        alarm.pause(); ms += dt;
                        document.getElementById('ht').innerText = Math.max(0, (30000-ms)/1000).toFixed(1);
                        document.getElementById('ht').style.color = "#4CAF50";
                    }} else {{
                        if(ms < 30000) alarm.play();
                        document.getElementById('ht').style.color = "#ff4b4b";
                    }}
                }});
                if(cam) await cam.stop();
                cam = new Camera(vid, {{
                    onFrame: async () => {{ await pose.send({{image: vid}}); }},
                    width: 1280, height: 720, facingMode: face
                }});
                await cam.start();
                const tr = vid.srcObject.getVideoTracks()[0];
                const cap = tr.getCapabilities();
                if(cap.zoom) tr.applyConstraints({{advanced: [{{zoom: cap.zoom.min}}]}});
            }}
            function switchC() {{
                face = (face === "user") ? "environment" : "user";
                document.getElementById('v').style.transform = (face === "user") ? "scaleX(-1)" : "scaleX(1)";
                start();
            }}
        </script>
    </body>
    </html>
    """
    
    # DER FIX: Wir nutzen ein Iframe mit expliziten Permissions direkt via Markdown
    import streamlit.components.v1 as components
    st.components.v1.html(camera_html, height=600, scrolling=False)
    
    # Falls der Browser den Iframe blockt, hier ein manueller Button
    if st.button("DEHNEN BEENDET -> RECAP"):
        st.session_state.phase = "RECAP"
        st.rerun()

elif st.session_state.phase == "RECAP":
    st.subheader("📝 Recap")
    recap = st.text_area("Was hast du gelernt?")
    if st.button("SPEICHERN"):
        save_study_session(st.session_state.current_minutes, recap)
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
