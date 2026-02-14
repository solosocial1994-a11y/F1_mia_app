import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 2026 Data Analysis", layout="wide")

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else [data]
        return None
    except: return None

def format_time(seconds):
    if pd.isna(seconds) or seconds <= 0: return "-"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

# --- SIDEBAR PER ARCHIVIO ---
st.sidebar.title("📚 Archivio 2026")
year = st.sidebar.selectbox("Stagione", [2026, 2025, 2024], index=0)
sessions = get_f1(f"sessions?year={year}")

if sessions:
    s_df = pd.DataFrame(sessions).sort_values('date_start', ascending=False)
    loc = st.sidebar.selectbox("Circuito", s_df['location'].unique())
    s_options = s_df[s_df['location'] == loc]
    s_name = st.sidebar.selectbox("Sessione", s_options['session_name'].unique())
    s_key = s_options[s_options['session_name'] == s_name]['session_key'].values[0]
else:
    st.stop()

# --- CARICAMENTO DATI PILOTI ---
drivers = get_f1(f"drivers?session_key={s_key}")
d_map = {str(d['driver_number']): {"name": d['broadcast_name'], "color": f"#{d['team_colour']}"} for d in drivers} if drivers else {}

st.title(f"📖 Analisi: {loc} ({year})")
st.info(f"Stai studiando i dati della sessione {s_name}. ID Sessione: {s_key}")

tab1, tab2, tab3 = st.tabs(["📊 Analisi Giri", "🏎️ Telemetria Media", "🎙️ Archivio Radio"])

with tab1:
    st.subheader("Tutti i Giri della Sessione")
    laps = get_f1(f"laps?session_key={s_key}")
    if laps:
        df_l = pd.DataFrame(laps)
        df_l['Pilota'] = df_l['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', x))
        df_l['Tempo'] = df_l['lap_duration'].apply(format_time)
        # Filtriamo solo i giri validi per l'analisi
        st.dataframe(df_l[['Pilota', 'lap_number', 'Tempo', 'stint']].sort_values(by=['lap_number'], ascending=False), use_container_width=True)
    else: st.write("Dati giri non trovati.")

with tab2:
    st.subheader("Telemetria Salvata (Primi 50 campioni)")
    # Per sessioni chiuse carichiamo i dati iniziali per studio
    car = get_f1(f"car_data?session_key={s_key}")
    if car:
        df_c = pd.DataFrame(car).head(50) # Carichiamo l'inizio per studio
        if 'driver_number' in df_c.columns:
            df_c['Pilota'] = df_c['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', x))
            cols = [c for c in ['Pilota', 'speed', 'rpm', 'n_gear', 'throttle'] if c in df_c.columns]
            st.table(df_c[cols])
    else: st.write("Dati telemetria archiviati non disponibili.")

with tab3:
    st.subheader("Comunicazioni Radio Registrate")
    radio = get_f1(f"team_radio?session_key={s_key}")
    if radio:
        st.write(f"Trovati {len(radio)} messaggi audio.")
        for r in radio[:10]: # Mostriamo i primi 10 per studio
            p_name = d_map.get(str(r['driver_number']), {}).get('name', f"Pilota {r['driver_number']}")
            st.audio(r['recording_url'])
            st.caption(f"Audio di: {p_name}")
    else: st.write("Nessun archivio audio per questa sessione.")
