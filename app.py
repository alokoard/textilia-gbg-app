import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime
import urllib.parse
import uuid

# --- KONFIGURATION (Wide mode för bättre överblick) ---
st.set_page_config(page_title="Textilia Gbg - Ultimate Control", layout="wide")

# --- INITIALISERING AV MINNE ---
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'rutten' not in st.session_state:
    st.session_state.rutten = []

# Hjälpfunktion för GPS i Göteborg
def hämta_gps(adress):
    try:
        geolocator = Nominatim(user_agent="textilia_ultimate_v14")
        loc = geolocator.geocode(adress + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except: return (None, None)

st.title("🚛 Textilia Gbg Logistik - Ultimate Control Tower")

tab1, tab2, tab3 = st.tabs(["🏗️ Chef: Fleet & Planering", "📍 Chaufför: Rutter", "🖥️ Chef: Live Dashboard"])

# ==========================================
# FLIK 1: CHEFENS KONTROLLRUM (Planering & Fleet)
# ==========================================
with tab1:
    pwd = st.sidebar.text_input("Ange Chefskod:", type="password")
    if pwd == "textilia2026":
        col_fleet, col_plan = st.columns([1, 2])
        
        with col_fleet:
            st.subheader("🚐 Hantera Fleet")
            with st.container(border=True):
                v_namn = st.text_input("Fordons-ID", placeholder="Ex: Bil 104")
                v_typ = st.selectbox("Fordonstyp", ["Singelbil", "Lastbil + Släp"])
                
                c1, c2 = st.columns(2)
                cap_bil = c1.number_input("Kapacitet Bil", value=70)
                cap_slap = c2.number_input("Kapacitet Släp", value=0) if v_typ == "Lastbil + Släp" else 0
                
                total_cap = cap_bil + cap_slap
                st.info(f"**Total kapacitet:** {total_cap} containers")
                
                if st.button("➕ Registrera Fordon"):
                    st.session_state.fleet.append({"namn": v_namn, "typ": v_typ, "cap": total_cap})
                    st.success(f"{v_namn} tillagd i fleet!")

        with col_plan:
            st.subheader("📍 Skapa Optimerad Rutt")
            with st.container(border=True):
                r_nr = st.number_input("Rutt Nummer (ID)", min_value=1, step=1)
                r_val_v = st.selectbox("Tilldela Fordon:", [f["namn"] for f in st.session_state.fleet] if st.session_state.fleet else ["Inga fordon"])
                
                addr = st.text_input("Adress")
                prio = st.number_input("Körordning / Prioritet (1 = Först)", min_value=1, value=1)
                info = st.text_area("Viktig info till chaufför (Portkod, instruktioner etc.)")
                
                if st.button("🚀 Lägg till & Spara i Rutt"):
                    lat, lon = hämta_gps(addr)
                    st.session_state.rutten.append({
                        "id": str(uuid.uuid4()), "rutt": r_nr, "fordon": r_val_v,
                        "adress": addr, "prio": prio, "info": info,
                        "status": "Väntar", "tid": None, "problem": False,
                        "lat": lat, "lon": lon
                    })
                    st.rerun()

        st.divider()
        st.subheader("📝 Justera Körordning (Prio)")
        if st.session_state.rutten:
            for i, stopp in enumerate(st.session_state.rutten):
                if stopp['status'] == "Väntar":
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.write(f"Rutt {stopp['rutt']} | {stopp['fordon']} | **{stopp['adress']}**")
                    stopp['prio'] = c2.number_input("Prio", 1, 100, stopp['prio'], key=f"prio_{stopp['id']}")
                    if c3.button("Ta bort", key=f"del_{stopp['id']}"):
                        st.session_state.rutten.pop(i)
                        st.rerun()
            
            if st.button("🔴 NOLLSTÄLL ALL DATA"):
                st.session_state.rutten = []
                st.rerun()
    else:
        st.warning("Logga in i sidomenyn för att använda kontrollrummet.")

# ==========================================
# FLIK 2: CHAUFFÖRSVY (Prio-sorterad & Smidig)
# ==========================================
with tab2:
    rutter_id = sorted(list(set([r['rutt'] for r in st.session_state.rutten])))
    if not rutter_id:
        st.info("Väntar på att rutter ska skapas av chefen...")
    else:
        val_r = st.selectbox("Välj din Rutt:", rutter_id)
        mina_stopp = [s for s in st.session_state.rutten if s['rutt'] == val_r and s['status'] == "Väntar"]
        # SORTERA EFTER PRIO
        mina_stopp.sort(key=lambda x: x['prio'])
        
        st.header(f"Körschema: Rutt {val_r}")
        for i, stopp in enumerate(mina_stopp):
            with st.expander(f"STÖPP {i+1} (Prio {stopp['prio']}): {stopp['adress']}", expanded=(i==0)):
                if stopp['info']:
                    st.warning(f"⚠️ **VIKTIG INFO:** {stopp['info']}")
                
                maps_url = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(stopp['adress'] + ', Göteborg')}"
                st.link_button("🧭 Öppna GPS / Navigering", maps_url)
                
                c1, c2 = st.columns(2)
                if c1.button("✅ MARKERA LEVERERAD", key=f"ok_{stopp['id']}", use_container_width=True):
                    stopp['status'] = "Levererad"
                    stopp['tid'] = datetime.now().strftime("%H:%M")
                    st.rerun()
                
                if c2.button("⚠️ RAPPORTERA PROBLEM", key=f"err_{stopp['id']}", use_container_width=True):
                    stopp['problem'] = True
                
                if stopp['problem']:
                    st.error("Ta en bild och beskriv felet:")
                    st.camera_input("Foto på hinder", key=f"cam_{stopp['id']}")
                    if st.button("Skicka felrapport", key=f"send_{stopp['id']}"):
                        stopp['status'] = "Problem"
                        stopp['tid'] = datetime.now().strftime("%H:%M")
                        st.rerun()

# ==========================================
# FLIK 3: LIVE DASHBOARD (Chefens överblick)
# ==========================================
with tab3:
    st.header("🖥️ Realtidsövervakning - Textilia Gbg")
    if st.session_state.rutten:
        df = pd.DataFrame(st.session_state.rutten)
        
        # Snabba siffror (Metrics)
        m1, m2, m3 = st.columns(3)
        m1.metric("Totalt antal stopp", len(df))
        m2.metric("Levererade", len(df[df['status'] == "Levererad"]))
        m3.metric("Problemrapporter", len(df[df['status'] == "Problem"]))
        
        st.divider()
        
        col_karta, col_logg = st.columns([1, 1])
        with col_karta:
            st.subheader("📍 Fleet Map")
            st.map(df.dropna(subset=['lat', 'lon']))
        
        with col_logg:
            st.subheader("📋 Leveransbevis & Checklista")
            for r_id in sorted(df['rutt'].unique()):
                st.write(f"**Rutt {r_id}:**")
                r_df = df[df['rutt'] == r_id]
                st.dataframe(r_df[['prio', 'adress', 'status', 'tid', 'info']], use_container_width=True, hide_index=True)
    else:
        st.info("Ingen aktivitet just nu.")
