import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import urllib.parse

# Grundinställningar
st.set_page_config(page_title="Textilia Gbg Pro", layout="wide")

# 1. Initiera minne (Session State)
if 'uppdrag' not in st.session_state:
    st.session_state.uppdrag = []
if 'chaufforer' not in st.session_state:
    st.session_state.chaufforer = ["Chaufför 1", "Chaufför 2"]

# Funktion för att hämta GPS-koordinater i Göteborg
def hämta_gps(adress):
    try:
        geolocator = Nominatim(user_agent="textilia_gbg_final_v8")
        loc = geolocator.geocode(adress + ", Göteborg, Sweden")
        return (loc.latitude, loc.longitude) if loc else (None, None)
    except:
        return None, None

st.title("🚚 Textilia Gbg Logistik - Pro v8.1")

tab1, tab2, tab3 = st.tabs(["👑 Chef: Planering", "📍 Chaufför: Leverans", "📊 Statistik & Analys"])

# ==========================================
# FLIK 1: CHEFSVY (Planering & Prioritering)
# ==========================================
with tab1:
    pwd = st.text_input("Chefskod:", type="password")
    if pwd == "textilia2026":
        col_v, col_h = st.columns([1, 2])
        
        with col_v:
            st.subheader("Personal & Fleet")
            ny_c = st.text_input("Namn på ny chaufför:")
            if st.button("Lägg till chaufför"):
                st.session_state.chaufforer.append(ny_c)
                st.rerun()
            
            if st.button("🔴 NOLLSTÄLL ALL DATA"):
                st.session_state.uppdrag = []
                st.rerun()

        with col_h:
            st.subheader("Ruttplanering")
            val_c = st.selectbox("Välj chaufför för rutt:", st.session_state.chaufforer)
            adresser = st.text_area("Klistra in adresser (en per rad):")
            
            if st.button("🚀 Skicka & Beräkna Rutt"):
                for rad in adresser.split("\n"):
                    if rad.strip():
                        lat, lon = hämta_gps(rad.strip())
                        # Skapa ett unikt ID baserat på tid + slump för att undvika dubbletter
                        u_id = f"{datetime.now().strftime('%f')}_{len(st.session_state.uppdrag)}"
                        st.session_state.uppdrag.append({
                            "id": u_id,
                            "vecka": datetime.now().strftime("%W"),
                            "dag": datetime.now().strftime("%Y-%m-%d"),
                            "chauffor": val_c,
                            "adress": rad.strip(),
                            "status": "Väntar",
                            "prio": 1,
                            "lat": lat, "lon": lon,
                            "klar_tid": None,
                            "tids_atgang": 0
                        })
                st.success("Adresser tillagda!")

        if st.session_state.uppdrag:
            st.divider()
            st.subheader("Hantera Prioritering")
            df_plan = pd.DataFrame(st.session_state.uppdrag)
            v_mask = df_plan['status'] == "Väntar"
            
            for i, row in df_plan[v_mask].iterrows():
                c1, c2 = st.columns([3, 1])
                c1.write(f"📍 {row['adress']} ({row['chauffor']})")
                # Vi använder row['id'] här också för att hålla reda på rätt rad
                st.session_state.uppdrag[i]['prio'] = c2.number_input(f"Prio för {i}", 1, 50, row['prio'], key=f"prio_input_{row['id']}")
            
            if st.button("🔄 Sortera Rutter efter Prioritet"):
                st.session_state.uppdrag.sort(key=lambda x: (x['chauffor'], x['prio']))
                st.success("Rutten är nu sorterad!")
                st.rerun()
    else:
        st.info("Logga in för att hantera fleet.")

# ==========================================
# FLIK 2: CHAUFFÖRSVY
# ==========================================
with tab2:
    inlogg = st.selectbox("Inloggad som:", st.session_state.chaufforer)
    mina = [u for u in st.session_state.uppdrag if u['chauffor'] == inlogg and u['status'] == "Väntar"]
    
    if not mina:
        st.success("Alla leveranser klara!")
    else:
        for i, u in enumerate(mina):
            with st.expander(f"ORDNING {u['prio']}: {u['adress']}", expanded=(i==0)):
                link = f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(u['adress'] + ', Göteborg')}"
                st.link_button("🗺️ Öppna i Google Maps", link)
                
                # FIX: Här använder vi u['id'] istället för adressen som nyckel
                if st.button("✅ MARKERA KLAR", key=f"k_{u['id']}"):
                    nu = datetime.now()
                    idag_klara = [x for x in st.session_state.uppdrag if x['chauffor'] == inlogg and x['status'] == "Levererad" and x['dag'] == u['dag']]
                    
                    if idag_klara:
                        sista_tid = datetime.strptime(idag_klara[-1]['klar_tid'], "%H:%M")
                        u['tids_atgang'] = (nu.hour*60 + nu.minute) - (sista_tid.hour*60 + sista_tid.minute)
                    else:
                        u['tids_atgang'] = (nu.hour*60 + nu.minute) - (6*60 + 45)
                    
                    u['status'] = "Levererad"
                    u['klar_tid'] = nu.strftime("%H:%M")
                    st.rerun()

# ==========================================
# FLIK 3: STATISTIK & KARTA
# ==========================================
with tab3:
    if st.session_state.uppdrag:
        df_stat = pd.DataFrame(st.session_state.uppdrag)
        st.subheader("Ruttkarta Göteborg")
        map_points = df_stat.dropna(subset=['lat', 'lon'])
        if not map_points.empty:
            st.map(map_points[['lat', 'lon']])
        
        st.divider()
        klara_df = df_stat[df_stat['status'] == "Levererad"]
        if not klara_df.empty:
            st.subheader("Veckoanalys (Tidsåtgång)")
            st.bar_chart(klara_df.set_index('adress')['tids_atgang'])
