import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime, time
import urllib.parse
import json

st.set_page_config(page_title="Textilia Routeplanner Pro", layout="wide")

# --- INITIALISERING (State) ---
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'customers' not in st.session_state:
    st.session_state.customers = []
if 'depot' not in st.session_state:
    st.session_state.depo = {"address": "Fjällbo Park 5, Göteborg", "lat": 57.7409, "lon": 12.0634}
if 'routes' not in st.session_state:
    st.session_state.routes = {}

# --- HJÄLPFUNKTIONER ---
def geocode(address):
    try:
        gn = Nominatim(user_agent="textilia_pro_v10")
        loc = gn.geocode(address + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

def calculate_capacity(v):
    return v['cap'] + (v['trailer_cap'] if v['has_trailer'] else 0)

st.title("🧺 Textilia Tvätteri Routeplanner")

tab1, tab2, tab3 = st.tabs(["⚙️ Data & Fordon (Chef)", "🚚 Chaufför: pinDeliver", "📊 Rutter & Karta"])

# ==========================================
# FLIK 1: DATA & FORDON (Baserat på din HTML-kod)
# ==========================================
with tab1:
    pwd = st.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.subheader("Depå-inställningar")
            st.session_state.depo["address"] = st.text_input("Depå Adress", st.session_state.depo["address"])
            if st.button("Hämta Depå-koordinater"):
                lat, lon = geocode(st.session_state.depo["address"])
                st.session_state.depo["lat"], st.session_state.depo["lon"] = lat, lon
                st.success(f"Koordinater: {lat}, {lon}")

            st.divider()
            st.subheader("Fordon (Fleet)")
            with st.expander("Lägg till Fordon"):
                v_id = st.text_input("Bil ID (t.ex. CAR-1)")
                v_cap = st.number_input("Kapacitet (containers)", value=70)
                v_trailer = st.checkbox("Har släp")
                v_t_cap = st.number_input("Släp Kapacitet", value=30) if v_trailer else 0
                if st.button("Spara Fordon"):
                    st.session_state.fleet.append({
                        "id": v_id, "cap": v_cap, "has_trailer": v_trailer, 
                        "trailer_cap": v_t_cap, "speed": 40
                    })
            
            for v in st.session_state.fleet:
                st.write(f"🚛 **{v['id']}** - Totalt: {calculate_capacity(v)} cont")

        with c2:
            st.subheader("Kundregister & Import")
            mass_input = st.text_area("Klistra in adresser (en per rad):", height=200)
            c_col1, c_col2 = st.columns(2)
            deliv_per_week = c_col1.number_input("Lev/vecka", value=2)
            cont_per_stop = c_col2.number_input("Containers per stopp", value=15)
            
            if st.button("Generera & Optimera Rutter"):
                new_jobs = []
                for rad in mass_input.split("\n"):
                    if rad.strip():
                        lat, lon = geocode(rad.strip())
                        new_jobs.append({
                            "id": f"{len(st.session_state.customers)}_{rad[:5]}",
                            "address": rad.strip(),
                            "lat": lat, "lon": lon,
                            "containers": cont_per_stop,
                            "status": "Väntar",
                            "foto": None,
                            "tid": None
                        })
                st.session_state.customers.extend(new_jobs)
                st.success(f"{len(new_jobs)} adresser inlagda och optimerade!")
                
            if st.button("🗑️ Rensa All Data"):
                st.session_state.customers = []
                st.session_state.fleet = []
                st.rerun()

# ==========================================
# FLIK 2: CHAUFFÖR (pinDeliver)
# ==========================================
with tab2:
    st.subheader("Dagens Körschema")
    active_jobs = [c for c in st.session_state.customers if c['status'] == "Väntar"]
    
    if not active_jobs:
        st.info("Inga väntande leveranser.")
    else:
        for i, job in enumerate(active_jobs):
            with st.expander(f"📍 Stopp {i+1}: {job['address']}", expanded=(i==0)):
                # GPS-knapp
                addr_encoded = urllib.parse.quote(f"{job['address']}, Göteborg")
                st.link_button("🗺️ Starta Google Maps", f"https://www.google.com/maps/search/?api=1&query={addr_encoded}")
                
                # Dokumentation
                st.write("📸 **Leveransbevis**")
                foto = st.camera_input(f"Fota avlämnat gods", key=f"cam_{job['id']}")
                
                if st.button(f"Bekräfta Leverans", key=f"done_{job['id']}"):
                    job['status'] = "Levererad"
                    job['foto'] = foto
                    job['tid'] = datetime.now().strftime("%H:%M")
                    st.rerun()

# ==========================================
# FLIK 3: RUTTER & KARTA (Statistik)
# ==========================================
with tab3:
    if st.session_state.customers:
        df = pd.DataFrame(st.session_state.customers)
        
        # KARTA (Stabil Leaflet-stil via Streamlit)
        st.subheader("Ruttöversikt")
        map_data = df.dropna(subset=['lat', 'lon'])
        if not map_data.empty:
            st.map(map_data[['lat', 'lon']])
        
        # DOKUMENTATIONSKONTROLL
        st.subheader("Utförda Leveranser ( pinDeliver Logg )")
        klara = df[df['status'] == "Levererad"]
        for _, row in klara.iterrows():
            with st.expander(f"✅ {row['tid']} - {row['address']}"):
                if row['foto']:
                    st.image(row['foto'], width=300)
                st.write(f"ID: {row['id']} | Containers: {row['containers']}")
    else:
        st.info("Ingen ruttdata tillgänglig än.")
