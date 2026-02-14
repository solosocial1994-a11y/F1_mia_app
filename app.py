import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 Live Dashboard", layout="wide")

# --- FUNZIONI DI SUPPORTO ---
def get_data(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except: return None

# --- SIDEBAR: SELEZIONE EVENTO ---
st.sidebar.title("🏁 Menu F1")

# 1. Scegli l'Anno
year = st.sidebar.selectbox("Seleziona Anno", [2024, 2023], index=0)

# 2. Scegli la Gara (Location)
all_sessions = get_data(f"sessions?year={year}")
if all_sessions:
    # Creiamo una lista di nomi unici delle piste
    locations = sorted(list(set([s['location'] for s in all_sessions])))
    selected_loc = st.sidebar.selectbox("Seleziona Circuito", locations)
    
    # 3. Scegli la Sessione (Gara, Qualifiche, FP1...)
    session_options = [s for s in all_sessions if s['location'] == selected_loc]
    session_names = {s['session_name']: s['session_key'] for s in session_options}
    selected_session_name = st.sidebar.selectbox("Tipo Sessione", list(session_names.keys()))
    s_key = session_names[selected_session_name]
else:
    st.error("Errore nel caricamento dei calendari.")
    st.stop()

st.title(f"🏎️ {selected_loc}: {selected_session_name}")

# --- RECUPERO DATI PILOTI (Per trasformare i numeri in Nomi) ---
drivers_list = get_data(f"drivers?session_key={s_key}")
driver_map = {}
if drivers_list:
    # Creiamo un "dizionario" per tradurre il numero (es. 16) in Nome (Leclerc)
    driver_map = {str(d['driver_number']): d['broadcast_name'] for d in drivers_list}

# --- TAB INTERFACCIA ---
tab1, tab2, tab3 = st.tabs(["📊 Classifica & Tempi", "📻 Radio Live", "🌦️ Meteo"])

with tab1:
    st.header("Tempi sul Giro")
    laps = get_data(f"laps?session_key={s_key}")
    if laps:
        df_laps = pd.DataFrame(laps)
        # TRADUZIONE: Sostituiamo il numero col nome del pilota
        df_laps['pilota'] = df_laps['driver_number'].astype(str).map(driver_map)
        
        # Pulizia: mostriamo solo le cose importanti
        display_laps = df_laps[['pilota', 'lap_number', 'lap_duration', 'pitting']].tail(20)
        st.table(display_laps) # La tabella "Table" è più leggibile su mobile rispetto a "Dataframe"

with tab2:
    st.header("Comunicazioni Radio")
    radio = get_data(f"team_radio?session_key={s_key}")
    if radio:
        df_radio = pd.DataFrame(radio)
        df_radio['pilota'] = df_radio['driver_number'].astype(str).map(driver_map)
        
        for _, msg in df_radio.tail(10).iterrows():
            with st.chat_message("player"):
                st.write(f"**{msg['pilota']}**: [Audio Link]({msg['recording_url']})")

with tab3:
    weather = get_data(f"weather?session_key={s_key}")
    if weather:
        w = weather[-1]
        c1, c2 = st.columns(2)
        c1.metric("Temperatura Aria", f"{w['air_temperature']}°C")
        c2.metric("Temperatura Pista", f"{w['track_temperature']}°C")
