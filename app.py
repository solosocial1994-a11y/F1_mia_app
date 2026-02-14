import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="OpenF1 Ultimate", layout="wide")
st.title("🏁 OpenF1 Full Dashboard")

def get_data(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        return r.json()
    except: return None

# Selezione Sessione (Prendiamo l'ultima del 2024 per sicurezza dati)
sessions = get_data("sessions?year=2024")
if sessions:
    session = sessions[-1]
    s_key = session['session_key']
    st.sidebar.success(f"Sessione: {session['location']}")
    
    # CREAZIONE TAB PER VEDERE "TUTTO"
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 Piloti", "⏱️ Tempi & Gomme", "📡 Telemetria Live", "📻 Radio & Race Control", "🌦️ Meteo"
    ])

    # --- TAB 1: PILOTI ---
    with tab1:
        st.header("Anagrafica Piloti")
        drivers = get_data(f"drivers?session_key={s_key}")
        if drivers:
            st.table(pd.DataFrame(drivers)[['broadcast_name', 'team_name', 'driver_number', 'country_code']])

    # --- TAB 2: TEMPI & GOMME ---
    with tab2:
        st.header("Ultimi Giri e Mescole")
        laps = get_data(f"laps?session_key={s_key}")
        stints = get_data(f"stints?session_key={s_key}")
        if laps:
            st.dataframe(pd.DataFrame(laps).tail(20)) # Mostra gli ultimi 20 giri registrati
        if stints:
            st.subheader("Strategia Gomme")
            st.write(pd.DataFrame(stints)[['driver_number', 'compound', 'tyre_age_at_start']])

    # --- TAB 3: TELEMETRIA (GPS) ---
    with tab3:
        st.header("Posizione GPS in tempo reale")
        # Prendiamo le posizioni degli ultimi secondi
        location = get_data(f"location?session_key={s_key}")
        if location:
            df_loc = pd.DataFrame(location).tail(100)
            fig = px.scatter_3d(df_loc, x='x', y='y', z='z', color='driver_number', title="Mappa 3D Circuito")
            st.plotly_chart(fig, use_container_width=True)

    # --- TAB 4: RADIO & MESSAGGI ---
    with tab4:
        col_r, col_m = st.columns(2)
        with col_r:
            st.header("Team Radio")
            radio = get_data(f"team_radio?session_key={s_key}")
            if radio: st.write(pd.DataFrame(radio).tail(10))
        with col_m:
            st.header("Direzione Gara")
            messages = get_data(f"race_control?session_key={s_key}")
            if messages: st.write(pd.DataFrame(messages).tail(10))

    # --- TAB 5: METEO ---
    with tab5:
        st.header("Dati Ambientali")
        weather = get_data(f"weather?session_key={s_key}")
        if weather:
            df_w = pd.DataFrame(weather)
            st.line_chart(df_w.set_index('date')['track_temperature'])
            st.metric("Vento", f"{weather[-1]['wind_speed']} m/s")

else:
    st.error("Connessione fallita.")
