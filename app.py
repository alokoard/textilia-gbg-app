import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Textilia Logistik Gbg", layout="wide")

# 1. Starta systemet
if 'stopp' not in st.session_state:
    st.session_state.stopp = []
if 'historik' not in st.session_state:
    st.session_state.historik = []

st.title("🚚 Textilia Gbg - Professionell Logistik")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Chefsvy", "📍 Chaufför", "🗄️ Historik", "📊 Dashboard"])

# ==========================================
# FLIK 1: CHEFSVY (Skapa & Prioritera)
# ==========================================
with tab1:
    st.header("Planera rutter")
    
    with st.expander("➕ Mass-inmatning av adresser"):
        inmatning = st.text_area("Klistra in adresser (en per rad):", placeholder="Sahlgrenska\nGothia Towers")
        start_prio = st.selectbox("Bas-prioritet för dessa:", [1, 2, 3, 4, 5], index=2)
        if st.button("Lägg till i listan"):
            for rad in inmatning.split("\n"):
                if rad.strip():
                    st.session_state.stopp.append({
                        "adress": rad.strip(), "status": "Väntar", "prio": start_prio, "lat": None, "lon": None
                    })
            st.rerun()

    if st.session_state.stopp:
        st.subheader("Aktuell lista")
        # Här kan du manuellt ändra prioritet på varje stopp
        for i, s in enumerate(st.session_state.stopp):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{s['adress']}**")
            s['prio'] = col2.number_input("Prio (1=Högst)", 1, 10, s['prio'], key=f"prio_{i}")

        if st.button("🚀 Optimera & Sortera (Prio först!)"):
            # Sorterar först på manuell prio, sedan på adress (kan bytas mot GPS-optimering)
            st.session_state.stopp.sort(key=lambda x: (x['prio'], x['adress']))
            st.success("Rutten är sorterad efter dina prioriteringar!")
            st.rerun()

# ==========================================
# FLIK 2: CHAUFFÖRSVY (Navigering & Signatur)
# ==========================================
with tab2:
    st.header("Dagens Körning")
    for i, s in enumerate(st.session_state.stopp):
        if s['status'] == "Väntar":
            with st.expander(f"Prio {s['prio']}: {s['adress']}", expanded=True):
                # Navigeringsknapp
                url_adress = urllib.parse.quote(f"{s['adress']}, Göteborg")
                st.link_button("🗺️ Starta GPS (Google Maps)", f"https://www.google.com/maps/search/?api=1&query={url_adress}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Levererat", key=f"ok_{i}"):
                        s['status'] = "Klar"
                        st.session_state.historik.append({"adress": s['adress'], "tid": datetime.now(), "typ": "OK"})
                        st.rerun()
                with col2:
                    kamera = st.camera_input("Foto vid avvikelse", key=f"cam_{i}")
                    if st.button("⚠️ Rapportera Problem", key=f"err_{i}"):
                        s['status'] = "Problem"
                        st.session_state.historik.append({"adress": s['adress'], "tid": datetime.now(), "typ": "FEL", "foto": kamera})
                        st.rerun()

# ==========================================
# FLIK 4: DASHBOARD (Miljö & Prestanda)
# ==========================================
with tab4:
    st.header("Prestanda & Miljö")
    klar = len([x for x in st.session_state.stopp if x['status'] == "Klar"])
    total = len(st.session_state.stopp)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Genomförda", f"{klar}/{total}")
    col2.metric("CO2 Besparing", f"{klar * 0.4:.1 f} kg", "+12%")
    col3.metric("Effektivitet", f"{100 if total == 0 else (klar/total)*100:.0 f}%")
