import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# Configurazione ottimizzata per Mobile
st.set_page_config(page_title="F1 Live 2026", layout="wide", initial_sidebar_state="collapsed")

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        return data if isinstance(data, list) else [data]
    except: return None

# --- SIDEBAR: SELEZIONE STAGIONE 2026 ---
st.sidebar.title("🏁 Stagione 2026")
# Aggiunto il 2026 come opzione predefinita
year = st.sidebar.selectbox("Anno", [2026, 2025, 2024], index=0)

sessions = get_f1(f"sessions?year={year}")
if sessions:
    # Ordiniamo per data decrescente per avere i test/gare più recenti in alto
    locations = sorted(list(set([s['location'] for s in sessions])), reverse=True)
    sel_loc = st.sidebar.selectbox("Circuito", locations)
    
    s_options = [s for s in sessions if s['location'] == sel_loc]
    s_map = {f"{s['session_name']} ({s['date_start'][:10]})": s['session_key'] for s in s_options}
    sel_s_name = st.sidebar.selectbox("Sessione", list(s_map.keys()))
    s_key = s_map[sel_s_name]
else:
    st.error("Dati 2026 non ancora caricati nell'API. Riprova tra poco.")
    st.stop()

# --- MAPPA PILOTI 2026 ---
drivers_raw = get_f1(f"drivers?session_key={s_key}")
d_map = {str(d['driver_number']): {"name": d['broadcast_name'], "color": f"#{d['team_colour']}"} for d in drivers_raw} if drivers_raw else {}

# --- DASHBOARD PRINCIPALE ---
st.title(f"🏎️ {sel_loc}")
st.write(f"**Sessione:** {sel_s_name} | **ID:** {s_key}")

tabs = st.tabs(["⏱️ Classifica", "📡 GPS & Telemetria", "📻 Radio", "🌦️ Meteo"])

with tabs[0]: # CLASSIFICA TEMPI
    laps = get_f1(f"laps?session_key={s_key}")
    if laps:
        df_laps = pd.DataFrame(laps)
        df_laps['Pilota'] = df_laps['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', x))
        # Mostriamo i dati essenziali per i test
        st.dataframe(df_laps[['Pilota', 'lap_number', 'lap_duration', 'pitting']].tail(30), use_container_width=True)
    else:
        st.info("In attesa di tempi sul giro...")

with tabs[1]: # TELEMETRIA GPS
    st.subheader("Tracciato Live (GPS)")
    locs = get_f1(f"location?session_key={s_key}")
    if locs:
        df_loc = pd.DataFrame(locs).tail(500)
        if {'x', 'y', 'z'}.issubset(df_loc.columns):
            fig = px.line_3d(df_loc, x='x', y='y', z='z', color='driver_number', title="Posizioni in Pista")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Dati GPS non disponibili per questa sessione.")

with tabs[2]: # RADIO AUDIO
    st.subheader("Team Radio Recenti")
    radio = get_f1(f"team_radio?session_key={s_key}")
    if radio:
        for r in radio[-10:]: # Ultimi 10 messaggi
            p_name = d_map.get(str(r['driver_number']), {}).get('name', f"Pilota {r['driver_number']}")
            st.audio(r['recording_url'])
            st.caption(f"📻 {p_name}")
    else:
        st.write("Nessun messaggio radio registrato.")

with tabs[3]: # METEO LIVE
    st.subheader("Condizioni in Pista")
    weather = get_f1(f"weather?session_key={s_key}")
    if weather:
        w = weather[-1]
        c1, c2, c3 = st.columns(3)
        c1.metric("Aria", f"{w['air_temperature']}°C")
        c2.metric("Pista", f"{w['track_temperature']}°C")
        c3.metric("Pioggia", "SÌ" if w['rainfall'] else "NO")
