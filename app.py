import streamlit as st
import requests

st.set_page_config(page_title="F1 Live", layout="centered")
st.title("🏎️ OpenF1 Mobile")

# Funzione per prendere i dati dall'API che hai linkato
def get_data(path):
    url = f"https://api.openf1.org/v1/{path}"
    return requests.get(url).json()

# Mostra l'ultima sessione
try:
    session = get_data("sessions?latest")[0]
    st.subheader(f"{session['location']} - {session['session_name']}")
    st.write(f"Anno: {session['year']}")
    
    # Esempio: Mostra il meteo live
    st.markdown("---")
    st.write("### ☁️ Meteo in Pista")
    weather = get_data(f"weather?session_key={session['session_key']}&latest")[0]
    col1, col2 = st.columns(2)
    col1.metric("Aria", f"{weather['air_temperature']}°C")
    col2.metric("Pista", f"{weather['track_temperature']}°C")

except:
    st.error("Dati al momento non disponibili.")
