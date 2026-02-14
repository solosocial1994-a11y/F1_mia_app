import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="F1 2026 Live", layout="wide")

def get_f1(endpoint):
    url = f"https://api.openf1.org/v1/{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if not data: return None
        return data if isinstance(data, list) else [data]
    except: return None

def format_time(seconds):
    if pd.isna(seconds) or seconds <= 0: return "-"
    minutes = int(seconds // 60)
    rem_seconds = seconds % 60
    return f"{minutes}:{rem_seconds:06.3f}"

# --- SELEZIONE SESSIONE 2026 ---
st.sidebar.title("🏁 Centro Dati 2026")
year = st.sidebar.selectbox("Anno", [2026, 2025, 2024], index=0)
sessions = get_f1(f"sessions?year={year}")

if sessions:
    s_df = pd.DataFrame(sessions).sort_values('date_start', ascending=False)
    loc = st.sidebar.selectbox("Circuito", s_df['location'].unique())
    s_options = s_df[s_df['location'] == loc]
    s_name = st.sidebar.selectbox("Sessione", s_options['session_name'].unique())
    s_key = s_options[s_options['session_name'] == s_name]['session_key'].values[0]
else: st.stop()

# --- MAPPA PILOTI ---
drivers = get_f1(f"drivers?session_key={s_key}")
d_map = {str(d['driver_number']): d['broadcast_name'] for d in drivers} if drivers else {}

st.title(f"🏎️ {loc}")

tab1, tab2, tab3 = st.tabs(["⏱️ Classifica", "📊 Tele
