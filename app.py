import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 2026 Lab", layout="wide")

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
st.sidebar.title("🔬 Studio Test 2026")
year = st.sidebar.selectbox("Anno", [2026, 2025, 2024], index=0)
sessions = get_f1(f"sessions?year={year}")

if not sessions:
    st.error("Dati non disponibili per quest'anno.")
    st.stop()

s_df = pd.DataFrame(sessions).sort_values('date_start', ascending=False)
loc = st.sidebar.selectbox("Circuito", s_df['location'].unique())
s_key = s_df[s_df['location'] == loc]['session_key'].values[0]

# --- RECUPERO PILOTI (Protetto) ---
drivers_raw = get_f1(f"drivers?session_key={s_key}")
d_map = {str(d['driver_number']): d['broadcast_name'] for d in drivers_raw} if drivers_raw else {}

if not d_map:
    st.warning("Nessun pilota trovato per questa sessione.")
    st.stop()

# Selezione pilota con controllo di sicurezza
sel_driver_name = st.sidebar.selectbox("Scegli Pilota", list(d_map.values()))
# Risolviamo l'IndexError con una ricerca sicura
sel_driver_num = next((k for k, v in d_map.items() if v == sel_driver_name), None)

if not sel_driver_num:
    st.error("Errore nella selezione del pilota.")
    st.stop()

st.title(f"📊 Analisi: {sel_driver_name}")
st.caption(f"Circuito: {loc} | Sessione ID: {s_key}")

tab1, tab2, tab3 = st.tabs(["⏱️ Tempi sul Giro", "📈 Telemetria", "📻 Radio"])

with tab1:
    laps = get_f1(f"laps?session_key={s_key}&driver_number={sel_driver_num}")
    if laps:
        df_l = pd.DataFrame(laps)
        df_l['Tempo'] = df_l['lap_duration'].apply(format_time)
        cols = [c for c in ['lap_number', 'Tempo', 'stint', 'compound'] if c in df_l.columns]
        st.dataframe(df_l[cols].sort_values('lap_number', ascending=False), use_container_width=True)
    else: st.info("Nessun giro registrato per questo pilota.")

with tab2:
    st.subheader("Analisi Velocità")
    car = get_f1(f"car_data?session_key={s_key}&driver_number={sel_driver_num}")
    if car:
        df_c = pd.DataFrame(car).tail(200) # Più dati per lo studio
        if 'speed' in df_c.columns:
            st.line_chart(df_c['speed'])
            st.write("Dati medi: Speed:", int(df_c['speed'].mean()), "km/h")
    else: st.info("Telemetria non disponibile.")

with tab3:
    radio = get_f1(f"team_radio?session_key={s_key}&driver_number={sel_driver_num}")
    if radio:
        for r in radio[-10:]:
            st.audio(r['recording_url'])
            st.caption(f"Giro: {r.get('lap_number', 'N/D')}")
    else: st.info("Nessun audio radio salvato.")
