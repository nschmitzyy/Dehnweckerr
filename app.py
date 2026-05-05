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
    /* Hintergrund Video */
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(35%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    
    /* Header-Killer */
    [data-testid="stHeader"], header, .st-emotion-cache-18ni7ap {{
        display: none !important; visibility: hidden !important;
    }}
    
    .block-container {{ 
        padding-top: 0rem !important; 
        margin-top: -50px !important; 
    }}
    
    .stApp {{ background: transparent !important; }}
    
    /* Glas-Design Karte */
    .main-card {{
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px); 
        -webkit-backdrop-filter: blur(20px);
        border-radius: 30px; padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 5vh;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }}
    
    .stButton>button {{
        width: 100%; border-radius: 50px; 
        background: rgba(255, 255, 255, 0.9); 
        color: #000; font-weight: bold; padding: 15px; border: none;
    }}
    
    .stNumberInput div[data-baseweb="input"] {{
        background-color: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }}
    </style>
    
    <video autoplay muted loop playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

# --- 2. VOLLBILD BUTTON RECHTS OBEN ---
fs_html = """
<div style="position: fixed; top: 10px; right: 10px; z-index: 10000;">
    <button onclick="toggleFS()" style="
        width: 40px; height: 40px; border-radius: 50%; 
        border: 1px solid rgba(255,255,255,0.2); 
        background: rgba(255,255,255,0.1); color: white; 
        cursor: pointer; backdrop-filter: blur(10px);
        display: flex; align-items: center; justify-content: center;
    ">⛶</button>
</div>
<script>
function toggleFS() {
    var doc = window.parent.document;
    if (!doc.fullscreenElement) doc.documentElement.requestFullscreen();
    else doc.exitFullscreen();
}
</script>
"""
components.html(fs_html, height=60)

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- 3. AUDIO VORBEREITEN ---
audio_html_src = ""
if os.path.exists("sirene-da-monique.mp3"):
    try:
        with open("sirene-da-monique.mp3", "rb") as f:
            audio_html_src = f"data:audio/mp3;base64,{base64.b64encode(f.read()).decode()}"
    except: pass

# --- 4. PHASEN ---
if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    st.write("Wann soll der Wecker klingeln?")
    
    col1, col2, col3 = st.columns(3)
    hrs = col1.number_input("Std", 0, 23, 0)
    mins = col2.number_input("Min", 0, 59, 20) 
    secs = col3.number_input("Sek", 0, 59, 0)
    
    if st.button("SCHARF SCHALTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 80px; font-weight: 100; font-family: monospace; margin: 20px 0;">00:00:00</p>
            <p style="opacity: 0.7; letter-spacing: 2px;">KONZENTRATION...</p>
        </div>

        <div id="exercise-area" style="display: none;">
            <h2 style="color: #ff4b4b; margin: 0; letter-spacing: 5px;">🚨 ALARM 🚨</h2>
            <h2 id="hold-timer" style="font-size: 64px; margin: 10px 0; font-family: monospace;">30.0</h2>
            <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1); border-radius: 20px; border: 2px solid white;" autoplay playsinline></video>
            <p id="status" style="margin-top: 10px; font-size: 18px; color: #ff4b4b; font-weight: bold;">TIEFER GEHEN!</p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>

    <script>
        const holdTimerDisplay = document.getElementById('hold-timer');
        const status = document.getElementById('status');
        const video = document.getElementById('vid');
        const alarm = new Audio("{audio_html_src}");
        alarm.loop = true;

        let timeLeft = {st.session_state.total_seconds};
        let stretchMs = 0;
        let lastTs = Date.now();

        const timerInt = setInterval(() => {{
            if (timeLeft > 0) {{
                timeLeft--;
                document.getElementById('big-timer').innerText = new Date(timeLeft * 1000).toISOString().substr(11, 8);
            }} else {{
                clearInterval(timerInt);
                document.getElementById('countdown-area').style.display = 'none';
                document.getElementById('exercise-area').style.display = 'block';
                alarm.play().catch(e => {{}});
                startCamera();
            }}
        }}, 1000);

        async function startCamera() {{
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});

            pose.onResults(res => {{
                const now = Date.now();
                const dt = now - lastTs;
                lastTs = now;

                if (res.poseLandmarks) {{
                    const noseY = res.poseLandmarks[0].y;
                    const hipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;

                    if (noseY > hipY + 0.05) {{
                        alarm.pause();
                        stretchMs += dt;
                        let rem = Math.max(0, (30000 - stretchMs) / 1000);
                        holdTimerDisplay.innerText = rem.toFixed(1);
                        holdTimerDisplay.style.color = "#4CAF50";
                        status.innerText = "Sirene pausiert...";
                        if (stretchMs >= 30000) {{
                            status.innerText = "FERTIG!";
                            holdTimerDisplay.innerText = "✓";
                        }}
                    }} else {{
                        if (stretchMs < 30000) alarm.play().catch(()=>{{}});
                        status.innerText = "TIEFER GEHEN!";
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
