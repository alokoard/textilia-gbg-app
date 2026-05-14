import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime
import urllib.parse
import uuid

# Optimera för stora skärmar
st.set_page_config(page_title="Textilia Gbg - Control Tower", layout="wide")

# --- INITIALISERING ---
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'jobs' not in st.session_state:
    st.session_state.jobs = []
if 'depo' not in st.session_state:
    st.session_state.depo = {"address": "Fjällbo Park 5, Göteborg", "lat": 57.7409, "lon": 12.0634}

# Geokodning
def get_gps(address):
    try:
        gn = Nominatim(user_agent="textilia_control_tower")
        loc = gn.geocode(address + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

# --- UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .status-card { padding: 20px; border-radius: 10px; background-color: white; border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚛 Textilia Gbg Logistik - Control Tower")

tab1, tab2, tab3 = st.tabs(["🏗️ Planering & Fleet", "🚚 Chaufförsvy", "🖥️ Chefens Dashboard"])

# ==========================================
# FLIK 1: PLANERING & FLEET (Bättre layout)
# ==========================================
with tab1:
    pwd = st.sidebar.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        col_fleet, col_plan = st.columns([1, 2])
        
        with col_fleet:
            st.subheader("🚐 Hantera Fleet")
            with st.container():
                v_name = st.text_input("Fordonsnamn/ID", placeholder="Ex: Bil 104")
                v_type = st.radio("Typ av fordon", ["Singelbil", "Ekipage (Bil + Släp)"])
                
                c1, c2 = st.columns(2)
                cap_truck = c1.number_input("Kapacitet Bil", value=70)
                cap_trailer = c2.number_input("Kapacitet Släp", value=0) if v_type == "Ekipage (Bil + Släp)" else 0
                
                total_cap = cap_truck + cap_trailer
                st.info(f"**Total kapacitet:** {total_cap} containers")
                
                if st.button("➕ Lägg till i Fleet"):
                    st.session_state.fleet.append({
                        "id": str(uuid.uuid4())[:8],
                        "name": v_name,
                        "type": v_type,
                        "total_cap": total_cap,
                        "truck_cap": cap_truck,
                        "trailer_cap": cap_trailer
                    })
                    st.success(f"{v_name} tillagd!")

            st.divider()
            st.write("**Aktiva Fordon:**")
            for v in st.session_state.fleet:
                st.write(f"▪️ {v['name']} ({v['type']}) - {v['total_cap']} cont")

        with col_plan:
            st.subheader("📍 Ruttplanering & Adressimport")
            mass_addr = st.text_area("Klistra in adresser (en per rad):", height=200, placeholder="Gothia Towers\nSahlgrenska\n...")
            
            sel_v = st.selectbox("Tilldela till fordon:", [v['name'] for v in st.session_state.fleet] if st.session_state.fleet else ["Inga fordon tillgängliga"])
            
            if st.button("🚀 Generera och Spara Rutt"):
                new_entries = []
                for addr in mass_addr.split("\n"):
                    if addr.strip():
                        lat, lon = get_gps(addr.strip())
                        new_entries.append({
                            "id": str(uuid.uuid4()), # Unikt ID för varje stopp
                            "driver": sel_v,
                            "address": addr.strip(),
                            "status": "Väntar",
                            "lat": lat, "lon": lon,
                            "time": None,
                            "photo": None
                        })
                st.session_state.jobs.extend(new_entries)
                st.success(f"Rutt sparad för {sel_v}!")

    else:
        st.warning("Vänligen ange chefskod i sidomenyn för att komma åt planeringen.")

# ==========================================
# FLIK 2: CHAUFFÖRSVY (Smidig check-in)
# ==========================================
with tab2:
    if not st.session_state.fleet:
        st.info("Inga fordon eller chaufförer är upplagda än.")
    else:
        driver_sel = st.selectbox("Logga in som chaufför:", [v['name'] for v in st.session_state.fleet])
        my_jobs = [j for j in st.session_state.jobs if j['driver'] == driver_sel and j['status'] == "Väntar"]
        
        if not my_jobs:
            st.success("🎉 Snyggt! Alla dina leveranser är klara.")
        else:
            st.subheader(f"Dagens uppdrag för {driver_sel}")
            for job in my_jobs:
                with st.expander(f"📍 Leverans: {job['address']}", expanded=True):
                    # GPS
                    enc_addr = urllib.parse.quote(f"{job['address']}, Göteborg")
                    st.link_button("🧭 Öppna GPS", f"https://www.google.com/maps/search/?api=1&query={enc_addr}")
                    
                    # pinDeliver dokumentation
                    st.write("---")
                    pic = st.camera_input("Ta leveransbild (Bevis)", key=f"cam_{job['id']}")
                    
                    if st.button("✅ BEKRÄFTA LEVERERAD", key=f"btn_{job['id']}"):
                        job['status'] = "Levererad"
                        job['time'] = datetime.now().strftime("%H:%M")
                        job['photo'] = pic
                        st.rerun()

# ==========================================
# FLIK 3: CHEFENS DASHBOARD (Överblick)
# ==========================================
with tab3:
    st.subheader("🖥️ Live Kontrollpanel")
    
    if not st.session_state.jobs:
        st.info("Väntar på data från fältet...")
    else:
        # Metriker längst upp
        tot = len(st.session_state.jobs)
        klar = len([j for j in st.session_state.jobs if j['status'] == "Levererad"])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Totala Leveranser", tot)
        m2.metric("Genomförda", klar)
        m3.metric("Återstående", tot - klar)
        
        st.divider()
        
        # Karta och Detaljerad logg
        col_map, col_log = st.columns([1, 1])
        
        with col_map:
            st.write("**Ruttkarta (Realtid)**")
            df = pd.DataFrame(st.session_state.jobs)
            st.map(df.dropna(subset=['lat', 'lon']))

        with col_log:
            st.write("**Leveranslogg (Senaste händelser)**")
            for j in reversed(st.session_state.jobs):
                status_color = "🟢" if j['status'] == "Levererad" else "🟡"
                with st.container():
                    st.markdown(f"{status_color} **{j['time'] or 'Väntar'}** - {j['driver']} @ {j['address']}")
                    if j['photo']:
                        with st.expander("Visa Bildbevis"):
                            st.image(j['photo'], width=200)
