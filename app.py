import streamlit as st
import requests

st.set_page_config(page_title="F1 Live", layout="centered")
st.title("🏎️ OpenF1 Mobile")

def get_data(endpoint):
    try:
        url = f"https://api.openf1.org/v1/{endpoint}"
        response = requests.get(url, timeout=10)
        return response.json()
    except:
        return None

# Proviamo a caricare l'ultima sessione del 2024 per testare l'app
st.write("### Ultime Sessioni")
sessions = get_data("sessions?year=2024")

if sessions:
    # Prendiamo l'ultima sessione della lista
    last_session = sessions[-1] 
    st.success(f"✅ Dati trovati: {last_session['location']}")
    
    with st.container():
        st.subheader(f"{last_session['session_name']}")
        st.info(f"Data: {last_session['date_start'][:10]}")
        
        # Mostriamo il meteo di quella specifica sessione
        st.write("---")
        st.write("#### ☁️ Meteo Sessione")
        weather_data = get_data(f"weather?session_key={last_session['session_key']}")
        if weather_data:
            w = weather_data[0]
            c1, c2 = st.columns(2)
            c1.metric("Aria", f"{w['air_temperature']}°C")
            c2.metric("Pista", f"{w['track_temperature']}°C")
else:
    st.error("L'API non risponde. Riprova tra pochi minuti.")
