import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Textilia Tvätteri Routeplanner", layout="wide")

# --- SESSION STATE ---
if 'fleet' not in st.session_state:
    st.session_state.fleet = {"bil_id": "CAR-1", "kapacitet": 70, "hastighet": 40, "max_tid": 480}
if 'depo' not in st.session_state:
    st.session_state.depo = {"adress": "Fjällbo Park 5, Göteborg", "lat": 57.7409, "lon": 12.0634}
if 'uppdrag' not in st.session_state:
    st.session_state.uppdrag = []

# Hjälpfunktion för GPS
def hämta_gps(adress):
    try:
        geolocator = Nominatim(user_agent="textilia_v9_1")
        loc = geolocator.geocode(adress + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

st.title("🧺 Tvätteri Routeplanner - Professional")

tab1, tab2, tab3 = st.tabs(["⚙️ Data & Fordon", "🚚 Chaufför: Körning", "📊 Planering & Karta"])

# ==========================================
# FLIK 1: DATA & FORDON (Baserat på image_93ea73.png & image_93ea39.png)
# ==========================================
with tab1:
    pwd = st.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Depå & Fordon")
            st.session_state.depo["adress"] = st.text_input("Depå adress:", st.session_state.depo["adress"])
            st.session_state.fleet["kapacitet"] = st.number_input("Kapacitet (containers):", value=70)
            st.session_state.fleet["hastighet"] = st.number_input("Medelhastighet (km/h):", value=40)
            
        with col2:
            st.subheader("Kunder & Last")
            mass_input = st.text_area("Klistra in adresser (en per rad):")
            service_tid = st.number_input("Servicetid per stopp (min):", value=10)
            containers = st.number_input("Containers per stopp:", value=5)
            
            if st.button("Generera Rutter"):
                for rad in mass_input.split("\n"):
                    if rad.strip():
                        lat, lon = hämta_gps(rad.strip())
                        u_id = f"{datetime.now().strftime('%f')}_{len(st.session_state.uppdrag)}"
                        st.session_state.uppdrag.append({
                            "id": u_id,
                            "adress": rad.strip(),
                            "status": "Väntar",
                            "prio": 1,
                            "lat": lat, "lon": lon,
                            "containers": containers,
                            "servicetid": service_tid,
                            "foto": None,
                            "klar_tid": None
                        })
                st.success("Rutt genererad och redo för körning!")
                
        if st.session_state.uppdrag:
            st.divider()
            if st.button("🔴 Rensa all data"):
                st.session_state.uppdrag = []
                st.rerun()
    else:
        st.info("Logga in för att hantera fordonsdata och ruttplanering.")

# ==========================================
# FLIK 2: CHAUFFÖR (Dokumentation & GPS)
# ==========================================
with tab2:
    mina = [u for u in st.session_state.uppdrag if u['status'] == "Väntar"]
    
    if not mina:
        st.success("Dagens rutt är färdiglevererad!")
    else:
        u = mina[0]
        st.header(f"Nästa stopp: {u['adress']}")
        
        # GPS-knapp
        encoded_addr = urllib.parse.quote(f"{u['adress']}, Göteborg")
        st.link_button("🗺️ Starta Navigering (Google Maps)", f"https://www.google.com/maps/search/?api=1&query={encoded_addr}")
        
        st.divider()
        
        # Foto-dokumentation (Ersätter signatur för snabbare flöde)
        st.write("📸 **Dokumentera leverans** (Valfritt)")
        foto = st.camera_input("Ta bild på avlämnat gods", key=f"cam_{u['id']}")
        
        if st.button("✅ MARKERA SOM LEVERERAD", use_container_width=True):
            u['status'] = "Levererad"
            u['foto'] = foto
            u['klar_tid'] = datetime.now().strftime("%H:%M")
            st.success(f"Leverans till {u['adress']} registrerad!")
            st.rerun()

# ==========================================
# FLIK 3: PLANERING & KARTA (Baserat på image_93ea14.jpg)
# ==========================================
with tab3:
    st.subheader("Aktuell Ruttstatus")
    if st.session_state.uppdrag:
        df = pd.DataFrame(st.session_state.uppdrag)
        
        # Karta
        map_df = df.dropna(subset=['lat', 'lon'])
        if not map_df.empty:
            st.map(map_df[['lat', 'lon']])
            
        # Kapacitet och Statistik
        klara = df[df['status'] == "Levererad"]
        lastade = klara['containers'].sum()
        st.metric("Kapacitetsutnyttjande", f"{lastade} / {st.session_state.fleet['kapacitet']} containers")
        
        # Leveransbevis för chefen
        st.subheader("Granskning av utförda leveranser")
        for index, row in klara.iterrows():
            with st.expander(f"✅ {row['klar_tid']} - {row['adress']}"):
                if row['foto']:
                    st.image(row['foto'], caption="Leveransfoto", width=300)
                st.write(f"Containers: {row['containers']} st")
    else:
        st.info("Ingen planering aktiv. Gå till fliken 'Data & Fordon' för att starta.")
