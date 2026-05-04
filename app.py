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
        backdrop-filter: blur(20px); border-radius: 30px; padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 2vh;
    }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: white; color: black; font-weight: bold;
    }}
    /* Radio Button Styling */
    div[data-testid="stWidgetLabel"] p {{ color: white !important; font-size: 1.2rem; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo"><source src="{VIDEO_URL}" type="video/mp4"></video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

# Vollbild Button
components.html("""
<div style="position: fixed; top: 10px; right: 10px; z-index: 10000;">
    <button onclick="toggleFS()" style="width: 40px; height: 40px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: white; cursor: pointer;">⛶</button>
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

# --- 4. LOGIK ---
if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    
    # NEU: Modus Auswahl
    mode = st.radio("Was möchtest du tun?", ["Dehnen (30 Sek halten)", "15 Kniebeugen"], index=0)
    
    st.write("Wann soll der Wecker klingeln?")
    c1, c2, c3 = st.columns(3)
    hrs = c1.number_input("Std", 0, 23, 0)
    mins = c2.number_input("Min", 0, 59, 20)
    secs = c3.number_input("Sek", 0, 59, 0)
    
    if st.button("SCHARF SCHALTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.mode = "STRETCH" if "Dehnen" in mode else "SQUATS"
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 80px; font-weight: 100; font-family: monospace;">00:00:00</p>
            <p style="opacity: 0.7;">FOKUSSIERT BLEIBEN...</p>
        </div>
        <div id="exercise-area" style="display: none;">
            <h2 style="color: #ff4b4b; letter-spacing: 5px;">🚨 ALARM 🚨</h2>
            <h1 id="task-display" style="font-size: 60px; margin: 10px 0;">30.0</h1>
            <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1); border-radius: 20px; border: 2px solid white;" autoplay playsinline></video>
            <p id="status-msg" style="font-size: 20px; margin-top: 10px; font-weight: bold;"></p>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script>
        const mode = "{st.session_state.mode}";
        const taskDisplay = document.getElementById('task-display');
        const statusMsg = document.getElementById('status-msg');
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        
        let timeLeft = {st.session_state.total_seconds};
        let stretchMs = 0;
        let squatCount = 0;
        let isDown = false;
        let lastTs = Date.now();

        // Timer Logik
        const timerInt = setInterval(() => {{
            if (timeLeft > 0) {{
                timeLeft--;
                document.getElementById('big-timer').innerText = new Date(timeLeft * 1000).toISOString().substr(11, 8);
            }} else {{
                clearInterval(timerInt);
                document.getElementById('countdown-area').style.display = 'none';
                document.getElementById('exercise-area').style.display = 'block';
                alarm.play();
                startCamera();
            }}
        }}, 1000);

        async function startCamera() {{
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
            pose.onResults(res => {{
                const now = Date.now();
                const dt = now - lastTs; lastTs = now;
                if (!res.poseLandmarks) return;

                const nose = res.poseLandmarks[0].y;
                const hip = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;

                if (mode === "STRETCH") {{
                    if (nose > hip + 0.05) {{
                        alarm.pause(); stretchMs += dt;
                        let rem = Math.max(0, (30000 - stretchMs) / 1000);
                        taskDisplay.innerText = rem.toFixed(1) + "s";
                        statusMsg.innerText = "Gut so! Halten...";
                        if (stretchMs >= 30000) {{ taskDisplay.innerText = "✓"; statusMsg.innerText = "FERTIG!"; }}
                    }} else {{
                        if (stretchMs < 30000) alarm.play();
                        statusMsg.innerText = "TIEFER BEUGEN!";
                    }}
                }} else {{ // SQUAT MODE
                    if (hip > 0.75) {{ // Tiefpunkt
                        if (!isDown) {{ isDown = true; }}
                        statusMsg.innerText = "Und wieder hoch!";
                    }} else if (hip < 0.6 && isDown) {{ // Wieder oben
                        isDown = false;
                        squatCount++;
                        if (squatCount <= 15) alarm.pause(); 
                        setTimeout(() => {{ if(squatCount < 15) alarm.play(); }}, 800);
                    }}
                    taskDisplay.innerText = squatCount + " / 15";
                    if (squatCount >= 15) {{ taskDisplay.innerText = "✓"; statusMsg.innerText = "SAUBER!"; alarm.pause(); }}
                    else if (!isDown) {{ statusMsg.innerText = "GEH TIEF!"; }}
                }}
            }});
            const cam = new Camera(document.getElementById('vid'), {{
                onFrame: async () => {{ await pose.send({{image: document.getElementById('vid')}}); }},
                width: 480, height: 360
            }});
            cam.start();
        }}
    </script>
    """
    components.html(js_code, height=650)
    if st.button("RESET"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
