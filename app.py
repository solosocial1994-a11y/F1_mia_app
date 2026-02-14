import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 2026 Analysis", layout="wide")

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        return data if isinstance(data, list) else [data]
    except: return None

def format_time(seconds):
    if pd.isna(seconds) or seconds <= 0: return "-"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

# --- ARCHIVIO ---
st.sidebar.title("📚 Studio Dati 2026")
year = st.sidebar.selectbox("Anno", [2026, 2025, 2024], index=0)
sessions = get_f1(f"sessions?year={year}")

if sessions:
    s_df = pd.DataFrame(sessions).sort_values('date_start', ascending=False)
    loc = st.sidebar.selectbox("Circuito", s_df['location'].unique())
    s_key = s_df[s_df['location'] == loc]['session_key'].values[0]
else: st.stop()

# --- FILTRO PILOTA ---
drivers = get_f1(f"drivers?session_key={s_key}")
d_map = {str(d['driver_number']): d['broadcast_name'] for d in drivers} if drivers else {}
# Qui puoi finalmente scegliere chi analizzare
sel_driver_name = st.sidebar.selectbox("Seleziona Pilota da Analizzare", list(d_map.values()))
sel_driver_num = [k for k, v in d_map.items() if v == sel_driver_name][0]

st.title(f"📖 Analisi {sel_driver_name}: {loc}")

tab1, tab2, tab3 = st.tabs(["⏱️ Cronologia Giri", "📊 Telemetria Studio", "🎙️ Radio Salva"])

with tab1:
    laps = get_f1(f"laps?session_key={s_key}&driver_number={sel_driver_num}")
    if laps:
        df_l = pd.DataFrame(laps)
        df_l['Tempo'] = df_l['lap_duration'].apply(format_time)
        # Protezione colonne: mostriamo solo quelle esistenti
        cols = [c for c in ['lap_number', 'Tempo', 'stint', 'pitting'] if c in df_l.columns]
        st.dataframe(df_l[cols].sort_values('lap_number', ascending=False), use_container_width=True)
    else: st.info("Nessun giro trovato per questo pilota.")

with tab2:
    # Telemetria specifica del pilota scelto
    car = get_f1(f"car_data?session_key={s_key}&driver_number={sel_driver_num}")
    if car:
        df_c = pd.DataFrame(car).head(100)
        cols_tel = [c for c in ['speed', 'rpm', 'n_gear', 'throttle'] if c in df_c.columns]
        st.write(f"Dati telemetria per {sel_driver_name}")
        st.line_chart(df_c['speed'] if 'speed' in df_c.columns else [])
        st.dataframe(df_c[cols_tel], use_container_width=True)
    else: st.info("Telemetria non disponibile.")

with tab3:
    radio = get_f1(f"team_radio?session_key={s_key}&driver_number={sel_driver_num}")
    if radio:
        for r in radio[-10:]:
            st.audio(r['recording_url'])
            st.caption(f"Giro: {r.get('lap_number', 'N/D')}")
    else: st.info("Nessun audio trovato per questo pilota.")
