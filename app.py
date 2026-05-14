import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Textilia Gbg Test-Drive", layout="wide")

# Initiera minnet
if 'stopp' not in st.session_state:
    st.session_state.stopp = []
if 'historik' not in st.session_state:
    st.session_state.historik = []

st.title("🚚 Textilia Gbg - Logistik v4.0 (Test-läge)")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Chef: Planera", "📍 Chaufför: Körning", "🗄️ Historik", "📊 Miljö-Dashboard"])

# ==========================================
# FLIK 1: CHEFSVY (Mass-inmatning & Prio)
# ==========================================
with tab1:
    st.header("Planera dagens rutt")
    
    with st.expander("➕ Mass-inmatning (Klistra in här)"):
        inmatning = st.text_area("En adress per rad:", placeholder="Sahlgrenska\nGothia Towers\nLiseberg")
        if st.button("Lägg till adresser"):
            for rad in inmatning.split("\n"):
                if rad.strip():
                    st.session_state.stopp.append({
                        "adress": rad.strip(), 
                        "status": "Väntar", 
                        "prio": 3, 
                        "tid": None
                    })
            st.rerun()

    if st.session_state.stopp:
        st.subheader("Justera prioritering manuellt")
        st.write("Ändra siffran för att tvinga en viss ordning (1 är först).")
        
        for i, s in enumerate(st.session_state.stopp):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"📍 **{s['adress']}**")
            s['prio'] = col2.number_input("Prio", 1, 10, s['prio'], key=f"prio_{i}")
            if col3.button("Ta bort", key=f"del_{i}"):
                st.session_state.stopp.pop(i)
                st.rerun()

        if st.button("🚀 Sortera listan efter Prio"):
            st.session_state.stopp.sort(key=lambda x: x['prio'])
            st.success("Rutten är nu sorterad!")
            st.rerun()
            
    if st.button("🗑️ Rensa allt"):
        st.session_state.stopp = []
        st.session_state.historik = []
        st.rerun()

# ==========================================
# FLIK 2: CHAUFFÖRSVY
# ==========================================
with tab2:
    st.header("Dagens Uppdrag")
    väntande = [s for s in st.session_state.stopp if s['status'] == "Väntar"]
    
    if not väntande:
        st.success("Alla leveranser är klara eller inga adresser inlagda!")
    else:
        for i, s in enumerate(väntande):
            with st.expander(f"STÖPP {i+1}: {s['adress']} (Prio {s['prio']})", expanded=(i==0)):
                # Google Maps länk
                url_adress = urllib.parse.quote(f"{s['adress']}, Göteborg")
                st.link_button("🗺️ Öppna i Google Maps", f"https://www.google.com/maps/search/?api=1&query={url_adress}")
                
                c1, c2 = st.columns(2)
                if c1.button("✅ Markera som Klar", key=f"done_{i}"):
                    s['status'] = "Klar"
                    s['tid'] = datetime.now().strftime("%H:%M")
                    st.session_state.historik.append(s)
                    st.rerun()
                
                if c2.button("⚠️ Problem", key=f"err_{i}"):
                    s['status'] = "Problem"
                    s['tid'] = datetime.now().strftime("%H:%M")
                    st.session_state.historik.append(s)
                    st.rerun()

# ==========================================
# FLIK 3 & 4: HISTORIK & DASHBOARD
# ==========================================
with tab3:
    st.header("Utförda leveranser")
    for h in reversed(st.session_state.historik):
        ikon = "✅" if h['status'] == "Klar" else "❌"
        st.write(f"{ikon} {h['tid']} - **{h['adress']}**")

with tab4:
    st.header("Dagens Statistik")
    klar = len([s for s in st.session_state.stopp if s['status'] == "Klar"])
    total = len(st.session_state.stopp)
    st.metric("Leveransgrad", f"{klar} av {total}")
    st.progress(0 if total == 0 else klar/total)
    st.write(f"🌱 Uppskattad CO2-besparing: {klar * 0.5:.1f} kg")
