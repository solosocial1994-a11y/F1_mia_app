import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 2026 Ultimate", layout="wide")

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data: return None
        return data if isinstance(data, list) else [data]
    except: return None

def format_time(seconds):
    if pd.isna(seconds) or seconds <= 0: return "-"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

# --- SIDEBAR ---
st.sidebar.title("🏁 Comandi 2026")
year = st.sidebar.selectbox("Anno", [2026, 2025, 2024], index=0)
sessions = get_f1(f"sessions?year={year}")

if sessions:
    s_df = pd.DataFrame(sessions).sort_values('date_start', ascending=False)
    loc = st.sidebar.selectbox("Circuito", s_df['location'].unique())
    s_options = s_df[s_df['location'] == loc]
    s_name = st.sidebar.selectbox("Sessione", s_options['session_name'].unique())
    s_key = s_options[s_options['session_name'] == s_name]['session_key'].values[0]
else: st.stop()

# --- MAPPA PILOTI ---
drivers = get_f1(f"drivers?session_key={s_key}")
d_map = {str(d['driver_number']): {"name": d['broadcast_name'], "color": f"#{d['team_colour']}"} for d in drivers} if drivers else {}

st.title(f"🏎️ {loc}")

tab1, tab2, tab3, tab4 = st.tabs(["⏱️ Classifica", "📊 Telemetria", "📻 Radio", "🌦️ Meteo"])

with tab1:
    st.subheader("Classifica Tempi")
    laps = get_f1(f"laps?session_key={s_key}")
    if laps:
        df_l = pd.DataFrame(laps).tail(20)
        if 'driver_number' in df_l.columns:
            df_l['Pilota'] = df_l['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', x))
            df_l['Tempo'] = df_l['lap_duration'].apply(format_time)
            st.table(df_l[['Pilota', 'lap_number', 'Tempo']].rename(columns={'lap_number':'Giro'}))
    else: st.info("Nessun tempo disponibile.")

with tab2:
    st.subheader("Telemetria Live")
    car_data = get_f1(f"car_data?session_key={s_key}")
    if car_data:
        df_c = pd.DataFrame(car_data).tail(15)
        # Protezione colonne per evitare errori
        avail_cols = [c for c in ['driver_number', 'speed', 'rpm', 'n_gear', 'throttle'] if c in df_c.columns]
        df_display = df_c[avail_cols].copy()
        if 'driver_number' in df_display.columns:
            df_display['Pilota'] = df_display['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', x))
        st.dataframe(df_display, use_container_width=True)
    else: st.info("Dati telemetria non pervenuti.")

with tab3:
    st.subheader("Team Radio")
    radio_data = get_f1(f"team_radio?session_key={s_key}")
    if radio_data:
        for r in radio_data[-8:]: # Ultimi 8 messaggi
            p_info = d_map.get(str(r['driver_number']), {"name": f"Pilota {r['driver_number']}", "color": "#ccc"})
            st.markdown(f"<div style='border-left: 5px solid {p_info['color']}; padding-left: 10px;'><b>{p_info['name']}</b></div>", unsafe_allow_html=True)
            st.audio(r['recording_url'])
    else: st.info("Nessun audio radio trovato.")

with tab4:
    weather = get_f1(f"weather?session_key={s_key}")
    if weather:
        w = weather[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("Pista", f"{w.get('track_temperature', 'N/D')}°C")
        c2.metric("Aria", f"{w.get('air_temperature', 'N/D')}°C")
        c3.metric("Umidità", f"{w.get('humidity', 'N/D')}%")
