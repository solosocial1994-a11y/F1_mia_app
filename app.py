import streamlit as st
import requests
import pandas as pd

# Configurazione per farla sembrare un'app vera sul telefono
st.set_page_config(page_title="F1 Live 2026", layout="wide")

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except: return None

# --- SIDEBAR: SELEZIONE PULITA ---
st.sidebar.title("🏎️ F1 2026")
year = st.sidebar.selectbox("Anno", [2026, 2025, 2024], index=0)

sessions = get_f1(f"sessions?year={year}")
if sessions:
    # Mostriamo solo i nomi delle piste
    loc_list = sorted(list(set([s['location'] for s in sessions])), reverse=True)
    sel_loc = st.sidebar.selectbox("Circuito", loc_list)
    
    # Filtriamo le sessioni per quella pista
    s_options = [s for s in sessions if s['location'] == sel_loc]
    s_map = {f"{s['session_name']}": s['session_key'] for s in s_options}
    sel_s_name = st.sidebar.selectbox("Sessione", list(s_map.keys()))
    s_key = s_map[sel_s_name]
else:
    st.error("Dati non disponibili")
    st.stop()

# --- IL SEGRETO: LA MAPPA PILOTI (Per non vedere più solo numeri) ---
drivers_raw = get_f1(f"drivers?session_key={s_key}")
d_map = {}
if drivers_raw:
    for d in drivers_raw:
        d_map[str(d['driver_number'])] = {
            "name": d['broadcast_name'],
            "team": d['team_name'],
            "color": f"#{d['team_colour']}"
        }

# --- INTERFACCIA GRAFICA PULITA ---
st.title(f"🏁 {sel_loc}")
st.subheader(f"{sel_s_name} - 2026")

tab1, tab2, tab3 = st.tabs(["⏱️ Classifica", "📻 Radio", "🌦️ Meteo"])

with tab1:
    laps = get_f1(f"laps?session_key={s_key}")
    if laps:
        df = pd.DataFrame(laps)
        # Trasformiamo il numero nel Nome del Pilota
        df['Pilota'] = df['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', f"Pilota {x}"))
        
        # MOSTRA SOLO QUELLO CHE SERVE (Basta tabelle giganti!)
        # Selezioniamo solo le colonne importanti
        viste_importanti = df[['Pilota', 'lap_number', 'lap_duration']].dropna().tail(15)
        st.table(viste_importanti) 
    else:
        st.info("Nessun tempo registrato.")

with tab2:
    radio = get_f1(f"team_radio?session_key={s_key}")
    if radio:
        for r in radio[-10:]:
            info = d_map.get(str(r['driver_number']), {"name": "Pilota", "color": "#ccc", "team": ""})
            # Creiamo un box colorato per ogni messaggio
            st.markdown(f"""
                <div style="border-left: 10px solid {info['color']}; padding: 15px; background: #262730; border-radius: 5px; margin-bottom: 10px;">
                    <strong>{info['name']}</strong> ({info['team']})<br>
                    <a href="{r['recording_url']}" target="_blank" style="color: #ff4b4b; text-decoration: none;">▶️ ASCOLTA MESSAGGIO RADIO</a>
                </div>
            """, unsafe_allow_html=True)

with tab3:
    weather = get_f1(f"weather?session_key={s_key}")
    if weather:
        w = weather[-1]
        col1, col2 = st.columns(2)
        col1.metric("Temperatura Aria", f"{w['air_temperature']}°C")
        col2.metric("Temperatura Pista", f"{w['track_temperature']}°C")
