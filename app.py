import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. DESIGN & BACKGROUND ---
st.set_page_config(page_title="ZenStretch: Sirenen-Modus", layout="centered")

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
        background: rgba(0, 0, 0, 0.65);
        backdrop-filter: blur(25px); -webkit-backdrop-filter: blur(20px);
        border-radius: 30px; padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 5vh;
    }}
    .timer-display {{ font-size: 100px; font-weight: 100; font-family: monospace; margin: 10px; color: #fff; }}
    header, footer {{ visibility: hidden !important; }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: white; color: black; font-weight: bold; border: none; padding: 12px; margin-top: 10px;
    }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo" poster="{POSTER_URL}">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- 2. PHASEN ---

if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    st.write("Stoppe die Sirene durch eine Vorbeuge!")
    c1, c2 = st.columns(2)
    with c1: mins = st.number_input("Minuten", 0, 60, 0)
    with c2: secs = st.number_input("Sekunden", 0, 59, 10)
    
    if st.button("Timer starten"):
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

        js_code = """
        <div id="cam-root" style="text-align: center; color: white; font-family: sans-serif;">
            <div id="setup-area">
                <button id="start-btn" style="padding: 15px 30px; border-radius: 30px; border: none; background: #ff4b4b; color: white; font-weight: bold; cursor: pointer; font-size: 16px;">
                    KLICKEN ZUM AKTIVIEREN (Sirene & Kamera)
                </button>
            </div>
            
            <div id="capture-area" style="display: none;">
                <h2 id="hold-timer" style="font-size: 64px; margin: 10px 0; font-family: monospace;">30.0</h2>
                <div style="position: relative; display: inline-block; border: 2px solid white; border-radius: 20px; overflow: hidden;">
                    <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1); background: #000;" autoplay playsinline></video>
                </div>
                <p id="status" style="margin-top: 10px; font-size: 18px; height: 24px;">Beuge dich nach unten!</p>
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
            
            // Audio laden
            const alarm = new Audio('sirene-da-monique.mp3');
            alarm.loop = true;

            let totalHeldMs = 0;
            let lastTimestamp = Date.now();
            const targetMs = 30000;
            let isFinished = false;

            startBtn.onclick = async () => {
                setupArea.style.display = 'none';
                captureArea.style.display = 'block';
                alarm.play(); // Sirene startet sofort
                
                try {
                    const pose = new Pose({locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
                    pose.setOptions({ modelComplexity: 0, minDetectionConfidence: 0.5 });

                    pose.onResults(res => {
                        if (isFinished) return;

                        const now = Date.now();
                        const deltaTime = now - lastTimestamp;
                        lastTimestamp = now;

                        if (res.poseLandmarks) {
                            const lm = res.poseLandmarks;
                            const noseY = lm[0].y;
                            const hipY = (lm[23].y + lm[24].y) / 2;

                            // Logik: Kopf tiefer als Hüfte
                            if (noseY > hipY + 0.05) {
                                alarm.pause(); // SIRENE PAUSIERT BEIM DEHNEN
                                totalHeldMs += deltaTime;
                                
                                let remaining = (targetMs - totalHeldMs) / 1000;
                                if (remaining < 0) remaining = 0;
                                
                                holdTimerDisplay.innerText = remaining.toFixed(1);
                                holdTimerDisplay.style.color = "#4CAF50";
                                bar.style.width = (totalHeldMs / targetMs * 100) + "%";
                                status.innerText = "Sirene gestoppt... Halten!";

                                if (totalHeldMs >= targetMs) {
                                    isFinished = true;
                                    alarm.pause();
                                    status.innerText = "FERTIG! Sirene dauerhaft aus.";
                                    holdTimerDisplay.innerText = "✓";
                                }
                            } else {
                                if (!isFinished) alarm.play(); // SIRENE SPIELT, WENN MAN NICHT DEHNT
                                status.innerText = "TIEFER! Beuge dich, um die Sirene zu stoppen!";
                                holdTimerDisplay.style.color = "#ff4b4b";
                            }
                        }
                    });

                    const camera = new Camera(video, {
                        onFrame: async () => { await pose.send({image: video}); },
                        width: 480, height: 360
                    });
                    await camera.start();
                } catch (e) {
                    status.innerText = "Fehler: " + e.message;
                }
            };
        </script>
        """
        components.html(js_code, height=600)

    if st.button("🔙 Zurück zum Start / Reset"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
