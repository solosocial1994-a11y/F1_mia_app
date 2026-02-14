import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OpenF1 Ultimate Hub", layout="wide")
st.title("🏎️ OpenF1 Ultimate Dashboard")

# Funzione di recupero dati robusta
def get_data(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data: return None
        # Forza i dati in una lista se non lo sono già
        return data if isinstance(data, list) else [data]
    except:
        return None

# Recupero ultima sessione disponibile
sessions = get_data("sessions?year=2024")
if sessions:
    session = sessions[-1]
    s_key = session['session_key']
    
    st.sidebar.markdown(f"### 🏁 {session['location']}")
    st.sidebar.write(f"**Sessione:** {session['session_name']}")
    st.sidebar.write(f"**Data:** {session['date_start'][:10]}")

    # Organizzazione in Tab per non fare confusione
    tab_drivers, tab_laps, tab_telemetry, tab_comms, tab_weather = st.tabs([
        "👥 Piloti", "⏱️ Tempi & Gomme", "📡 Telemetria & GPS", "📻 Comunicazioni", "🌦️ Meteo"
    ])

    with tab_drivers:
        st.header("Griglia di Partenza")
        drivers = get_data(f"drivers?session_key={s_key}")
        if drivers:
            df_d = pd.DataFrame(drivers)
            st.dataframe(df_d[['broadcast_name', 'team_name', 'driver_number', 'team_colour']], use_container_width=True)

    with tab_laps:
        st.header("Analisi Giri e Strategia")
        col_l, col_s = st.columns(2)
        with col_l:
            st.subheader("Ultimi Giri")
            laps = get_data(f"laps?session_key={s_key}")
            if laps: st.dataframe(pd.DataFrame(laps).tail(50))
        with col_s:
            st.subheader("Uso Gomme (Stints)")
            stints = get_data(f"stints?session_key={s_key}")
            if stints: st.dataframe(pd.DataFrame(stints))

    with tab_telemetry:
        st.header("Dati GPS e Telemetria")
        st.info("I dati GPS mostrano il tracciato basato sulle ultime 200 posizioni rilevate.")
        location = get_data(f"location?session_key={s_key}")
        if location:
            df_loc = pd.DataFrame(location).tail(200)
            fig = px.line_3d(df_loc, x='x', y='y', z='z', color='driver_number', title="Tracciato Live")
            st.plotly_chart(fig, use_container_width=True)

    with tab_comms:
        st.header("Radio & Race Control")
        radio = get_data(f"team_radio?session_key={s_key}")
