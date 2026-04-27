import streamlit as st
import streamlit.components.v1 as components

# --- ZEN DESIGN ---
st.set_page_config(page_title="StretchWake JS", page_icon="🧘")

st.markdown("""
    <style>
    .main { background-color: #F0F4F2; color: #3A5A40; }
    .stApp { background-color: #F0F4F2; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧘 StretchWake")
st.subheader("Die KI läuft hier in deinem Browser – kein Server-Error!")

# --- UI CONTROLS ---
col1, col2 = st.columns(2)
with col1:
    st.info("1. Stell den Timer")
    duration = st.number_input("Sekunden dehnen:", min_value=5, value=10)
with col2:
    st.info("2. Starte die Kamera")
    start_btn = st.button("Kamera & Timer aktivieren")

# --- DER JAVASCRIPT-BLOCK (Die Magie) ---
# Dieser Teil lädt MediaPipe direkt im Frontend des Nutzers.
if start_btn:
    st.write(f"Halte deine Arme hoch, um den {duration}s Timer zu starten!")
    
    js_code = f"""
    <div style="position: relative;">
        <video id="input_video" style="width: 100%; border-radius: 15px; transform: scaleX(-1);"></video>
        <canvas id="output_canvas" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%;"></canvas>
        <h2 id="status" style="color: #588157; text-align: center;">Suche Pose...</h2>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils"></script>

    <script>
        const videoElement = document.getElementById('input_video');
        const canvasElement = document.getElementById('output_canvas');
        const canvasCtx = canvasElement.getContext('2d');
        const statusText = document.getElementById('status');
        
        let counter = 0;
        const targetSeconds = {duration};
        let finished = false;

        function onResults(results) {{
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);
            
            if (results.poseLandmarks) {{
                // Zeichne die Gelenke (Feedback für User)
                drawConnectors(canvasCtx, results.poseLandmarks, POSE_CONNECTIONS, {{color: '#A3B18A', lineWidth: 4}});
                drawLandmarks(canvasCtx, results.poseLandmarks, {{color: '#3A5A40', lineWidth: 2}});

                // Logik: Arme über Schulterhöhe (Einfacher Check)
                const leftWrist = results.poseLandmarks[15].y;
                const rightWrist = results.poseLandmarks[16].y;
                const nose = results.poseLandmarks[0].y;

                if (leftWrist < nose && rightWrist < nose && !finished) {{
                    counter++;
                    statusText.innerText = "Dehnung erkannt! Halten: " + Math.floor(counter/10) + "s";
                    
                    if (counter >= targetSeconds * 10) {{
                        statusText.innerText = "✅ GESCHAFFT! Du bist wach.";
                        statusText.style.color = "blue";
                        finished = true;
                        // Hier könnte ein Sound-Stop Signal kommen
                    }}
                }} else if (!finished) {{
                    statusText.innerText = "Hände über den Kopf zum Stoppen!";
                }}
            }}
            canvasCtx.restore();
        }}

        const pose = new Pose({{locateFile: (file) => {{
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{file}}`;
        }}}});

        pose.setOptions({{
            modelComplexity: 1,
            smoothLandmarks: true,
            minDetectionConfidence: 0.5,
            minTrackingConfidence: 0.5
        }});

        pose.onResults(onResults);

        const camera = new Camera(videoElement, {{
            onFrame: async () => {{
                await pose.send({{image: videoElement}});
            }},
            width: 640,
            height: 480
        }});
        camera.start();
    </script>
    """
    components.html(js_code, height=600)
