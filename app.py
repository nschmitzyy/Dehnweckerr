elif st.session_state.phase == "ALARM_READY":
    js_code = f"""
    <div id="root" style="text-align: center; color: white; font-family: sans-serif;">
        <div id="countdown-area">
            <p id="big-timer" style="font-size: 80px; font-weight: 100; font-family: monospace; margin: 20px 0;">00:00:00</p>
            <p id="hint" style="letter-spacing: 2px; opacity: 0.8;">BIS ZUM ALARM</p>
        </div>

        <div id="exercise-area" style="display: none;">
            <h2 style="color: #ff4b4b; margin: 0; letter-spacing: 5px;">🚨 ALARM 🚨</h2>
            <h2 id="hold-timer" style="font-size: 64px; margin: 10px 0; font-family: monospace;">30.0</h2>
            <div style="position: relative; display: inline-block; border: 2px solid white; border-radius: 20px; overflow: hidden; background: #000;">
                <video id="vid" style="width: 100%; max-width: 400px; transform: scaleX(-1);" autoplay playsinline></video>
            </div>
            <p id="status" style="margin-top: 10px; font-size: 18px; color: #ff4b4b; font-weight: bold;">BEUGE DICH NACH UNTEN!</p>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/pose/pose.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js"></script>

    <script>
        const bigTimer = document.getElementById('big-timer');
        const countdownArea = document.getElementById('countdown-area');
        const exerciseArea = document.getElementById('exercise-area');
        const holdTimerDisplay = document.getElementById('hold-timer');
        const status = document.getElementById('status');
        const video = document.getElementById('vid');

        const alarm = new Audio("{audio_html_src}");
        alarm.loop = true;

        let timeLeft = {st.session_state.total_seconds};
        let totalHeldMs = 0;
        let lastTimestamp = Date.now();

        function formatTime(s) {{
            const h = Math.floor(s / 3600);
            const m = Math.floor((s % 3600) / 60);
            const sec = s % 60;
            return [h, m, sec].map(v => v < 10 ? "0" + v : v).join(":");
        }}

        const mainInterval = setInterval(() => {{
            if (timeLeft > 0) {{
                timeLeft--;
                bigTimer.innerText = formatTime(timeLeft);
            }} else {{
                clearInterval(mainInterval);
                startAlarmMode();
            }}
        }}, 1000);
        bigTimer.innerText = formatTime(timeLeft);

        async function startAlarmMode() {{
            countdownArea.style.display = 'none';
            exerciseArea.style.display = 'block';
            alarm.play().catch(e => console.log("Audio Blocked"));
            startCamera();
        }}

        async function startCamera() {{
            const pose = new Pose({{locateFile: (f) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${{f}}` }});
            pose.setOptions({{ modelComplexity: 0, minDetectionConfidence: 0.5 }});

            pose.onResults(res => {{
                const now = Date.now();
                const delta = now - lastTimestamp;
                lastTimestamp = now;

                if (res.poseLandmarks) {{
                    const noseY = res.poseLandmarks[0].y;
                    const hipY = (res.poseLandmarks[23].y + res.poseLandmarks[24].y) / 2;

                    if (noseY > hipY + 0.05) {{
                        alarm.pause();
                        totalHeldMs += delta;
                        let rem = Math.max(0, (30000 - totalHeldMs) / 1000);
                        holdTimerDisplay.innerText = rem.toFixed(1);
                        holdTimerDisplay.style.color = "#4CAF50";
                        status.innerText = "Sirene pausiert...";
                        status.style.color = "#4CAF50";
                    }} else {{
                        if (totalHeldMs < 30000) alarm.play().catch(()=>{{}});
                        status.innerText = "TIEFER! BEUGE DICH!";
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
