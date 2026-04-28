import streamlit as st
import streamlit.components.v1 as components
import time

# --- SETUP ---
st.set_page_config(page_title="ZenStretch", layout="centered")

# Dein Direkt-Link
VIDEO_URL = "https://raw.githubusercontent.com/nschmitzyy/dehnweckerr/main/247740_medium.mp4"

# --- DER ULTIMATIVE HINTERGRUND-HACK ---
# Wir schreiben das CSS so, dass es ALLES in Streamlit transparent macht
st.markdown(f"""
    <style>
    /* Das Video-Element direkt in den Body zwingen */
    .stApp {{
        background: url("") !important; /* Entfernt Standard-Hintergrund */
    }}
    
    #video-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        object-fit: cover;
        z-index: -1;
        filter: brightness(40%);
    }}

    /* Die Glas-Box zentrieren */
    .main-box {{
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 30px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        text-align: center;
        margin-top: 50px;
        font-family: sans-serif;
    }}
    
    /* Verstecke Streamlit UI Reste */
    header, footer {{visibility: hidden !important;}}
    .stDeployButton {{display:none;}}
    </style>

    <video autoplay muted loop playsinline id="video-bg">
        <source src="{VIDEO_URL}" type="video/mp4">
    </video>
    """, unsafe_allow_html=True)

# --- APP STRUKTUR ---
# Wir packen alles in einen div "main-box", den wir oben gestylt haben
st.markdown('<div class="main-box">', unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "START"

st.title("🧘 ZenStretch")

if st.session_state.phase == "START":
    st.write("Wähle deine Zeit für die Ruhe.")
    sek = st.number_input("Sekunden", 5, 300, 10)
    if st.button("Timer starten"):
        st.session_state.timer = sek
        st.session_state.phase = "COUNT"
        st.rerun()

elif st.session_state.phase == "COUNT":
    display = st.empty()
    for i in range(st.session_state.timer, 0, -1):
        display.markdown(f"<h1 style='font-size: 80px;'>{i}</h1>", unsafe_allow_html=True)
        time.sleep(1)
    st.session_state.phase = "ALARM"
    st.rerun()

elif st.session_state.phase == "ALARM":
    st.write("Erhebe dich!")
    st.audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3", autoplay=True)
    
    # Einfaches Kamera-Test-Fenster (MediaPipe)
    components.html("""
        <div style="text-align:center;">
            <video id="web" style="width:90%; border-radius:20px; transform:scaleX(-1);" autoplay playsinline></video>
        </div>
        <script>
            navigator.mediaDevices.getUserMedia({video: true}).then(s => {
                document.getElementById('web').srcObject = s;
            });
        </script>
    """, height=400)
    
    if st.button("Fertig"):
        st.session_state.phase = "START"
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
