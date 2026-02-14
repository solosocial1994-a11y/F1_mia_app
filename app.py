import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OpenF1 Hub", layout="wide")
st.title("🏎️ OpenF1 Ultimate Dashboard")

def get_data(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data: return None
        return data if isinstance(data, list) else [data]
    except:
        return None

# Recupero ultima sessione
sessions = get_data("sessions?year=2024")
if sessions:
    session = sessions[-1]
    s_key = session['session_key']
    
    st.sidebar.success(f"📍 {session['location']}")
    st.sidebar.info(f"Sessione ID: {s_key}")

    tabs = st.tabs(["👥 Piloti", "⏱️ Tempi", "📡 GPS", "📻 Radio", "🌦️ Meteo"])

    # 1. PILOTI - Mostra tutto quello che l'API invia
    with tabs[0]:
        st.header("Anagrafica Piloti")
        drivers = get_data(f"drivers?session_key={s_key}")
        if drivers:
            df_d = pd.DataFrame(drivers)
            # Mostra tutte le colonne disponibili invece di sceglierle
            st.dataframe(df_d, use_container_width=True)
        else:
            st.warning("Dati piloti non disponibili per questa sessione.")

    # 2. TEMPI - Analisi Giri
    with tabs[1]:
        st.header("Cronometraggio")
        laps = get_data(f"laps?session_key={s_key}")
        if laps:
            st.dataframe(pd.DataFrame(laps).tail(50), use_container_width=True)

    # 3. GPS - Tracciato 3D
    with tabs[2]:
        st.header("Live Tracking (GPS)")
        locs = get_data(f"location?session_key={s_key}")
        if locs:
            df_loc = pd.DataFrame(locs).tail(300)
            # Usiamo nomi colonne sicuri
            fig = px.scatter_3d(df_loc, x='x', y='y', z='z', color='driver_number')
            st.plotly_chart(fig, use_container_width=True)

    # 4. RADIO - Comunicazioni
    with tabs[3]:
        st.header("Team Radio & Race Control")
        radio = get_data(f"team_radio?session_key={s_key}")
        if radio:
            st.dataframe(pd.DataFrame(radio).tail(20), use_container_width=True)

    # 5. METEO - Grafico temperature
    with tabs[4]:
        st.header("Meteo")
        weather = get_data(f"weather?session_key={s_key}")
        if weather:
            df_w = pd.DataFrame(weather)
            st.line_chart(df_w[['track_temperature', 'air_temperature']])
else:
    st.error("Impossibile caricare i dati. Verifica la connessione all'API.")
