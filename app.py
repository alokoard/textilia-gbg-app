import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
import urllib.parse
import uuid

# --- KONFIGURATION ---
st.set_page_config(page_title="Textilia Gbg - Optimizer Pro", layout="wide")

if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'rutten' not in st.session_state:
    st.session_state.rutten = []
if 'depo' not in st.session_state:
    st.session_state.depo = {"namn": "Depå Textilia", "lat": 57.7409, "lon": 12.0634}

# Geokodning för Göteborg
def hämta_gps(adress):
    try:
        geolocator = Nominatim(user_agent="textilia_optimizer_v15_3")
        loc = geolocator.geocode(adress + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

# --- OPTIMERINGS-ALGORITM ---
def optimera_rutt(stopp_lista):
    if not stopp_lista: return []
    
    prio_stopp = sorted([s for s in stopp_lista if s.get('prio') == 1], key=lambda x: x.get('prio', 2))
    ovriga = [s for s in stopp_lista if s.get('prio', 2) > 1]
    
    sorterad = prio_stopp
    nuvarande_pos = (st.session_state.depo['lat'], st.session_state.depo['lon'])
    
    if prio_stopp:
        sista_prio = prio_stopp[-1]
        if sista_prio.get('lat'): nuvarande_pos = (sista_prio['lat'], sista_prio['lon'])

    med_gps = [s for s in ovriga if s.get('lat') is not None]
    utan_gps = [s for s in ovriga if s.get('lat') is None]

    while med_gps:
        närmsta = min(med_gps, key=lambda s: geodesic(nuvarande_pos, (s['lat'], s['lon'])).km)
        sorterad.append(närmsta)
        nuvarande_pos = (närmsta['lat'], närmsta['lon']) 
        med_gps.remove(närmsta)
    
    return sorterad + utan_gps

st.title("🚛 Textilia Gbg Logistik - Optimizer Pro v15.3")

tab1, tab2, tab3 = st.tabs(["🏗️ Chef: Planera & Optimera", "📍 Chaufför: Körning", "🖥️ Chef: Dashboard"])

# ==========================================
# FLIK 1: CHEFENS PLANERING
# ==========================================
with tab1:
    pwd = st.sidebar.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        col_f, col_p = st.columns([1, 2])
        
        with col_f:
            st.subheader("🚐 Fleet Management")
            v_id = st.text_input("Fordons-ID (Ex: Bil 104)")
            v_typ = st.selectbox("Typ", ["Singel", "Lastbil+Släp"])
            c1, c2 = st.columns(2)
            cap_b = c1.number_input("Kapacitet Bil", 1, 200, 70)
            cap_s = c2.number_input("Kapacitet Släp", 0, 200, 30) if v_typ == "Lastbil+Släp" else 0
            if st.button("➕ Registrera Fordon"):
                st.session_state.fleet.append({"id": v_id, "cap": cap_b + cap_s, "typ": v_typ})
                st.success(f"{v_id} registrerad!")

        with col_p:
            st.subheader("🚀 Mass-import & Optimering")
            r_id = st.number_input("Skapa Rutt ID", 1, 100, 1)
            f_val = st.selectbox("Tilldela till:", [f['id'] for f in st.session_state.fleet] if st.session_state.fleet else ["Inga fordon"])
            
            mass_addr = st.text_area("Klistra in adresser (en per rad):", height=150)
            vagnar_per_stopp = st.number_input("Vagnar att hämta (snitt):", 1, 50, 10)
            
            if st.button("⚡ Optimera & Spara Rutt"):
                temp_stopp = []
                for rad in mass_addr.split("\n"):
                    if rad.strip():
                        lat, lon = hämta_gps(rad.strip())
                        temp_stopp.append({
                            "id": str(uuid.uuid4()), "rutt": r_id, "fordon": f_val,
                            "adress": rad.strip(), "prio": 2, "vagnar": vagnar_per_stopp,
                            "lat": lat, "lon": lon, "status": "Väntar", "tid": None
                        })
                optimerad = optimera_rutt(temp_stopp)
                st.session_state.rutten.extend(optimerad)
                st.success(f"Rutt {r_id} optimerad!")

        st.divider()
        if st.session_state.rutten:
            st.subheader("📝 Redigera Aktiva Stopp")
            # Vi skapar en kopia för att undvika problem vid borttagning i loop
            for i, s in enumerate(st.session_state.rutten[:]):
                if s['status'] == "Väntar":
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"Rutt {s.get('rutt')} | **{s.get('adress')}**")
                    if col3.button("Ta bort", key=f"d_{s['id']}"):
                        st.session_state.rutten.remove(s)
                        st.rerun()
            
            if st.button("🔴 NOLLSTÄLL ALL DATA"):
                st.session_state.rutten = []
                st.rerun()
    else:
        st.info("Ange chefskod.")

# ==========================================
# FLIK 2: CHAUFFÖRSVY
# ==========================================
with tab2:
    rutter_aktiva = sorted(list(set([r.get('rutt') for r in st.session_state.rutten if r.get('rutt')])))
    if rutter_aktiva:
        val_r = st.selectbox("Välj din rutt:", rutter_aktiva)
        mina = [s for s in st.session_state.rutten if s.get('rutt') == val_r and s.get('status') == "Väntar"]
        
        st.header(f"Körschema: Rutt {val_r}")
        
        # Lastmätare
        f_info = next((f for f in st.session_state.fleet if f['id'] in [m.get('fordon') for m in mina]), None)
        vagnar_i_last = sum([s.get('vagnar', 0) for s in st.session_state.rutten if s.get('rutt') == val_r and s.get('status') == "Levererad"])
        
        if f_info:
            st.metric("📦 Last i bilen", f"{vagnar_i_last} / {f_info['cap']} containers")
        
        for i, s in enumerate(mina):
            with st.expander(f"STOPP {i+1}: {s.get('adress')}", expanded=(i==0)):
                st.write(f"Hämta: **{s.get('vagnar', 0)} vagnar**")
                st.link_button("🧭 Navigera", f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(s.get('adress', '') + ', Göteborg')}")
                
                if st.button("✅ Levererat & Hämtat", key=f"ok_{s['id']}"):
                    s['status'] = "Levererad"
                    s['tid'] = datetime.now().strftime("%H:%M")
                    st.rerun()
    else:
        st.info("Inga rutter tillgängliga.")

# ==========================================
# FLIK 3: DASHBOARD (Fixad för KeyError)
# ==========================================
with tab3:
    st.header("🖥️ Dashboard - Textilia Gbg")
    if st.session_state.rutten:
        df = pd.DataFrame(st.session_state.rutten)
        
        # Säkert sätt att visa karta
        map_df = df.dropna(subset=['lat', 'lon'])
        if not map_df.empty:
            st.map(map_df[['lat', 'lon']])
        
        st.subheader("Händelselogg")
        # FIX: Kontrollera att kolumnerna finns innan vi filtrerar df
        cols_att_visa = ['rutt', 'fordon', 'adress', 'status', 'tid', 'vagnar']
        befintliga_cols = [c for c in cols_att_visa if c in df.columns]
        
        if 'tid' in df.columns:
            st.dataframe(df[befintliga_cols].sort_values('tid', ascending=False), use_container_width=True)
        else:
            st.dataframe(df[befintliga_cols], use_container_width=True)
    else:
        st.info("Ingen data att visa.")
