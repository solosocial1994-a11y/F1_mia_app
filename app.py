import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 2026 Hub", layout="wide")

# CSS per evitare che le tabelle siano brutte su mobile
st.markdown("""<style> .stTable { font-size: 12px !important; } </style>""", unsafe_allow_html=True)

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except: return None

# --- SIDEBAR ---
with st.sidebar:
    st.title("🏁 Comandi 2026")
    year = st.selectbox("Anno", [2026, 2025, 2024], index=0)
    sessions = get_f1(f"sessions?year={year}")
    
    if sessions:
        # Ordiniamo per data per trovare subito i test del Bahrain
        s_df = pd.DataFrame(sessions).sort_values('date_start', ascending=False)
        loc = st.selectbox("Circuito", s_df['location'].unique())
        
        s_options = s_df[s_df['location'] == loc]
        s_name = st.selectbox("Sessione", s_options['session_name'].unique())
        s_key = s_options[s_options['session_name'] == s_name]['session_key'].values[0]
    else:
        st.stop()

# --- MAPPA PILOTI ---
drivers_raw = get_f1(f"drivers?session_key={s_key}")
d_map = {str(d['driver_number']): {"name": d['broadcast_name'], "team": d['team_name'], "color": f"#{d['team_colour']}"} for d in drivers_raw} if drivers_raw else {}

st.title(f"🏎️ {loc}")
st.caption(f"Dati Live Sessione: {s_key}")

tab1, tab2, tab3, tab4 = st.tabs(["⏱️ Tempi", "📊 Telemetria", "📻 Radio", "🌦️ Meteo"])

with tab1:
    st.subheader("Classifica Tempi")
    laps = get_f1(f"laps?session_key={s_key}")
    if laps:
        df_l = pd.DataFrame(laps).tail(20)
        df_l['Pilota'] = df_l['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', x))
        # Mostriamo solo dati essenziali e puliti
        st.table(df_l[['Pilota', 'lap_number', 'lap_duration']].rename(columns={'lap_number':'Giro', 'lap_duration':'Tempo'}))

with tab2:
    st.subheader("Telemetria in Tempo Reale")
    # Prendiamo gli ultimi dati dei sensori (velocità, giri motore)
    car_data = get_f1(f"car_data?session_key={s_key}")
    if car_data:
        df_c = pd.DataFrame(car_data).tail(10)
        df_c['Pilota'] = df_c['driver_number'].astype(str).map(lambda x: d_map.get(x, {}).get('name', x))
        st.dataframe(df_c[['Pilota', 'speed', 'rpm', 'n_gear', 'throttle', 'brake']], use_container_width=True)
    else:
        st.info("Telemetria non disponibile per questa sessione di test.")

with tab3:
    st.subheader("Radio Team")
    radio = get_f1(f"team_radio?session_key={s_key}")
    if radio:
        for r in radio[-5:]:
            info = d_map.get(str(r['driver_number']), {"name": "Driver", "color": "#888"})
            st.markdown(f"<div style='border-left:5px solid {info['color']}; padding-left:10: margin:10'><b>{info['name']}</b></div>", unsafe_allow_html=True)
            st.audio(r['recording_url'])

with tab4:
    weather = get_f1(f"weather?session_key={s_key}")
    if weather:
        w = weather[-1]
        st.metric("Pista", f"{w['track_temperature']}°C")
        st.metric("Vento", f"{w['wind_speed']} m/s")
