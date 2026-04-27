import streamlit as st
import streamlit.components.v1 as components
import time

# --- KONFIGURATION & BRANDING ---
st.set_page_config(page_title="ZenStretch Wecker", page_icon="🧘", layout="centered")

# --- PLACEHOLDER FÜR DEIN BILD ---
# Ersetze diesen Link durch den Pfad zu deinem Bild (z.B. auf GitHub gehostet oder ein Unsplash-Link)
# Das Bild sollte die Berge und den sitzenden Mönch darstellen.
BACKGROUND_IMAGE_URL = "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?q=80&w=2000" # Beispiel: Japanische Berge

# --- ULTIMATIVES ZEN-DESIGN (CSS) ---
st.markdown(f"""
    <style>
    /* Hintergrundbild für die gesamte App */
    .stApp {{
        background-image: url("{BACKGROUND_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* Alle Streamlit-Container transparent machen */
    .stDeployButton, .stDebugElement, header, .stToolbar {{
        display: none !important; /* Unnötige UI-Elemente verstecken */
    }}

    /* Hauptcontainer stylen: Schwebende, leicht transparente Karte */
    .block-container {{
        background-color: rgba(255, 255, 255, 0.6); /* Weiß mit 60% Deckkraft */
        backdrop-filter: blur(10px); /* Glas-Effekt */
        padding: 40px !important;
        border-radius: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-top: 50px;
        max_width: 700px;
    }}

    /* Typografie anpassen */
    h1 {{
        color: #2F4F4F; /* Dark Slate Gray */
        font-family: 'Amatic SC', cursive; /* Optional: Ein schöner Font, falls verfügbar */
        text-align: center;
        font-size: 3rem !important;
        font-weight: 400 !important;
    }}
    
    h3, .stMarkdown, p {{
        color: #4F4F4F;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }}

    /* Timer Text riesig und klar */
    .timer-text {{
        font-size: 100px !important;
        font-weight: 100; /* Sehr dünner Font für Zen-Look */
        color: #2F4F4F;
        text-align: center;
        margin: 20px 0;
        font-family: 'Helvetica Neue', sans-serif;
    }}

    /* Eingabefelder und Buttons verschönern */
    .stNumberInput div div input {{
        background-color: rgba(255,255,255,0.8) !important;
        border-radius: 15px !important;
        border: 1px solid #C0C0C0 !important;
        text-align: center;
    }}

    .stButton>button {{
        width: 100%;
        border-radius: 20px;
        background-color: #588157; /* Salbeigrün */
        color: white;
        border: none;
        padding: 12px;
        font-size: 1.1rem;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: #3A5A40;
        box-shadow: 0 5px 15px rgba(88,129,87,0.4);
    }}

    /* Warnungen sanfter gestalten */
    .stAlert {{
        background-color: rgba(255, 165, 0, 0.1) !important;
        color: #D2691E !important;
        border-radius: 15px;
        border: 1px solid rgba(255, 165, 0, 0.3);
    }}

    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Amatic+SC:wght@700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

# --- APP LOGIK (wie vorher, nur schöner verpackt) ---
if 'alarm_active' not in st.session_state:
    st.session_state.alarm_active = False

# Platz für das Logo oder ein Icon über dem Titel
st.markdown("<div style='text-align: center; font-size: 50px;'>🧘</div>", unsafe_allow_html=True)
st.title("ZenStretch")

# --- TIMER BEREICH ---
if not st.session_state.alarm_active:
    st.markdown("<h3>Stelle die Zeit bis zur Einkehr.</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        minutes = st.number_input("Minuten", min_value=0, max_value=60, value=0, key="min")
    with col2:
        seconds = st.number_input("Sekunden", min_value=0, max_value=59, value=10, key="sec")
    
    st.markdown("<br>", unsafe_allow_html=True) # Abstandhalter
    if st.button("In die Stille gehen"):
        total_seconds = minutes * 60 + seconds
        if total_seconds > 0:
            # Countdown Anzeige
            placeholder = st.empty()
            for i in range(total_seconds, 0, -1):
                placeholder.markdown(f"<p class='timer-text'>{i:02d}</p>", unsafe_allow_html=True)
                time.sleep(1)
            
            st.session_state.alarm_active = True
            st.rerun()
        else:
            st.error("Bitte stelle eine Zeit ein.")

# --- ALARM & DEHN BEREICH ---
if st.session_state.alarm_active:
    st.markdown("<h3 style='color: #bc4749;'>Die Stille endet. Zeit für Erhebung.</h3>", unsafe_allow_html=True)
    
    # Sanfter Gong als Alarm
    st.audio("https://cdn.pixabay.com/audio/2022/03/15/audio_206684742d.mp3", format="audio/mp3", autoplay=True, loop=True)

    # JavaScript Teil für die Kamera-Erkennung (mit Zen-Styling)
    js_code = """
    <div id="wrapper" style="text-align: center; font-family: 'Helvetica Neue', sans-serif;">
        <h2 id="js_status" style="color: #bc4749; font-weight: 300;">Bitte erhebe deine Arme.</h2>
        <div style="position: relative; display: inline-block;">
            <video id="input_video" style="width: 100%; max-width: 400px; border-radius: 20px; transform: scaleX(-1); border: 2px solid rgba(255,255,255,0.5); box-shadow: 0 10px 20px rgba(0,0,0,0.1);"></video>
            <canvas id="output_canvas" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"></canvas>
        </div>
        <div id="progress_bar" style="width: 100%; max-width: 400px; background: rgba(0,0,0,0.05); height: 10px; border-radius: 5px; margin: 20px auto 0 auto; overflow: hidden;">
            <div id="progress_fill" style="width: 0%; height: 100%; background: #588157; border-radius: 5px; transition: width 0.2s linear;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const statusText = document.getElementById('js_status');
        const progressFill = document.getElementById('progress_bar'); // Korrigiert: Zugriff auf das Fill-Element
        const videoElement = document.getElementById('input_video');
        const canvasElement = document.getElementById('output_canvas');
        const canvasCtx = canvasElement.getContext('2d');
        
        let counter = 0;
        const targetFrames = 150; // Etwa 8-10 Sekunden halten (flüssigerer Counter)
        let isFinished = false;

        function onResults(results) {
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
            
            if (results.poseLandmarks && !isFinished) {
                const landmarks = results.poseLandmarks;
                // Check: Hände (15, 16) über Augenbrauen (1, 4)
                const leftWristY = landmarks[15].y;
                const rightWristY = landmarks[16].y;
                const eyeY = (landmarks[1].y + landmarks[4].y) / 2;

                if (leftWristY < eyeY && rightWristY < eyeY) {
                    counter++;
                    let percent = (counter / targetFrames) * 100;
                    document.getElementById('progress_fill').style.width = percent + "%";
                    statusText.innerText = "Haltung eingenommen. Verweile...";
                    statusText.style.color = "#588157";
                    
                    if (counter >= targetFrames) {
                        isFinished = true;
                        statusText.innerText = "✅ Erhebung vollendet. Gehe in Frieden.";
                        statusText.style.color = "#2F4F4F";
                        setTimeout(() => { window.parent.location.reload(); }, 3000);
                    }
                } else {
                    if (counter > 0) counter -= 1; // Strafe fürs Abbrechen verdoppelt
                    document.getElementById('progress_fill').style.width = (counter / targetFrames) * 100 + "%";
                    statusText.innerText = "Bitte erhebe die Arme zum Gruße.";
                    statusText.style.color = "#bc4749";
                }
            }
            canvasCtx.restore();
        }

        const pose = new Pose({locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
        }});
        pose.setOptions({ modelComplexity: 1, minDetectionConfidence: 0.6 });
        pose.onResults(onResults);

        const camera = new Camera(videoElement, {
            onFrame: async () => { await pose.send({image: videoElement}); },
            width: 640, height: 480
        });
        camera.start();
    </script>
    """
    components.html(js_code, height=700)

    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("Notfall-Abbruch (Weltliche Verpflichtung)"):
        if st.button("Abbrechen"):
            st.session_state.alarm_active = False
            st.rerun()
            
