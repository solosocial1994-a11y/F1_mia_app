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
        if not data or len(data) == 0: return None
        return data if isinstance(data, list) else [data]
    except:
        return None

# Sessione 9662 (Yas Island 2024)
sessions = get_data("sessions?session_key=9662")
if sessions:
    session = sessions[0]
    s_key = session['session_key']
    
    st.sidebar.success(f"📍 {session['location']}")
    st.sidebar.info(f"Sessione: {session['session_name']}")

    tabs = st.tabs(["👥 Piloti", "⏱️ Tempi", "📡 GPS & Telemetria", "📻 Radio", "🌦️ Meteo"])

    with tabs[0]:
        st.header("Anagrafica Piloti")
        drivers = get_data(f"drivers?session_key={s_key}")
        if drivers:
            st.dataframe(pd.DataFrame(drivers), use_container_width=True)

    with tabs[1]:
        st.header("Cronometraggio")
        laps = get_data(f"laps?session_key={s_key}")
        if laps:
            st.dataframe(pd.DataFrame(laps).tail(100), use_container_width=True)

    with tabs[2]:
        st.header("Live Tracking (GPS)")
        locs = get_data(f"location?session_key={s_key}")
        if locs:
            df_loc = pd.DataFrame(locs).tail(200)
            # PROTEZIONE GRAFICO: Controlla se le colonne x, y, z esistono
            columns_needed = {'x', 'y', 'z', 'driver_number'}
            if columns_needed.issubset(df_loc.columns):
                try:
                    fig = px.scatter_3d(df_loc, x='x', y='y', z='z', color='driver_number', title="Mappa GPS")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.warning("Impossibile generare il grafico 3D. Ecco i dati grezzi:")
                    st.dataframe(df_loc)
            else:
                st.write("Dati GPS incompleti. Visualizzazione tabella:")
                st.dataframe(df_loc)

    with tabs[3]:
        st.header("Team Radio")
        radio = get_data(f"team_radio?session_key={s_key}")
        if radio:
            st.dataframe(pd.DataFrame(radio).tail(20), use_container_width=True)

    with tabs[4]:
        st.header("Meteo")
        weather = get_data(f"weather?session_key={s_key}")
        if weather:
            df_w = pd.DataFrame(weather)
            if 'track_temperature' in df_w.columns:
                st.line_chart(df_w[['track_temperature', 'air_temperature']])
            else:
                st.dataframe(df_w)
else:
    st.error("Nessun dato trovato per questa sessione.")
