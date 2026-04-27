import streamlit as st
import streamlit.components.v1 as components
import time

# --- ZEN DESIGN ---
st.set_page_config(page_title="StretchWake", page_icon="🧘")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9F5; }
    .timer-text { 
        font-size: 80px !important; 
        font-weight: bold; 
        color: #588157; 
        text-align: center; 
        margin-top: 50px;
    }
    .status-msg { text-align: center; font-family: sans-serif; color: #3A5A40; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧘 StretchWake")

# Session State initialisieren, um den Status zu speichern
if 'alarm_active' not in st.session_state:
    st.session_state.alarm_active = False

# --- TIMER BEREICH ---
if not st.session_state.alarm_active:
    st.write("Stelle deinen Timer. Sobald er abläuft, musst du dich dehnen.")
    minutes = st.number_input("Minuten", min_value=0, max_value=60, value=0)
    seconds = st.number_input("Sekunden", min_value=0, max_value=59, value=10)
    
    if st.button("Timer starten ⏰"):
        total_seconds = minutes * 60 + seconds
        
        # Countdown Anzeige
        placeholder = st.empty()
        for i in range(total_seconds, 0, -1):
            placeholder.markdown(f"<p class='timer-text'>{i:02d}s</p>", unsafe_allow_html=True)
            time.sleep(1)
        
        st.session_state.alarm_active = True
        st.rerun()

# --- ALARM & DEHN BEREICH ---
if st.session_state.alarm_active:
    st.warning("⚠️ ALARM! Zeit zum Dehnen! Der Alarm stoppt erst, wenn du dich dehnst.")
    
    # Optional: Ein Audio-Element, das den Wecker spielt
    # Du kannst hier einen Link zu einer MP3-Datei einfügen
    st.audio("https://www.soundjay.com/buttons/beep-01a.mp3", format="audio/mp3", autoplay=True, loop=True)

    # JavaScript Teil für die Kamera-Erkennung
    js_code = """
    <div id="wrapper" style="text-align: center; font-family: sans-serif;">
        <h2 id="js_status" style="color: #bc4749;">BITTE ARME HOCH!</h2>
        <div style="position: relative; display: inline-block;">
            <video id="input_video" style="width: 100%; max-width: 500px; border-radius: 15px; transform: scaleX(-1); border: 5px solid #A3B18A;"></video>
            <canvas id="output_canvas" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"></canvas>
        </div>
        <div id="progress_bar" style="width: 100%; background: #ddd; height: 20px; border-radius: 10px; margin-top: 10px;">
            <div id="progress_fill" style="width: 0%; height: 100%; background: #588157; border-radius: 10px; transition: width 0.3s;"></div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const statusText = document.getElementById('js_status');
        const progressFill = document.getElementById('progress_fill');
        const videoElement = document.getElementById('input_video');
        const canvasElement = document.getElementById('output_canvas');
        const canvasCtx = canvasElement.getContext('2d');
        
        let counter = 0;
        const targetFrames = 100; // Etwa 5-10 Sekunden halten
        let isFinished = false;

        function onResults(results) {
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
            
            if (results.poseLandmarks && !isFinished) {
                const landmarks = results.poseLandmarks;
                // Check: Handgelenke (15, 16) müssen höher sein als die Nase (0)
                const leftWristY = landmarks[15].y;
                const rightWristY = landmarks[16].y;
                const noseY = landmarks[0].y;

                if (leftWristY < noseY && rightWristY < noseY) {
                    counter++;
                    let percent = (counter / targetFrames) * 100;
                    progressFill.style.width = percent + "%";
                    statusText.innerText = "Hervorragend! Halten...";
                    statusText.style.color = "#588157";
                    
                    if (counter >= targetFrames) {
                        isFinished = true;
                        statusText.innerText = "✅ WEG FREI! Du bist wach.";
                        // Hier stoppen wir das Audio (durch Neuladen der Seite via Streamlit)
                        setTimeout(() => { window.parent.location.reload(); }, 2000);
                    }
                } else {
                    if (counter > 0) counter -= 0.5; // Strafe fürs Abbrechen
                    progressFill.style.width = (counter / targetFrames) * 100 + "%";
                    statusText.innerText = "ARME HOCH ZUM STOPPEN!";
                    statusText.style.color = "#bc4749";
                }
                
                drawConnectors(canvasCtx, landmarks, POSE_CONNECTIONS, {color: '#A3B18A', lineWidth: 2});
            }
            canvasCtx.restore();
        }

        const pose = new Pose({locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
        }});
        pose.setOptions({ modelComplexity: 1, minDetectionConfidence: 0.5 });
        pose.onResults(onResults);

        const camera = new Camera(videoElement, {
            onFrame: async () => { await pose.send({image: videoElement}); },
            width: 640, height: 480
        });
        camera.start();
    </script>
    """
    components.html(js_code, height=700)

    if st.button("Notfall-Reset"):
        st.session_state.alarm_active = False
        st.rerun()
