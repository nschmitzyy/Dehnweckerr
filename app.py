import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import json
from datetime import datetime
import pandas as pd

# --- 1. DATENVERWALTUNG ---
LOG_FILE = "study_log.json"

def load_data():
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                return json.load(f)
        except: return []
    return []

def save_study_session(minutes, summary):
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    data.append({
        "date": today, 
        "minutes": round(minutes, 1),
        "summary": summary
    })
    with open(LOG_FILE, "w") as f:
        json.dump(data, f)

# --- 2. CONFIG & STYLE ---
st.set_page_config(page_title="ZenStretch", layout="centered")

# CSS bleibt gleich (gekürzt für Übersicht)
st.markdown("""
    <style>
    /* ... dein bisheriges CSS ... */
    .summary-box { background: rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'phase' not in st.session_state:
    st.session_state.phase = "SETUP"

# --- 3. LOGIK ---
if st.session_state.phase == "SETUP":
    st.title("🧘 ZenStretch")
    
    # STATISTIK & RECAP
    raw_data = load_data()
    if raw_data:
        df = pd.DataFrame(raw_data)
        st.subheader("Deine Lern-Fortschritte")
        df['date_only'] = pd.to_datetime(df['date']).dt.date
        stats = df.groupby('date_only')['minutes'].sum()
        st.bar_chart(stats, height=150)
        
        with st.expander("Letzte Recaps ansehen"):
            for entry in reversed(raw_data[-5:]): # Zeige die letzten 5
                st.markdown(f"**{entry['date']}** ({entry['minutes']} min):")
                st.info(entry['summary'] if entry['summary'] else "Kein Recap geschrieben.")
    
    st.markdown("---")
    stretch_choice = st.radio("Wähle deine Pose:", ["Vorbeuge (Rücken & Beine)", "Herabschauender Hund (Bloodflow)"])
    
    col1, col2, col3 = st.columns(3)
    hrs = col1.number_input("Std", 0, 23, 0)
    mins = col2.number_input("Min", 0, 59, 20)
    secs = col3.number_input("Sek", 0, 59, 0)
    
    if st.button("SCHARF SCHALTEN"):
        st.session_state.total_seconds = (hrs * 3600) + (mins * 60) + secs
        st.session_state.mode = "DOG" if "Hund" in stretch_choice else "FORWARD"
        st.session_state.current_minutes = (hrs * 60) + mins + (secs / 60)
        st.session_state.phase = "ALARM_READY"
        st.rerun()

elif st.session_state.phase == "ALARM_READY":
    # JS Code für Timer und Kamera (wie zuvor)
    # WICHTIG: Wenn stretchMs >= 30000, setzen wir eine neue Phase in Streamlit
    components.html(f"""
        <!-- ... dein kompletter Kamera/Pose JS Code von oben ... -->
        <script>
            // Wenn fertig:
            // window.parent.document.dispatchEvent(new CustomEvent('stretch_done'));
        </script>
    """, height=500)
    
    # Als simpler Workflow: Nach dem Dehnen erscheint dieses Menü:
    st.success("Dehnen abgeschlossen! Zeit für ein kurzes Recap:")
    recap_text = st.text_area("Was hast du in dieser Session gelernt?", placeholder="Themen, Formeln, Erkenntnisse...")
    
    if st.button("SESSION SPEICHERN & BEENDEN"):
        save_study_session(st.session_state.current_minutes, recap_text)
        st.session_state.phase = "SETUP"
        st.rerun()

    if st.button("Abbrechen (ohne Speichern)", type="secondary"):
        st.session_state.phase = "SETUP"
        st.rerun()
