import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 Live Pro", layout="wide")

# --- MOTORE DI RICERCA DATI ---
def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except: return None

# --- SIDEBAR: CONTROLLO TOTALE ---
st.sidebar.title("🏎️ Centro Comandi F1")

# 1. Selezione Anno e Gara
year = st.sidebar.selectbox("Scegli Anno", [2024, 2023], index=0)
all_sessions = get_f1(f"sessions?year={year}")

if all_sessions:
    # Filtriamo i circuiti e i tipi di sessione (Race, Quali, ecc.)
    locations = sorted(list(set([s['location'] for s in all_sessions])))
    sel_loc = st.sidebar.selectbox("Circuito", locations)
    
    # Filtriamo la sessione specifica
    s_options = [s for s in all_sessions if s['location'] == sel_loc]
    s_map = {f"{s['session_name']} ({s['date_start'][:10]})": s['session_key'] for s in s_options}
    sel_s_name = st.sidebar.selectbox("Sessione", list(s_map.keys()))
    s_key = s_map[sel_s_name]
    
    # Opzione Live
    if st.sidebar.button("📡 Cerca Sessione LIVE"):
        live = get_f1("sessions?latest")
        if live: s_key = live[0]['session_key']
else:
    st.sidebar.error("Impossibile caricare il calendario.")
    st.stop()

# --- MAPPA PILOTI (Per non vedere solo numeri!) ---
drivers_raw = get_f1(f"drivers?session_key={s_key}")
driver_names = {}
if drivers_raw:
    for d in drivers_raw:
        driver_names[str(d['driver_number'])] = {
            'name': d['broadcast_name'],
            'team': d['team_name'],
            'color': f"#{d['team_colour']}"
        }

# --- INTERFACCIA PRINCIPALE ---
st.title(f"🏁 {sel_loc}")
tab_laps, tab_radio, tab_weather = st.tabs(["⏱️ Classifica Tempi", "📻 Radio & Box", "🌦️ Meteo"])

with tab_laps:
    st.subheader("Ultimi Tempi Registrati")
    laps = get_f1(f"laps?session_key={s_key}")
    if laps:
        df_laps = pd.DataFrame(laps).tail(15)
        # Trasformiamo il numero nel Nome
        df_laps['Pilota'] = df_laps['driver_number'].astype(str).map(lambda x: driver_names.get(x, {}).get('name', x))
        st.table(df_laps[['Pilota', 'lap_number', 'lap_duration', 'is_pit_out_lap']])
    else:
        st.info("Nessun tempo registrato per questa sessione.")

with tab_radio:
    st.subheader("Messaggi Radio dal Muretto")
    radio = get_f1(f"team_radio?session_key={s_key}")
    if radio:
        for msg in radio[-10:]: # Mostra gli ultimi 10 messaggi
            p_num = str(msg['driver_number'])
            p_info = driver_names.get(p_num, {'name': p_num, 'color': '#ccc'})
            st.markdown(f"""
                <div style="border-left: 5px solid {p_info['color']}; padding: 10px; margin: 5px; background: #1e1e1e;">
                    <strong>{p_info['name']}</strong> ({p_info['team']})<br>
                    <a href="{msg['recording_url']}" target="_blank">▶️ Ascolta Radio</a>
                </div>
            """, unsafe_allow_html=True)

with tab_weather:
    weather = get_f1(f"weather?session_key={s_key}")
    if weather:
        w = weather[-1]
        col1, col2, col3 = st.columns(3)
        col1.metric("Aria", f"{w['air_temperature']}°C")
        col2.metric("Pista", f"{w['track_temperature']}°C")
        col3.metric("Pioggia", "Sì" if w['rainfall'] else "No")
