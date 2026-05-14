import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
import urllib.parse
import uuid

# --- KONFIGURATION ---
# Sätter layout till wide för bättre överblick på stora skärmar
st.set_page_config(page_title="Textilia Gbg - Optimizer Pro", layout="wide")

if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'rutten' not in st.session_state:
    st.session_state.rutten = []
if 'depo' not in st.session_state:
    # Depån är fixerad till din bas i Göteborg
    st.session_state.depo = {"namn": "Depå Textilia", "lat": 57.7409, "lon": 12.0634}

# Geokodning för att hitta adresser i Göteborgsområdet
def hämta_gps(adress):
    try:
        geolocator = Nominatim(user_agent="textilia_optimizer_v15_2")
        loc = geolocator.geocode(adress + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

# --- OPTIMERINGS-ALGORITM (Här fixade vi NameError!) ---
def optimera_rutt(stopp_lista):
    if not stopp_lista: return []
    
    # 1. Prioritera adresser med Prio 1 (körs alltid först)
    prio_stopp = sorted([s for s in stopp_lista if s['prio'] == 1], key=lambda x: x['prio'])
    ovriga = [s for s in stopp_lista if s['prio'] > 1]
    
    # 2. Sortera övriga efter kortast avstånd (Nearest Neighbor)
    sorterad = prio_stopp
    nuvarande_pos = (st.session_state.depo['lat'], st.session_state.depo['lon'])
    
    if prio_stopp:
        sista_prio = prio_stopp[-1]
        if sista_prio['lat']: nuvarande_pos = (sista_prio['lat'], sista_prio['lon'])

    med_gps = [s for s in ovriga if s['lat'] is not None]
    utan_gps = [s for s in ovriga if s['lat'] is None]

    while med_gps:
        # Hittar närmsta stopp baserat på fågelvägen
        närmsta = min(med_gps, key=lambda s: geodesic(nuvarande_pos, (s['lat'], s['lon'])).km)
        sorterad.append(närmsta)
        # HÄR ÄR FIXEN: Stavningen av närmsta['lon'] är nu korrekt
        nuvarande_pos = (närmsta['lat'], närmsta['lon']) 
        med_gps.remove(närmsta)
    
    return sorterad + utan_gps

st.title("🚛 Textilia Gbg Logistik - Optimizer Pro v15.2")

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
                st.success(f"{v_id} registrerad med {cap_b + cap_s} vagnar totalt!")

        with col_p:
            st.subheader("🚀 Mass-import & Ruttoptimering")
            r_id = st.number_input("Skapa Rutt ID", 1, 100, 1)
            f_val = st.selectbox("Tilldela till:", [f['id'] for f in st.session_state.fleet] if st.session_state.fleet else ["Inga fordon"])
            
            mass_addr = st.text_area("Klistra in adresser (en per rad):", height=150)
            vagnar_per_stopp = st.number_input("Containers/Vagnar att hämta (snitt):", 1, 50, 10)
            
            if st.button("⚡ Optimera & Spara Rutt"):
                temp_stopp = []
                for rad in mass_addr.split("\n"):
                    if rad.strip():
                        lat, lon = hämta_gps(rad.strip())
                        temp_stopp.append({
                            "id": str(uuid.uuid4()), "rutt": r_id, "fordon": f_val,
                            "adress": rad.strip(), "prio": 2, "vagnar": vagnar_per_stopp,
                            "lat": lat, "lon": lon, "status": "Väntar", "info": ""
                        })
                # Beräknar den effektivaste vägen automatiskt
                optimerad = optimera_rutt(temp_stopp)
                st.session_state.rutten.extend(optimerad)
                st.success(f"Rutt {r_id} optimerad för {f_val}!")

        st.divider()
        if st.session_state.rutten:
            st.subheader("📝 Redigera Aktiva Stopp")
            for i, s in enumerate(st.session_state.rutten):
                if s['status'] == "Väntar":
                    col1, col2, col3 = st.columns([3, 1, 1])
                    col1.write(f"Rutt {s['rutt']} | **{s['adress']}** ({s['vagnar']} vagnar)")
                    s['prio'] = col2.number_input("Prio (1=Först)", 1, 2, s['prio'], key=f"p_{s['id']}")
                    if col3.button("Ta bort", key=f"d_{s['id']}"):
                        st.session_state.rutten.pop(i)
                        st.rerun()
            
            if st.button("🔴 NOLLSTÄLL ALL DATA"):
                st.session_state.rutten = []
                st.rerun()

# ==========================================
# FLIK 2: CHAUFFÖRSVY
# ==========================================
with tab2:
    rutter = sorted(list(set([r['rutt'] for r in st.session_state.rutten])))
    if rutter:
        val_r = st.selectbox("Välj din rutt för passet:", rutter)
        mina = [s for s in st.session_state.rutten if s['rutt'] == val_r and s['status'] == "Väntar"]
        
        st.header(f"Körschema: Rutt {val_r}")
        
        # Visar hur fylld lastbilen är baserat på hämtade vagnar
        f_info = next((f for f in st.session_state.fleet if f['id'] in [m['fordon'] for m in mina]), None)
        vagnar_i_last = sum([s['vagnar'] for s in st.session_state.rutten if s['rutt'] == val_r and s['status'] == "Levererad"])
        
        if f_info:
            st.metric("📦 Aktuell Last (Vagnar)", f"{vagnar_i_last} / {f_info['cap']}")
        
        for i, s in enumerate(mina):
            with st.expander(f"STOPP {i+1}: {s['adress']}", expanded=(i==0)):
                if s['prio'] == 1: st.warning("⭐ Högprioriterad leverans!")
                st.write(f"Väntad retur: **{s['vagnar']} containers**")
                
                # Snabbknapp för navigering
                st.link_button("🧭 Navigera", f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(s['adress'] + ', Göteborg')}")
                
                c1, c2 = st.columns(2)
                if c1.button("✅ Levererat & Hämtat", key=f"ok_{s['id']}"):
                    s['status'] = "Levererad"
                    s['tid'] = datetime.now().strftime("%H:%M")
                    st.rerun()
                if c2.button("⚠️ Problem", key=f"err_{s['id']}"):
                    st.camera_input("Foto på avvikelse (vid problem)", key=f"cam_{s['id']}")

# ==========================================
# FLIK 3: DASHBOARD (Driftöverblick)
# ==========================================
with tab3:
    st.header("🖥️ Dashboard - Textilia Gbg")
    if st.session_state.rutten:
        df = pd.DataFrame(st.session_state.rutten)
        # Realtidskarta över dagens rutter i Göteborg
        st.map(df.dropna(subset=['lat', 'lon']))
        st.subheader("Händelselogg")
        st.dataframe(df[['rutt', 'fordon', 'adress', 'status', 'tid', 'vagnar']].sort_values('tid', ascending=False), use_container_width=True)
    else:
        st.info("Ingen aktiv ruttdata att visa.")
