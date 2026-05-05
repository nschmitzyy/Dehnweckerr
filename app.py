elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 80px; font-weight: 100; font-family: monospace;">00:00:00</p>
            <p>LERNPHASE AKTIV...</p>
        </div>
        <div id="exercise-area" style="display: none;">
            <h2 style="color: #ff4b4b;">🚨 ZEIT ZUM DEHNEN! 🚨</h2>
            <h2 id="hold-timer" style="font-size: 64px; font-family: monospace;">30.0</h2>
            <div style="position: relative; display: inline-block;">
                <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1); border-radius: 20px; border: 2px solid white;" autoplay playsinline></video>
                <button onclick="switchCamera()" style="position: absolute; bottom: 10px; right: 10px; background: rgba(0,0,0,0.5); color: white; border: none; border-radius: 5px; padding: 10px; cursor: pointer;">🔄</button>
            </div>
            <p id="status" style="margin-top: 10px; font-size: 20px; font-weight: bold;"></p>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>
    <script>
        const mode = "{st.session_state.mode}";
        const alarm = new Audio("{audio_html_src}"); alarm.loop = true;
        let timeLeft = {st.session_state.total_seconds};
        let stretchMs = 0; let lastTs = Date.now();
        let currentFacingMode = "user";
        let cameraObj = null;

        const timerInt = setInterval(() => {{
            if (timeLeft > 0) {{
                timeLeft--;
                document.getElementById('big-timer').innerText = new Date(timeLeft * 1000).toISOString().substr(11, 8);
            }} else {{
                clearInterval(timerInt);
                document.getElementById('countdown-area').style.display = 'none';
                document.getElementById('exercise-area').style.display = 'block';
                alarm.play(); startCamera();
            }}
        }}, 1000);

        async function startCamera() {{
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});
            pose.onResults(res => {{
                const now = Date.now(); const dt = now - lastTs; lastTs = now;
                if (!res.poseLandmarks) return;
                const noseY = res.poseLandmarks[0].y;
                const avgHipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;
                
                let isStretching = (mode === "FORWARD") ? (noseY > avgHipY + 0.05) : (avgHipY < noseY - 0.1);

                if (isStretching) {{
                    alarm.pause(); stretchMs += dt;
                    let rem = Math.max(0, (30000 - stretchMs) / 1000);
                    document.getElementById('hold-timer').innerText = rem.toFixed(1);
                    document.getElementById('hold-timer').style.color = "#4CAF50";
                    document.getElementById('status').innerText = "Perfekt! Halten...";
                }} else {{
                    if (stretchMs < 30000) alarm.play();
                    document.getElementById('hold-timer').style.color = "#ff4b4b";
                    document.getElementById('status').innerText = mode === "FORWARD" ? "TIEFER BEUGEN!" : "HÜFTE HÖHER!";
                }}
            }});
            
            try {{
                if (cameraObj) await cameraObj.stop();
                cameraObj = new Camera(document.getElementById('vid'), {{
                    onFrame: async () => {{ await pose.send({{image: document.getElementById('vid')}}); }},
                    width: 1280, height: 720, facingMode: currentFacingMode
                }});
                await cameraObj.start();
            }} catch (err) {{
                console.error("Kamerafehler:", err);
                document.getElementById('status').innerText = "Kamera-Zugriff verweigert!";
            }}
        }}

        function switchCamera() {{
            currentFacingMode = (currentFacingMode === "user") ? "environment" : "user";
            document.getElementById('vid').style.transform = (currentFacingMode === "user") ? "scaleX(-1)" : "scaleX(1)";
            startCamera();
        }}
    </script>
    """
    # HIER IST DIE WICHTIGE ÄNDERUNG: allow="camera"
    components.html(js_code, height=600, allow="camera")
    
    if st.button("DEHNEN FERTIG -> RECAP"):
        st.session_state.phase = "RECAP"
        st.rerun()
