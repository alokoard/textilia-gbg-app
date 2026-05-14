import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Textilia Routeplanner Pro", layout="wide")

# --- INITIALISERING ---
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'customers' not in st.session_state:
    st.session_state.customers = []
if 'depo' not in st.session_state:
    st.session_state.depo = {"address": "Fjällbo Park 5, Göteborg", "lat": 57.7409, "lon": 12.0634}

# --- HJÄLPFUNKTIONER ---
def geocode(address):
    try:
        gn = Nominatim(user_agent="textilia_pro_v10_1")
        loc = gn.geocode(address + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

st.title("🧺 Textilia Tvätteri Routeplanner")

tab1, tab2, tab3 = st.tabs(["⚙️ Data & Fordon (Chef)", "🚚 Chaufför: pinDeliver", "📊 Rutter & Karta"])

# ==========================================
# FLIK 1: DATA & FORDON
# ==========================================
with tab1:
    pwd = st.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        c1, c2 = st.columns([1, 2])
        with c1:
            st.subheader("Depå & Fordon")
            st.session_state.depo["address"] = st.text_input("Depå Adress", st.session_state.depo["address"])
            
            if st.button("Spara Fordon"):
                st.session_state.fleet.append({"id": f"CAR-{len(st.session_state.fleet)+1}", "cap": 70})
            
            for v in st.session_state.fleet:
                st.write(f"🚛 **{v['id']}**")

        with c2:
            st.subheader("Ruttplanering")
            mass_input = st.text_area("Klistra in adresser (en per rad):", height=150)
            
            if st.button("Generera Rutter"):
                new_jobs = []
                # FIX: Använd enumerate för att skapa unika ID:n i loopen
                start_index = len(st.session_state.customers)
                for i, rad in enumerate(mass_input.split("\n")):
                    if rad.strip():
                        lat, lon = geocode(rad.strip())
                        # Unikt ID baserat på tid, index och adress-start
                        u_id = f"job_{start_index + i}_{datetime.now().strftime('%H%M%S%f')}"
                        new_jobs.append({
                            "id": u_id,
                            "address": rad.strip(),
                            "lat": lat, "lon": lon,
                            "status": "Väntar",
                            "foto": None,
                            "tid": None
                        })
                st.session_state.customers.extend(new_jobs)
                st.success(f"{len(new_jobs)} adresser tillagda!")
                
            if st.button("🗑️ Rensa All Data"):
                st.session_state.customers = []
                st.rerun()
    else:
        st.info("Ange chefskod.")

# ==========================================
# FLIK 2: CHAUFFÖR (pinDeliver)
# ==========================================
with tab2:
    active_jobs = [c for c in st.session_state.customers if c['status'] == "Väntar"]
    
    if not active_jobs:
        st.info("Inga väntande leveranser.")
    else:
        for job in active_jobs:
            with st.expander(f"📍 {job['address']}"):
                addr_encoded = urllib.parse.quote(f"{job['address']}, Göteborg")
                st.link_button("🗺️ Navigera", f"https://www.google.com/maps/search/?api=1&query={addr_encoded}")
                
                # Kamera med garanterat unik nyckel
                foto = st.camera_input("Fota leverans", key=f"cam_{job['id']}")
                
                if st.button("Klarmarkera", key=f"done_{job['id']}"):
                    job['status'] = "Levererad"
                    job['foto'] = foto
                    job['tid'] = datetime.now().strftime("%H:%M")
                    st.rerun()

# ==========================================
# FLIK 3: RUTTER & KARTA
# ==========================================
with tab3:
    if st.session_state.customers:
        df = pd.DataFrame(st.session_state.customers)
        st.map(df.dropna(subset=['lat', 'lon'])[['lat', 'lon']])
        
        st.subheader("Logg")
        klara = df[df['status'] == "Levererad"]
        for _, row in klara.iterrows():
            with st.expander(f"✅ {row['tid']} - {row['address']}"):
                if row['foto']: st.image(row['foto'])
