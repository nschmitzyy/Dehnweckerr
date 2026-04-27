import streamlit as st
import streamlit.components.v1 as components
import time

# --- 1. GRUNDKONFIGURATION ---
st.set_page_config(page_title="ZenStretch", layout="centered")

# Dein verifizierter Direkt-Link
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

# --- 2. CSS & VIDEO HINTERGRUND ---
# Wir nutzen hier einen etwas anderen CSS-Ansatz, um das Video zu "erzwingen"
st.markdown(f"""
    <style>
    /* Das Video-Element wird fixiert */
    #bgVideo {{
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%; 
        min-height: 100%;
        width: auto;
        height: auto;
        z-index: -1000;
        background-size: cover;
        object-fit: cover;
        filter: brightness(50%); /* Dunkler für bessere Lesbarkeit */
    }}

    /* Streamlit-Oberfläche transparent machen */
    .stApp {{
        background: transparent !important;
    {{

    /* Die zentrale Glas-Karte */
    .block-container {{
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 40px !important;
        margin-top: 5vh;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}

    /* Alle Texte weiß und schattiert */
    h1, h2, h3, p, label {{
        color: white !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.7);
        text-align: center;
    }}

    .big-timer {{
        font-size: 100px !important;
        font-weight: 100;
        color: white;
    }}

    /* Buttons stylen */
    .stButton>button {{
        width: 100%;
        border-radius: 50px;
        background: white;
        color: black;
        font-weight: bold;
        border: none;
        padding: 10px 20px;
    }}
    </style>

    <video autoplay muted loop playsinline id="bgVideo">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- 3. APP LOGIK (State-basiert) ---
if 'phase' not in st.session_state:
    st.session_state.phase = "EINSTELLEN"

st.markdown("<h1>🧘 ZenStretch</h1>", unsafe_allow_html=True)

# PHASE: SETUP
if st.session_state.phase == "EINSTELLEN":
    st.markdown("<h3>Wann möchtest du geweckt werden?</h3>", unsafe_allow_html=True)
    sek = st.number_input("Sekunden einstellen", 5, 600, 10)
    
    if st.button("Timer aktivieren"):
        st.session_state.countdown = sek
        st.session_state.phase = "COUNTDOWN"
        st.rerun()

# PHASE: COUNTDOWN
elif st.session_state.phase == "COUNTDOWN":
    display = st.empty()
    for i in range(st.session_state.countdown, 0, -1):
        display.markdown(f"<p class='big-timer'>{i}</p>", unsafe_allow_html=True)
        time.sleep(1)
    st.session_state.phase = "ALARM"
    st.rerun()

# PHASE: ALARM & POSE-CHECK
elif st.session_state.phase == "ALARM":
    st.markdown("<h3>Zeit für die Morgen-Dehnung!</h3>", unsafe_allow_html=True)
    
    # Der Gong
    st.audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3", autoplay=True)

    # Pose-Erkennung Interface
    js_interface = """
    <div style="text-align: center;">
        <div style="position: relative; display: inline-block; border: 3px solid white; border-radius: 20px; overflow: hidden;">
            <video id="v" style="width: 100%; max-width: 400px; transform: scaleX(-1);"></video>
            <canvas id="c" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"></canvas>
        </div>
        <p id="stat" style="color: white; font-size: 20px; margin-top: 10px;">Arme über den Kopf!</p>
        <div id="prog-bg" style="width: 100%; height: 10px; background: rgba(255,255,255,0.2); border-radius: 5px;">
            <div id="prog-fill" style="width: 0%; height: 100%; background: white; border-radius: 5px; transition: 0.2s;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const v = document.getElementById('v');
        const fill = document.getElementById('prog-fill');
        const stat = document.getElementById('stat');
        let count = 0;

        const pose = new Pose({locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${f}`});
        pose.setOptions({modelComplexity: 1, minDetectionConfidence: 0.5});

        pose.onResults(res => {
            if (res.poseLandmarks) {
                const lm = res.poseLandmarks;
                // Handgelenke (15, 16) vs Nase (0)
                if (lm[15].y < lm[0].y && lm[16].y < lm[0].y) {
                    count++;
                    fill.style.width = (count/80*100) + "%";
                    stat.innerText = "Haltung erkannt!";
                    if (count >= 80) {
                        stat.innerText = "Fertig!";
                        setTimeout(() => window.parent.location.reload(), 1500);
                    }
                }
            }
        });

        const cam = new Camera(v, {onFrame: async () => await pose.send({image: v}), width: 640, height: 480});
        cam.start();
    </script>
    """
    components.html(js_interface, height=550)

    if st.button("Reset"):
        st.session_state.phase = "EINSTELLEN"
        st.rerun()
