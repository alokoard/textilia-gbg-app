import streamlit as st
import pandas as pd
from datetime import datetime
# OBS: Installera 'supabase' biblioteket via pip install supabase
# --- KONFIGURATION --
st.set_page_config(page_title="Textilia Logistik", layout="centered")
# Simulerad databas-koppling (Här lägger du dina Supabase-nycklar senare)
# URL = st.secrets["SUPABASE_URL"]
# KEY = st.secrets["SUPABASE_KEY"]
if 'customers' not in st.session_state:
    st.session_state.customers = [
        {"id": 1, "namn": "Sahlgrenska Sjukhuset", "plats": "Blå Stråket", "status": 
"Väntar", "prioritet": 1},
        {"id": 2, "namn": "Gothia Towers", "plats": "Mässans gata", "status": 
"Väntar", "prioritet": 2},
        {"id": 3, "namn": "Clarion Hotel Post", "plats": "Drottningtorget", 
"status": "Väntar", "prioritet": 2},
        {"id": 4, "namn": "Restaurang 28", "plats": "Götabergsgatan", "status": 
"Väntar", "prioritet": 3}
    ]
if 'log' not in st.session_state:
    st.session_state.log = []
# --- GRÄNSSNITT --
tab1, tab2, tab3 = st.tabs(["🚚 Körning", "📜 Historik", "📊 Miljö"])
with tab1:
    st.header("Dagens Rutt")
    st.info("Startpunkt: Fjällbo Park 5 (Textilia Depå)")
    for i, c in enumerate(st.session_state.customers):
        if c['status'] == "Väntar":
            with st.expander(f"{c['namn']} - {c['plats']}"):
                foto = st.camera_input(f"Leveransbevis: {c['namn']}", 
key=f"c_{c['id']}")
                if foto:
                    if st.button("Bekräfta & Spara", key=f"b_{c['id']}"):
                        tid = datetime.now().strftime("%H:%M")
                        st.session_state.log.append({"kund": c['namn'], "tid": tid, 
"foto": foto})
                        st.session_state.customers[i]['status'] = "Klar"
                        st.success("Sparat!")
                        st.rerun()
with tab2:
    st.header("Historik")
    if not st.session_state.log:
        st.write("Inga leveranser ännu.")
    for entry in reversed(st.session_state.log):
        col1, col2 = st.columns([1, 2])
        col1.image(entry['foto'], width=150)
        col2.write(f"**{entry['kund']}**")
        col2.write(f"Tid: {entry['tid']}")
with tab3:
    st.header("Miljörapport")
    st.metric("Sparat bränsle", "14%", "Mindre tomkörning")
    st.metric("CO2 Besparing", "5.2 kg")