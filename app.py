import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
from datetime import datetime, time
import time as t_module

st.set_page_config(page_title="Textilia Logistik - Fleet Control", layout="wide")

# --- INITIALISERING ---
ARBETSPASS_START = time(6, 45)
ARBETSPASS_SLUT = time(15, 30)

if 'chaufforer' not in st.session_state:
    st.session_state.chaufforer = ["Chaufför 1", "Chaufför 2", "Chaufför 3"]
if 'uppdrag' not in st.session_state:
    st.session_state.uppdrag = []

# --- HJÄLPFUNKTIONER ---
def get_coords(adress):
    try:
        geolocator = Nominatim(user_agent="textilia_gbg")
        location = geolocator.geocode(adress + ", Göteborg")
        if location:
            return location.latitude, location.longitude
    except:
        return None, None
    return None, None

st.title("🚛 Textilia Gbg Logistik Control")

tab1, tab2, tab3 = st.tabs(["👑 Chefsvy (Kontroll)", "🚚 Chaufförsvy", "📊 Realtids-statistik"])

# ==========================================
# FLIK 1: CHEFSVY (Ruttplanering & Uppföljning)
# ==========================================
with tab1:
    st.header("Planera & Tilldela")
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        val_chauffor = st.selectbox("Välj chaufför för detta uppdrag:", st.session_state.chaufforer)
        adresser = st.text_area("Klistra in adresser (en per rad):", height=200)
        if st.button("Skicka ut rutt"):
            rader = adresser.split("\n")
            for i, rad in enumerate(rader):
                if rad.strip():
                    lat, lon = get_coords(rad.strip())
                    st.session_state.uppdrag.append({
                        "id": len(st.session_state.uppdrag) + 1,
                        "chauffor": val_chauffor,
                        "adress": rad.strip(),
                        "status": "Väntar",
                        "nr": i + 1,
                        "lat": lat, "lon": lon,
                        "klar_tid": None,
                        "start_tid": datetime.now().replace(hour=6, minute=45)
                    })
            st.success(f"Rutt tilldelad till {val_chauffor}!")
            st.rerun()

    with col_b:
        st.subheader("Aktiva rutter i Göteborg")
        df_all = pd.DataFrame(st.session_state.uppdrag)
        if not df_all.empty:
            # Numrerad karta med Pydeck
            map_data = df_all.dropna(subset=['lat', 'lon'])
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=pdk.ViewState(latitude=57.7088, longitude=11.9746, zoom=11, pitch=0),
                layers=[
                    pdk.Layer('ScatterplotLayer', data=map_data, get_position='[lon, lat]', get_color='[200, 30, 0, 160]', get_radius=200),
                    pdk.Layer('TextLayer', data=map_data, get_position='[lon, lat]', get_text='nr', get_size=20, get_color=[255, 255, 255], get_alignment_baseline="'center'")
                ]
            ))

# ==========================================
# FLIK 2: CHAUFFÖRSVY
# ==========================================
with tab2:
    min_chauffor = st.selectbox("Logga in som:", st.session_state.chaufforer, key="login")
    mina_stopp = [s for s in st.session_state.uppdrag if s['chauffor'] == min_chauffor and s['status'] == "Väntar"]
    
    if not mina_stopp:
        st.info("Inga fler stopp för idag!")
    else:
        st.subheader(f"Din rutt ({len(mina_stopp)} kvar)")
        for i, s in enumerate(mina_stopp):
            with st.expander(f"📍 {s['nr']}. {s['adress']}", expanded=(i==0)):
                if st.button("✅ Markera som Levererat", key=f"btn_{s['id']}"):
                    s['status'] = "Klar"
                    s['klar_tid'] = datetime.now()
                    st.success("Leverans sparad!")
                    st.rerun()

# ==========================================
# FLIK 3: DASHBOARD (Tid & Miljö)
# ==========================================
with tab3:
    st.header("Analys: Arbetstid & Effektivitet")
    if st.session_state.uppdrag:
        df_stats = pd.DataFrame(st.session_state.uppdrag)
        for c in st.session_state.chaufforer:
            c_data = df_stats[df_stats['chauffor'] == c]
            klara = c_data[c_data['status'] == "Klar"]
            
            st.subheader(f"📊 {c}")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Leveranser", f"{len(klara)}/{len(c_data)}")
            
            with col2:
                if not klara.empty:
                    # Beräkna genomsnittlig tid per stopp
                    total_tid = (klara['klar_tid'].max() - klara['start_tid'].min()).seconds / 60
                    snitt = total_tid / len(klara)
                    st.metric("Snittid per stopp", f"{int(snitt)} min")
                else:
                    st.metric("Snittid per stopp", "0 min")
            
            with col3:
                # Kolla om de är klara innan 15:30
                status_text = "I fas" if datetime.now().time() < ARBETSPASS_SLUT else "Övertid"
                st.metric("Status", status_text)
