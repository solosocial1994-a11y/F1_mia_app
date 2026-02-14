import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 2026 Live", layout="wide")

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data: return None
        return data if isinstance(data, list) else [data]
    except: return None

# Funzione per rendere i tempi leggibili (es. 81.1 -> 1:21.100)
def format_time(seconds):
    if pd.isna(seconds): return "-"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

# --- SELEZIONE SESSIONE ---
st.sidebar.title("🏁 Centro Dati 2026")
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
d_map = {str(d['driver_number']): d['broadcast_name'] for d in drivers} if drivers else {}

st.title(f"🏎️ {loc}")

tab1, tab2, tab3 = st.tabs(["⏱️ Classifica", "📊 Telemetria", "🌦️ Meteo"])

with tab1:
    laps = get_f1(f"laps?session_key={s_key}")
    if laps:
        df_l = pd.DataFrame(laps).tail(20)
        df_l['Pilota'] = df_l['driver_number'].astype(str).map(d_map)
        # CONVERSIONE TEMPI
        df_l['Tempo'] = df_l['lap_duration'].apply(format_time)
        st.table(df_l[['Pilota', 'lap_number', 'Tempo']].rename(columns={'lap_number':'Giro'}))

with tab2:
    st.subheader("Dati Telemetria (Velocità/RPM)")
    car_data = get_f1(f"car_data?session_key={s_key}")
    if car_data and isinstance(car_data, list):
        df_c = pd.DataFrame(car_data).tail(15)
        df_c['Pilota'] = df_c['driver_number'].astype(str).map(d_map)
        # Mostriamo solo se le colonne esistono
        cols = [c for c in ['Pilota', 'speed', 'rpm', 'n_gear'] if c in df_c.columns]
        st.dataframe(df_c[cols], use_container_width=True)
    else:
        st.info("Dati telemetria non ancora disponibili per questa sessione.")

with tab3:
    weather = get_f1(f"weather?session_key={s_key}")
    if weather:
        w = weather[-1]
        st.metric("Pista", f"{w['track_temperature']}°C")
        st.metric("Aria", f"{w['air_temperature']}°C")
