import streamlit as st
import streamlit.components.v1 as components
import time
import base64
import os

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch: Sirene", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(35%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(0, 0, 0, 0.6);
        backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(20px);
        border-radius: 30px; padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 5vh;
    }}
    .timer-display {{ font-size: 100px; font-weight: 100; font-family: monospace; margin: 10px; color: #fff; }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: white; color: black; font-weight: bold; border: none; padding: 12px; margin-top: 10px;
    }}
    header, footer {{ visibility: hidden !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo" poster="{POSTER_URL}">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- 2. LOGIK ---

if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    st.write("Stelle die Zeit ein. Die Sirene stoppt nur bei Vorbeuge!")
    c1, c2 = st.columns(2)
    with c1: mins = st.number_input("Minuten", 0, 60, 0)
    with c2: secs = st.number_input("Sekunden", 0, 59, 10)
    
    if st.button("Wecker scharf schalten"):
        st.session_state.total_seconds = (mins * 60) + secs
        st.session_state.phase = "COUNTDOWN"
        st.rerun()

else:
    t_placeholder = st.empty()
    
    if st.session_state.phase == "COUNTDOWN":
        for i in range(st.session_state.total_seconds, 0, -1):
            t_placeholder.markdown(f"<p class='timer-display'>{i}</p>", unsafe_allow_html=True)
            time.sleep(1)
        st.session_state.phase = "ALARM"
        st.rerun()

    if st.session_state.phase == "ALARM":
        t_placeholder.markdown(f"<p class='timer-display' style='color:#ff4b4b;'>0</p>", unsafe_allow_html=True)
        
        # Audio-Datei einlesen für das Iframe
        audio_html = ""
        if os.path.exists("sirene-da-monique.mp3"):
            with open("sirene-da-monique.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                audio_html = f"data:audio/mp3;base64,{b64}"

        js_code = f"""
        <div id="cam-root" style="text-align: center; color: white; font-family: sans-serif;">
            <div id="setup-area">
                <p style="font-size: 1.2em; margin-bottom: 20px;">⚠️ Zeit abgelaufen!</p>
                <button id="start-btn" style="padding: 20px 40px; border-radius: 50px; border: none; background: #ff4b4b; color: white; font-weight: bold; cursor: pointer; font-size: 18px; box-shadow: 0 4px 15px rgba(255,75,75,0.4);">
                    KLICKEN: Sirene stoppen & Übung starten
                </button>
            </div>
            
            <div id="capture-area" style="display: none;">
                <h2 id="hold-timer" style="font-size: 64px; margin: 10px 0; font-family: monospace;">30.0</h2>
                <div style="position: relative; display: inline-block; border: 2px solid white; border-radius: 20px; overflow: hidden; background: #000;">
                    <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1);" autoplay playsinline></video>
                </div>
                <p id="status" style="margin-top: 10px; font-size: 18px; color: #ff4b4b;">Beuge dich tief!</p>
                <div style="width: 100%; height: 12px; background: rgba(255,255,255,0.2); border-radius: 6px; overflow: hidden; margin-top: 10px;">
                    <div id="progress" style="width: 0%; height: 100%; background: #4CAF50; transition: width 0.1s linear;"></div>
                </div>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>

        <script>
            const startBtn = document.getElementById('start-btn');
            const setupArea = document.getElementById('setup-area');
            const captureArea = document.getElementById('capture-area');
            const video = document.getElementById('vid');
            const status = document.getElementById('status');
            const bar = document.getElementById('progress');
            const holdTimerDisplay = document.getElementById('hold-timer');
            
            const alarm = new Audio("{audio_html}");
            alarm.loop = true;

            let totalHeldMs = 0;
            let lastTimestamp = Date.now();
            const targetMs = 30000;
            let isFinished = false;

            startBtn.onclick = async () => {{
                // Dieser Klick gibt uns die Erlaubnis für Audio!
                setupArea.style.display = 'none';
                captureArea.style.display = 'block';
                
                // Audio sofort testen und abspielen
                alarm.play().catch(e => {{
                    console.log("Audio konnte nicht starten:", e);
                }});
                
                try {{
                    const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
                    pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});

                    pose.onResults(res => {{
                        if (isFinished) return;
                        const now = Date.now();
                        const deltaTime = now - lastTimestamp;
                        lastTimestamp = now;

                        if (res.poseLandmarks) {{
                            const lm = res.poseLandmarks;
                            const noseY = lm[0].y;
                            const hipY = (lm[23].y + lm[24].y) / 2;

                            if (noseY > hipY + 0.05) {{
                                alarm.pause(); 
                                totalHeldMs += deltaTime;
                                let remaining = (targetMs - totalHeldMs) / 1000;
                                if (remaining < 0) remaining = 0;
                                holdTimerDisplay.innerText = remaining.toFixed(1);
                                holdTimerDisplay.style.color = "#4CAF50";
                                bar.style.width = (totalHeldMs / targetMs * 100) + "%";
                                status.innerText = "Sirene pausiert... Halten!";
                                status.style.color = "#4CAF50";

                                if (totalHeldMs >= targetMs) {{
                                    isFinished = true;
                                    alarm.pause();
                                    status.innerText = "GESCHAFFT!";
                                    holdTimerDisplay.innerText = "✓";
                                }}
                            }} else {{
                                if (!isFinished) alarm.play().catch(() => {{}});
                                status.innerText = "TIEFER! Beuge dich!";
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
                }} catch (e) {{
                    status.innerText = "Fehler: " + e.message;
                }}
            }};
        </script>
        """
        components.html(js_code, height=600)

    if st.button("Neustart / Wecker abbrechen"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
