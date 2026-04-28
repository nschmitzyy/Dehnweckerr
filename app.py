import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch Pro", layout="centered")

VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"
POSTER_URL = "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&q=80&w=1000"

st.markdown(f"""
    <style>
    #bgVideo {{
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: -1; object-fit: cover; filter: brightness(40%);
        background: url({POSTER_URL}) center/cover no-repeat;
    }}
    .stApp {{ background: transparent !important; }}
    .main-card {{
        background: rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 30px; padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: white; text-align: center; margin-top: 10vh;
    }}
    .timer-display {{ font-size: 80px; font-weight: 100; color: white; margin: 20px; }}
    h1, h3, p, label {{ color: white !important; text-shadow: 2px 2px 8px rgba(0,0,0,0.5); }}
    .stButton>button {{
        width: 100%; border-radius: 50px; background: white; color: black;
        font-weight: bold; border: none; padding: 12px; transition: 0.3s;
    }}
    .stButton>button:hover {{ transform: scale(1.02); background: #eee; }}
    header, footer {{ visibility: hidden !important; }}
    </style>
    <video autoplay muted loop playsinline id="bgVideo" poster="{POSTER_URL}">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 2. STATE MANAGEMENT ---
if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

st.markdown('<div class="main-card">', unsafe_allow_html=True)

# --- 3. PHASEN ---

# PHASE: SETUP
if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    st.write("Wähle die Zeit bis zum Erwachen:")
    
    col1, col2 = st.columns(2)
    with col1:
        mins = st.number_input("Minuten", 0, 60, 0)
    with col2:
        secs = st.number_input("Sekunden", 0, 59, 10)
    
    if st.button("Timer aktivieren"):
        st.session_state.total_seconds = (mins * 60) + secs
        st.session_state.phase = "RUNNING"
        st.rerun()

# PHASE: RUNNING (Countdown & KI-Preload)
elif st.session_state.phase == "RUNNING":
    js_code = f"""
    <div style="text-align: center; color: white; font-family: sans-serif;">
        <h1 id="timer-ui" style="font-size: 100px; font-weight: 100;">{st.session_state.total_seconds}</h1>
        <div id="cam-area" style="display: none; opacity: 0; transition: opacity 1s;">
            <div style="position: relative; display: inline-block;">
                <video id="webcam" style="width: 100%; max-width: 400px; border-radius: 20px; transform: scaleX(-1);" autoplay playsinline></video>
                <canvas id="out" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></canvas>
            </div>
            <h2 id="msg" style="margin-top: 15px; font-weight: 300;">Arme hoch zum Stoppen!</h2>
            <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.2); border-radius: 4px; overflow: hidden;">
                <div id="bar" style="width: 0%; height: 100%; background: white; transition: 0.2s;"></div>
            </div>
        </div>
        <p id="info">KI wird im Hintergrund kalibriert...</p>
    </div>

    <script type="module">
        import {{ Pose }} from "https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js";
        import {{ Camera }} from "https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js";

        const timerUi = document.getElementById('timer-ui');
        const camArea = document.getElementById('cam-area');
        const info = document.getElementById('info');
        const bar = document.getElementById('bar');
        const msg = document.getElementById('msg');
        const video = document.getElementById('webcam');
        
        let timeLeft = {st.session_state.total_seconds};
        let counter = 0;
        let lastTime = 0;
        const fpsLimit = 12; // Performance-Turbo: Nur 12 Bilder pro Sekunde

        const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
        pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
        
        pose.onResults(res => {{
            if (timeLeft <= 0 && res.poseLandmarks) {{
                const lm = res.poseLandmarks;
                // Check: Hände über Nase
                if (lm[15].y < lm[0].y && lm[16].y < lm[0].y) {{
                    counter++;
                    bar.style.width = (counter / 1.5) + "%"; 
                    if (counter >= 150) {{
                        // Signal an Streamlit: Fertig
                        window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'FINISHED'}}, '*');
                    }}
                }}
            }}
        }});

        const camera = new Camera(video, {{
            onFrame: async () => {{
                const now = Date.now();
                if (now - lastTime >= (1000 / fpsLimit)) {{
                    lastTime = now;
                    await pose.send({{image: video}});
                }}
            }},
            width: 480, height: 360
        }});
        camera.start();

        const countdown = setInterval(() => {{
            timeLeft--;
            if (timeLeft > 0) {{
                timerUi.innerText = timeLeft;
            }} else {{
                clearInterval(countdown);
                timerUi.style.display = 'none';
                info.style.display = 'none';
                camArea.style.display = 'block';
                setTimeout(() => camArea.style.opacity = '1', 50);
                
                const alarm = new Audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3");
                alarm.loop = true;
                alarm.play();
                window.alarmAudio = alarm;
            }}
        }}, 1000);
    </script>
    """
    # Wir fangen das Signal von JS ab, um die Phase zu wechseln
    res = components.html(js_code, height=600)
    
    # Da wir in Streamlit die Rückgabe schwer direkt fangen, nutzen wir einen Button als Fallback oder Reset
    if st.button("Abbrechen / Reset"):
        st.session_state.phase = "SETUP"
        st.rerun()

    # Kleiner Trick: Wir prüfen ob die Zeit abgelaufen ist und bieten einen "Ich bin fertig" Button an,
    # falls das JS-Signal im Browser-Sandboxing hängen bleibt.
    if st.button("Manuell Beenden (nach Übung)"):
        st.session_state.phase = "SUCCESS"
        st.rerun()

# PHASE: SUCCESS
elif st.session_state.phase == "SUCCESS":
    st.title("✨ Erwacht")
    st.write("Du hast die Übung erfolgreich abgeschlossen. Dein Geist ist nun klar.")
    st.markdown("<div style='font-size: 50px;'>🙏</div>", unsafe_allow_html=True)
    
    if st.button("Neuen Wecker stellen"):
        st.session_state.phase = "SETUP"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
