import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime, timedelta
import urllib.parse
import uuid

# --- KONFIGURATION ---
st.set_page_config(page_title="Textilia Gbg - Den Kompletta Appen", layout="wide")

# --- SVENSK TID FUNKTION ---
def svensk_tid():
    # Streamlit Cloud kör ofta på UTC. Vi lägger på 2 timmar för svensk sommartid (Maj).
    return (datetime.utcnow() + timedelta(hours=2)).strftime("%H:%M")

if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'rutten' not in st.session_state:
    st.session_state.rutten = []
if 'depo' not in st.session_state:
    st.session_state.depo = {"namn": "Depå Textilia", "lat": 57.7409, "lon": 12.0634}

def hämta_gps(adress):
    try:
        geolocator = Nominatim(user_agent="textilia_gbg_v16")
        loc = geolocator.geocode(adress + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

# --- OPTIMERINGS-MOTOR ---
def optimera_rutt(stopp_lista):
    if not stopp_lista: return []
    # Sortera först på Prio (1 är högst), sen på avstånd
    prio_1 = sorted([s for s in stopp_lista if s.get('prio') == 1], key=lambda x: x.get('id'))
    ovriga = [s for s in stopp_lista if s.get('prio', 2) > 1]
    
    sorterad = prio_1
    nuvarande_pos = (st.session_state.depo['lat'], st.session_state.depo['lon'])
    
    if prio_1:
        sista = prio_1[-1]
        if sista.get('lat'): nuvarande_pos = (sista['lat'], sista['lon'])

    med_gps = [s for s in ovriga if s.get('lat') is not None]
    utan_gps = [s for s in ovriga if s.get('lat') is None]

    while med_gps:
        närmsta = min(med_gps, key=lambda s: geodesic(nuvarande_pos, (s['lat'], s['lon'])).km)
        sorterad.append(närmsta)
        nuvarande_pos = (närmsta['lat'], närmsta['lon'])
        med_gps.remove(närmsta)
    
    return sorterad + utan_gps

st.title("🚛 Textilia Gbg Logistik v16.0")

tab1, tab2, tab3 = st.tabs(["🏗️ Chef: Planera & Fleet", "📍 Chaufför: Körning", "🖥️ Chef: Live Dashboard"])

# ==========================================
# FLIK 1: CHEFENS PLANERING (Inget borttaget!)
# ==========================================
with tab1:
    pwd = st.sidebar.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        col_f, col_p = st.columns([1, 2])
        
        with col_f:
            st.subheader("🚐 Hantera Fleet")
            v_id = st.text_input("Fordons-ID (Ex: Bil 104)")
            v_typ = st.selectbox("Typ", ["Singel", "Lastbil + Släp"])
            c1, c2 = st.columns(2)
            cap_b = c1.number_input("Kapacitet Bil", 1, 200, 70)
            cap_s = c2.number_input("Kapacitet Släp", 0, 200, 30) if v_typ == "Lastbil + Släp" else 0
            if st.button("➕ Registrera Fordon"):
                st.session_state.fleet.append({"id": v_id, "cap": cap_b + cap_s, "typ": v_typ})
                st.success(f"{v_id} registrerad (Totalt {cap_b + cap_s} vagnar)")

        with col_p:
            st.subheader("🚀 Mass-import & Optimering")
            r_id = st.number_input("Rutt ID", 1, 100, 1)
            f_val = st.selectbox("Tilldela till:", [f['id'] for f in st.session_state.fleet] if st.session_state.fleet else ["Inga fordon"])
            
            mass_addr = st.text_area("Klistra in adresser (en per rad):", height=120)
            v_retur = st.number_input("Vagnar att hämta per stopp:", 1, 100, 10)
            
            if st.button("⚡ Optimera & Spara Rutt"):
                temp_stopp = []
                for rad in mass_addr.split("\n"):
                    if rad.strip():
                        lat, lon = hämta_gps(rad.strip())
                        temp_stopp.append({
                            "id": str(uuid.uuid4()), "rutt": r_id, "fordon": f_val,
                            "adress": rad.strip(), "prio": 2, "vagnar": v_retur,
                            "lat": lat, "lon": lon, "status": "Väntar", "tid": None,
                            "info": "", "problem": False
                        })
                st.session_state.rutten.extend(optimera_rutt(temp_stopp))
                st.success(f"Rutt {r_id} sparad!")

        st.divider()
        if st.session_state.rutten:
            st.subheader("📝 Detaljerad planering (Viktig Info & Prio)")
            for s in st.session_state.rutten:
                if s['status'] == "Väntar":
                    with st.expander(f"Redigera: {s['adress']} (Rutt {s['rutt']})"):
                        s['info'] = st.text_area("Viktig info till chaufför:", s['info'], key=f"info_{s['id']}")
                        s['prio'] = st.selectbox("Prioritet", [1, 2], index=(s['prio']-1), key=f"prio_{s['id']}")
            
            if st.button("🔴 NOLLSTÄLL ALL DATA"):
                st.session_state.rutten = []
                st.rerun()

# ==========================================
# FLIK 2: CHAUFFÖRSVY (Med Info & Problem)
# ==========================================
with tab2:
    rutter = sorted(list(set([r.get('rutt') for r in st.session_state.rutten if r.get('rutt')])))
    if rutter:
        val_r = st.selectbox("Välj din rutt:", rutter)
        mina = [s for s in st.session_state.rutten if s.get('rutt') == val_r and s.get('status') == "Väntar"]
        
        st.header(f"Körschema: Rutt {val_r}")
        
        for i, s in enumerate(mina):
            with st.expander(f"STOPP {i+1}: {s['adress']}", expanded=(i==0)):
                # VISA VIKTIG INFO
                if s.get('info'):
                    st.warning(f"⚠️ **INFO:** {s['info']}")
                
                st.write(f"Hämta: **{s.get('vagnar', 0)} vagnar**")
                st.link_button("🧭 Öppna GPS", f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(s['adress'] + ', Göteborg')}")
                
                col1, col2 = st.columns(2)
                if col1.button("✅ Levererat & Hämtat", key=f"ok_{s['id']}"):
                    s['status'] = "Levererad"
                    s['tid'] = svensk_tid()
                    st.rerun()
                
                if col2.button("⚠️ Rapportera Problem", key=f"err_{s['id']}"):
                    s['problem'] = True
                
                if s.get('problem'):
                    st.error("Dokumentera problemet:")
                    st.camera_input("Ta bild på hinder/skada", key=f"cam_{s['id']}")
                    if st.button("Skicka Felrapport", key=f"f_{s['id']}"):
                        s['status'] = "Problem"
                        s['tid'] = svensk_tid()
                        st.rerun()
    else:
        st.info("Inga rutter inlagda än.")

# ==========================================
# FLIK 3: DASHBOARD
# ==========================================
with tab3:
    st.header("🖥️ Dashboard - Live status")
    if st.session_state.rutten:
        df = pd.DataFrame(st.session_state.rutten)
        st.map(df.dropna(subset=['lat', 'lon']))
        st.subheader("Händelselogg (Svensk tid)")
        # Säkra kolumner
        cols = ['rutt', 'fordon', 'adress', 'status', 'tid', 'info']
        st.dataframe(df[[c for c in cols if c in df.columns]], use_container_width=True)
    else:
        st.info("Ingen data att visa.")
